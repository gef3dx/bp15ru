"""Request storage, basic abuse protection and optional email notifications."""
import hashlib
import ipaddress
import json
import logging
import time
from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.crypto import salted_hmac

from .constants import CONSENT_TEXT
from .models import Inquiry, SubmissionRateBucket

logger = logging.getLogger(__name__)

class RateLimitExceeded(Exception):
    pass

class SubmissionConflict(Exception):
    pass

def client_address(request) -> str:
    raw = request.META.get("REMOTE_ADDR", "")
    if settings.TRUST_PROXY_HEADERS:
        raw = request.META.get("HTTP_X_REAL_IP", raw)
    try:
        return str(ipaddress.ip_address(raw))
    except ValueError:
        return "unknown"

def take_rate_slot(request) -> None:
    window = settings.INQUIRY_RATE_WINDOW_SECONDS
    bucket = int(time.time()) // window
    key = salted_hmac("buro.rate", f"{client_address(request)}|{bucket}", algorithm="sha256").hexdigest()
    expiry = datetime.fromtimestamp((bucket + 1) * window, tz=dt_timezone.utc)
    with transaction.atomic():
        SubmissionRateBucket.objects.get_or_create(key=key, defaults={"expires_at": expiry})
        updated = SubmissionRateBucket.objects.filter(key=key, count__lt=settings.INQUIRY_RATE_LIMIT).update(count=F("count") + 1)
        if not updated:
            raise RateLimitExceeded

def save_inquiry(cleaned_data: dict) -> tuple[Inquiry, bool]:
    data = {k: cleaned_data.get(k) for k in (
        "form_name", "name", "phone", "email", "format", "dates", "guests", "comment", "source_page", "program", "consent")}
    payload_hash = hashlib.sha256(json.dumps(data, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    key = salted_hmac("buro.submission", cleaned_data["submission_token"] + "|" + data["form_name"], algorithm="sha256").hexdigest()
    data.update(payload_hash=payload_hash, consent_text=CONSENT_TEXT,
                email_status=Inquiry.EmailStatus.PENDING if settings.INQUIRY_EMAIL_ENABLED else Inquiry.EmailStatus.DISABLED)
    item, created = Inquiry.objects.get_or_create(submission_key=key, defaults=data)
    if not created and item.payload_hash != payload_hash:
        raise SubmissionConflict
    return item, created

def notify_inquiry(pk: int) -> bool:
    """False means not sent; the saved inquiry remains available in admin.

    SMTP acceptance is not a guarantee of inbox delivery. The transaction prevents
    concurrent retry workers from normally sending the same notification twice.
    """
    if not settings.INQUIRY_EMAIL_ENABLED:
        return False
    with transaction.atomic():
        item = Inquiry.objects.select_for_update().get(pk=pk)
        if item.email_status == Inquiry.EmailStatus.SENT:
            return True
        body = "\n".join([
            f"Заявка №{item.pk}", f"Форма: {item.form_name}",
            f"Имя: {item.name}", f"Телефон: {item.phone}", f"E-mail: {item.email or '—'}",
            f"Формат: {item.format}", f"Даты: {item.dates or '—'}",
            f"Количество человек: {item.guests or '—'}", f"Программа: {item.program or '—'}",
            f"Страница: {item.source_page}", "", "Комментарий:", item.comment,
            "", f"Согласие: {item.consent_text}",
        ])
        try:
            sent = EmailMessage(
                subject=f"БЮРО путешествий — новая заявка №{item.pk}", body=body,
                from_email=settings.DEFAULT_FROM_EMAIL, to=settings.INQUIRY_RECIPIENTS,
                reply_to=[item.email] if item.email else [],
            ).send(fail_silently=False)
            if sent != 1:
                raise RuntimeError("SMTP did not accept the message")
        except Exception:
            # Avoid including form contents or SMTP credentials in application logs.
            item.email_status = Inquiry.EmailStatus.FAILED
            item.save(update_fields=["email_status"])
            logger.error("Email notification failed for inquiry %s; request is saved.", item.pk)
            return False
        item.email_status = Inquiry.EmailStatus.SENT
        item.email_sent_at = timezone.now()
        item.save(update_fields=["email_status", "email_sent_at"])
        return True
