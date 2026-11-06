import logging
from django.conf import settings
from django.core.exceptions import RequestDataTooBig, TooManyFieldsSent
from django.db import DatabaseError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from .constants import PAGE_PATHS
from .forms import InquiryForm
from .services import RateLimitExceeded, SubmissionConflict, notify_inquiry, save_inquiry, take_rate_slot

logger = logging.getLogger(__name__)

def wants_json(request):
    return "application/json" in request.headers.get("Accept", "")

@require_http_methods(["GET", "HEAD"])
@never_cache
def page(request, page_name="home"):
    return render(request, f"website/pages/{page_name}.html", {
        "page_name": page_name, "source_page": request.path,
        "modal_number": 2 if page_name == "contacts" else 1,
    })

@require_http_methods(["GET", "HEAD"])
@never_cache
def success(request):
    return render(request, "website/success.html")

def error_response(request, message, *, status=400, form=None):
    if wants_json(request):
        errors = {}
        if form is not None:
            errors = {name: [str(message) for message in messages] for name, messages in form.errors.items()}
        return JsonResponse({"ok": False, "message": message, "errors": errors}, status=status)
    return render(request, "website/form_error.html", {"error_message": message, "form": form}, status=status)

@require_POST
@never_cache
def inquiry_submit(request):
    try:
        if request.content_type not in {"application/x-www-form-urlencoded", "multipart/form-data"}:
            return error_response(request, "Неподдерживаемый формат запроса.", status=415)
        try:
            content_length = int(request.META.get("CONTENT_LENGTH") or "0")
        except ValueError:
            return error_response(request, "Некорректный размер запроса.")
        if content_length > settings.DATA_UPLOAD_MAX_MEMORY_SIZE:
            return error_response(request, "Слишком большой запрос.", status=413)
        raw = request.POST.copy()
        if request.FILES:
            return error_response(request, "Загрузка файлов этой формой не предусмотрена.")
        # Existing public field names are retained for compatibility with the source HTML.
        for old, new in {"form-name": "form_name", "source-page": "source_page", "bot-field": "bot_field", "submission-token": "submission_token"}.items():
            if old in raw:
                raw[new] = raw[old]
        form = InquiryForm(raw)
        take_rate_slot(request)
        if not form.is_valid():
            return error_response(request, "Проверьте поля формы. Введённые данные сохранены.", form=form)
        item, created = save_inquiry(form.cleaned_data)
    except (RequestDataTooBig, TooManyFieldsSent):
        return error_response(request, "Слишком большой запрос.", status=413)
    except RateLimitExceeded:
        response = error_response(request, "Слишком много запросов. Попробуйте позже или позвоните: +7 (928) 938-40-04.", status=429)
        response["Retry-After"] = str(settings.INQUIRY_RATE_WINDOW_SECONDS)
        return response
    except SubmissionConflict:
        return error_response(request, "Эта форма уже отправлена с другими данными. Обновите страницу для нового запроса.", status=409)
    except DatabaseError:
        logger.error("Inquiry database operation failed.")
        return error_response(request, "Не удалось сохранить запрос. Попробуйте ещё раз или позвоните: +7 (928) 938-40-04.", status=503)
    if created:
        try:
            notify_inquiry(item.pk)
        except DatabaseError:
            # The inquiry is already committed. The retry command can notify later.
            logger.error("Email status database update failed for inquiry %s.", item.pk)
    if wants_json(request):
        return JsonResponse({"ok": True, "redirect_url": reverse("website:success")}, status=201 if created else 200)
    return redirect("website:success")

@require_GET
def robots(request):
    text = "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /inquiries/\nDisallow: /success.html\nSitemap: " + settings.SITE_URL + "/sitemap.xml\n"
    return HttpResponse(text, content_type="text/plain; charset=utf-8")

@require_GET
def sitemap(request):
    return render(request, "website/sitemap.xml", {"paths": PAGE_PATHS, "site_url": settings.SITE_URL}, content_type="application/xml")

def not_found(request, exception=None):
    return render(request, "404.html", status=404)

def bad_request(request, exception=None):
    return error_response(request, "Не удалось обработать запрос.", status=400)

def permission_denied(request, exception=None):
    return error_response(request, "Доступ запрещён.", status=403)

def csrf_failure(request, reason=""):
    return error_response(request, "Срок действия формы истёк или проверка безопасности не пройдена. Обновите страницу и попробуйте ещё раз.", status=403)

def server_error(request):
    return render(request, "500.html", status=500)
