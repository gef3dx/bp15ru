from django.db import models

class Inquiry(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        CLOSED = "closed", "Завершена"
        SPAM = "spam", "Спам"

    class EmailStatus(models.TextChoices):
        DISABLED = "disabled", "Уведомления отключены"
        PENDING = "pending", "Ожидает отправки"
        SENT = "sent", "Передано почтовому серверу"
        FAILED = "failed", "Ошибка отправки"

    created_at = models.DateTimeField("Получена", auto_now_add=True, db_index=True)
    form_name = models.CharField("Форма", max_length=30)
    name = models.CharField("Имя", max_length=120)
    phone = models.CharField("Телефон", max_length=32)
    email = models.EmailField("E-mail", blank=True)
    format = models.CharField("Формат поездки", max_length=80, blank=True)
    dates = models.CharField("Даты", max_length=120, blank=True)
    guests = models.PositiveIntegerField("Количество человек", null=True, blank=True)
    comment = models.TextField("Комментарий", blank=True, max_length=4000)
    source_page = models.CharField("Страница", max_length=80)
    program = models.CharField("Программа / контекст", max_length=250, blank=True)
    consent = models.BooleanField("Согласие на обработку запроса")
    consent_text = models.CharField("Текст согласия", max_length=300)
    submission_key = models.CharField(max_length=64, unique=True, editable=False)
    payload_hash = models.CharField(max_length=64, editable=False)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)
    notes = models.TextField("Внутренние заметки", blank=True)
    email_status = models.CharField("Уведомление", max_length=16, choices=EmailStatus.choices, default=EmailStatus.DISABLED)
    email_sent_at = models.DateTimeField("Передано SMTP", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"

    def __str__(self):
        return f"№{self.pk} — {self.name}"

class SubmissionRateBucket(models.Model):
    # No raw IP address is stored; the key is an HMAC of IP + time window.
    key = models.CharField(max_length=64, primary_key=True)
    count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(db_index=True)
