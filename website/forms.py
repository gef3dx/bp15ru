import re
import uuid
from django import forms
from django.core import signing
from .constants import CONTACT_FORMATS, FORM_NAMES, PAGE_PATHS, TOKEN_MAX_AGE, TOKEN_SALT, TRIP_FORMATS

class InquiryForm(forms.Form):
    form_name = forms.ChoiceField(choices=[(v, v) for v in FORM_NAMES], widget=forms.HiddenInput)
    source_page = forms.ChoiceField(choices=[(v, v) for v in PAGE_PATHS], widget=forms.HiddenInput)
    submission_token = forms.CharField(max_length=300, widget=forms.HiddenInput)
    bot_field = forms.CharField(required=False, max_length=300, widget=forms.HiddenInput)
    program = forms.CharField(required=False, max_length=250, widget=forms.HiddenInput)
    name = forms.CharField(label="Имя", max_length=120, widget=forms.TextInput(attrs={"autocomplete": "name"}))
    phone = forms.CharField(label="Телефон", max_length=32, widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}))
    email = forms.EmailField(label="E-mail", max_length=254, required=False)
    format = forms.ChoiceField(label="Формат", choices=[(v, v) for v in dict.fromkeys(TRIP_FORMATS + CONTACT_FORMATS)])
    dates = forms.CharField(label="Даты", max_length=120, required=False)
    guests = forms.IntegerField(label="Количество человек", min_value=1, max_value=10000, required=False)
    comment = forms.CharField(label="Комментарий", max_length=4000, required=False, widget=forms.Textarea)
    consent = forms.BooleanField(label="Согласен(на) на обработку данных для ответа на запрос.", required=True)

    def clean_phone(self):
        value = self.cleaned_data["phone"].strip()
        digits = re.sub(r"[^0-9]", "", value)
        if not re.fullmatch(r"[+0-9().\s-]+", value) or not 7 <= len(digits) <= 15:
            raise forms.ValidationError("Укажите телефон с кодом города или страны (7–15 цифр).")
        return value

    def clean_name(self):
        value = self.cleaned_data["name"].strip()
        if not value or any(ord(c) < 32 for c in value):
            raise forms.ValidationError("Укажите Ваше имя.")
        return value

    def clean_submission_token(self):
        token = self.cleaned_data["submission_token"]
        try:
            uuid.UUID(signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE))
        except (signing.BadSignature, ValueError, TypeError, AttributeError):
            raise forms.ValidationError("Срок действия формы истёк. Обновите страницу и отправьте запрос снова.")
        return token

    def clean_bot_field(self):
        if self.cleaned_data.get("bot_field"):
            raise forms.ValidationError("Не удалось отправить запрос.")
        return ""

    def clean_consent(self):
        value = self.cleaned_data["consent"]
        if self.data.get("consent") not in {"yes", "on", "true", True}:
            raise forms.ValidationError("Подтвердите согласие на обработку запроса.")
        return value

    def clean(self):
        data = super().clean()
        allowed = CONTACT_FORMATS if data.get("form_name") == "contact-request" else TRIP_FORMATS
        if data.get("format") and data["format"] not in allowed:
            self.add_error("format", "Выберите формат из списка.")
        return data
