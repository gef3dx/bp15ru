from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Inquiry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True, verbose_name="Получена")),
                ("form_name", models.CharField(max_length=30, verbose_name="Форма")),
                ("name", models.CharField(max_length=120, verbose_name="Имя")),
                ("phone", models.CharField(max_length=32, verbose_name="Телефон")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="E-mail")),
                ("format", models.CharField(blank=True, max_length=80, verbose_name="Формат поездки")),
                ("dates", models.CharField(blank=True, max_length=120, verbose_name="Даты")),
                ("guests", models.PositiveIntegerField(blank=True, null=True, verbose_name="Количество человек")),
                ("comment", models.TextField(blank=True, max_length=4000, verbose_name="Комментарий")),
                ("source_page", models.CharField(max_length=80, verbose_name="Страница")),
                ("program", models.CharField(blank=True, max_length=250, verbose_name="Программа / контекст")),
                ("consent", models.BooleanField(verbose_name="Согласие на обработку запроса")),
                ("consent_text", models.CharField(max_length=300, verbose_name="Текст согласия")),
                ("submission_key", models.CharField(editable=False, max_length=64, unique=True)),
                ("payload_hash", models.CharField(editable=False, max_length=64)),
                ("status", models.CharField(choices=[("new", "Новая"), ("in_progress", "В работе"), ("closed", "Завершена"), ("spam", "Спам")], default="new", max_length=20, verbose_name="Статус")),
                ("notes", models.TextField(blank=True, verbose_name="Внутренние заметки")),
                ("email_status", models.CharField(choices=[("disabled", "Уведомления отключены"), ("pending", "Ожидает отправки"), ("sent", "Передано почтовому серверу"), ("failed", "Ошибка отправки")], default="disabled", max_length=16, verbose_name="Уведомление")),
                ("email_sent_at", models.DateTimeField(blank=True, null=True, verbose_name="Передано SMTP")),
            ],
            options={"verbose_name": "Заявка", "verbose_name_plural": "Заявки", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="SubmissionRateBucket",
            fields=[
                ("key", models.CharField(max_length=64, primary_key=True, serialize=False)),
                ("count", models.PositiveIntegerField(default=0)),
                ("expires_at", models.DateTimeField(db_index=True)),
            ],
        ),
    ]
