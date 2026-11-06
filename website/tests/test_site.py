import json
import re
import uuid
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail, signing
from django.test import Client, SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from website.constants import PAGE_PATHS, TOKEN_SALT
from website.forms import InquiryForm
from website.models import Inquiry, SubmissionRateBucket
from website.services import notify_inquiry

class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}: self.skip += 1
    def handle_endtag(self, tag):
        if tag in {"script", "style"}: self.skip = max(0, self.skip - 1)
    def handle_data(self, data):
        if not self.skip and data.strip(): self.parts.append(data.strip())

def norm(text):
    return " ".join(text.split())

def token():
    return signing.dumps(str(uuid.uuid4()), salt=TOKEN_SALT)

def payload(**changes):
    data = {"form-name": "trip-request", "source-page": "/", "submission-token": token(),
            "bot-field": "", "name": "Тестовый посетитель", "phone": "+7 (900) 000-00-00",
            "email": "visitor@example.test", "format": "Индивидуальная поездка", "dates": "12–15 сентября",
            "guests": "3", "comment": "Тестовая заявка, без отправки реальной почты.", "program": "", "consent": "yes"}
    data.update(changes);return data

class PagesTests(SimpleTestCase):
    def test_all_pages_and_original_texts(self):
        originals = json.loads((settings.BASE_DIR / "docs/original_page_texts.json").read_text(encoding="utf-8"))
        for path in PAGE_PATHS:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                html = response.content.decode()
                self.assertNotIn("data-netlify", html)
                self.assertIn('name="csrfmiddlewaretoken"', html)
                parser = TextParser(); parser.feed(html)
                name = "home" if path == "/" else path.strip("/")
                self.assertEqual(norm(" ".join(parser.parts)), norm(originals[name]))
                self.assertIn("no-store", response.headers.get("Cache-Control", ""))

    def test_legacy_and_slash_redirects(self):
        for path in PAGE_PATHS:
            legacy = path + "index.html"
            self.assertRedirects(self.client.get(legacy), path, status_code=301)
        self.assertRedirects(self.client.get("/bureau"), "/bureau/", status_code=301)

    def test_sitemap(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        for path in PAGE_PATHS:
            self.assertContains(response, "https://example.test" + path)
        self.assertContains(self.client.get("/robots.txt"), "Disallow: /admin/")

    @override_settings(DEBUG=False)
    def test_original_404(self):
        response = self.client.get("/missing-page/")
        self.assertContains(response, "Здесь нет маршрута.", status_code=404)

    def test_success_page(self):
        self.assertContains(self.client.get("/success.html"), "Спасибо.")

    def test_submit_get_not_allowed(self):
        self.assertEqual(self.client.get(reverse("website:inquiry_submit")).status_code, 405)

class InquiryTests(TestCase):
    def post(self, data=None, **kwargs):
        return self.client.post(reverse("website:inquiry_submit"), payload() if data is None else data, HTTP_ACCEPT="application/json", **kwargs)

    def test_save_trip(self):
        response = self.post()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["ok"])
        self.assertEqual(response.json()["redirect_url"], "/success.html")
        item = Inquiry.objects.get()
        self.assertEqual(item.name, "Тестовый посетитель")
        self.assertEqual(item.guests, 3)
        self.assertTrue(item.consent)
        self.assertEqual(item.email_status, "disabled")

    def test_contact_form(self):
        response = self.post(payload(**{"form-name": "contact-request", "source-page": "/contacts/", "format": "Частная поездка"}))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Inquiry.objects.get().form_name, "contact-request")

    def test_empty_optional_fields(self):
        self.assertEqual(self.post(payload(email="", dates="", guests="", comment="")).status_code, 201)
        self.assertIsNone(Inquiry.objects.get().guests)

    def test_validation(self):
        bad = [{"name": "   "}, {"phone": "abc"}, {"email": "invalid"}, {"guests": "0"},
               {"guests": "1.5"}, {"consent": "false"}, {"comment": "a" * 4001},
               {"format": "unknown"}, {"source-page": "https://untrusted.example/"}, {"form-name": "unknown"}]
        for changes in bad:
            with self.subTest(changes=list(changes)):
                self.assertEqual(self.post(payload(**changes)).status_code, 400)
        self.assertFalse(Inquiry.objects.exists())

    def test_honeypot(self):
        self.assertEqual(self.post(payload(**{"bot-field": "filled"})).status_code, 400)
        self.assertFalse(Inquiry.objects.exists())

    def test_invalid_token(self):
        self.assertEqual(self.post(payload(**{"submission-token": "tampered"})).status_code, 400)
        self.assertFalse(Inquiry.objects.exists())

    def test_expired_token(self):
        with patch("django.core.signing.time.time", return_value=1):
            expired = token()
        self.assertEqual(self.post(payload(**{"submission-token": expired})).status_code, 400)

    def test_idempotent_retry(self):
        data = payload()
        self.assertEqual(self.post(data).status_code, 201)
        self.assertEqual(self.post(data).status_code, 200)
        self.assertEqual(Inquiry.objects.count(), 1)

    def test_reused_token_changed_payload(self):
        data = payload(); self.post(data); data["name"] = "Другое имя"
        self.assertEqual(self.post(data).status_code, 409)
        self.assertEqual(Inquiry.objects.count(), 1)

    @override_settings(INQUIRY_RATE_LIMIT=2)
    def test_rate_limit(self):
        self.assertEqual(self.post().status_code, 201)
        self.assertEqual(self.post().status_code, 201)
        limited = self.post()
        self.assertEqual(limited.status_code, 429)
        self.assertIn("Retry-After", limited.headers)
        self.assertEqual(Inquiry.objects.count(), 2)

    def test_no_javascript_success(self):
        response = self.client.post(reverse("website:inquiry_submit"), payload())
        self.assertRedirects(response, "/success.html")

    def test_no_javascript_invalid_preserves_values(self):
        response = self.client.post(reverse("website:inquiry_submit"), payload(email="bad-email"))
        self.assertContains(response, "bad-email", status_code=400)
        self.assertContains(response, "Тестовый посетитель", status_code=400)

    def test_csrf_required(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(reverse("website:inquiry_submit"), payload(), HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Inquiry.objects.exists())

    def test_csrf_valid(self):
        client = Client(enforce_csrf_checks=True)
        html = client.get("/").content.decode()
        csrf = unescape(re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', html).group(1))
        data = payload();data["csrfmiddlewaretoken"] = csrf
        response = client.post(reverse("website:inquiry_submit"), data, HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 201)

    def test_database_error_does_not_report_success(self):
        from django.db import DatabaseError
        with patch("website.views.save_inquiry", side_effect=DatabaseError):
            response = self.post()
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json()["ok"])

    def test_payload_type_rejected(self):
        response = self.client.post(reverse("website:inquiry_submit"), "{}", content_type="application/json", HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 415)

    def test_large_payload_rejected(self):
        response = self.client.post(reverse("website:inquiry_submit"), "comment=" + "a" * 70000, content_type="application/x-www-form-urlencoded", HTTP_ACCEPT="application/json")
        self.assertEqual(response.status_code, 413)

    def test_anonymous_admin_redirect(self):
        self.assertEqual(self.client.get("/admin/").status_code, 302)

    def test_admin_inquiries(self):
        self.post()
        user = get_user_model().objects.create_superuser(username="admin-test", email="admin@example.test", password="test-only")
        self.client.force_login(user)
        self.assertContains(self.client.get("/admin/website/inquiry/"), "Тестовый посетитель")

    @override_settings(INQUIRY_EMAIL_ENABLED=True, INQUIRY_RECIPIENTS=["owner@example.test"], DEFAULT_FROM_EMAIL="site@example.test")
    def test_notification_uses_test_backend(self):
        data = payload(); self.assertEqual(self.post(data).status_code, 201)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["owner@example.test"])
        self.assertEqual(mail.outbox[0].reply_to, ["visitor@example.test"])
        self.assertEqual(Inquiry.objects.get().email_status, "sent")
        self.post(data)
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(INQUIRY_EMAIL_ENABLED=True, INQUIRY_RECIPIENTS=["owner@example.test"], DEFAULT_FROM_EMAIL="site@example.test")
    def test_smtp_failure_keeps_inquiry_and_can_retry(self):
        with patch("website.services.EmailMessage.send", side_effect=OSError("test")):
            self.assertEqual(self.post().status_code, 201)
        item = Inquiry.objects.get(); self.assertEqual(item.email_status, "failed")
        self.assertTrue(notify_inquiry(item.pk))
        item.refresh_from_db(); self.assertEqual(item.email_status, "sent")
        self.assertEqual(len(mail.outbox), 1)
