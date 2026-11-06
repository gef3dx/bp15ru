from django.contrib import admin, messages
from .models import Inquiry
from .services import notify_inquiry

admin.site.site_header = "БЮРО путешествий — заявки"
admin.site.site_title = "БЮРО путешествий"
admin.site.index_title = "Управление заявками"

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "name", "phone", "format", "status", "email_status")
    list_filter = ("status", "form_name", "email_status", "created_at")
    search_fields = ("name", "phone", "email", "program", "comment")
    date_hierarchy = "created_at"
    list_per_page = 30
    readonly_fields = ("created_at", "form_name", "name", "phone", "email", "format", "dates", "guests", "comment", "source_page", "program", "consent", "consent_text", "email_status", "email_sent_at")
    fields = readonly_fields + ("status", "notes")
    actions = ["retry_notifications"]

    def has_add_permission(self, request):
        return False

    @admin.action(description="Повторить неотправленные уведомления", permissions=["change"])
    def retry_notifications(self, request, queryset):
        sent = 0
        for item in queryset.exclude(email_status=Inquiry.EmailStatus.SENT):
            sent += int(notify_inquiry(item.pk))
        self.message_user(request, f"Передано почтовому серверу: {sent}. Статус остальных заявок сохранён.", messages.INFO)
