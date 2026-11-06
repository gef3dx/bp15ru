"""Isolated tests: no production database, no network email, no real credentials."""
import os
os.environ["DJANGO_DEBUG"] = "true"
os.environ["DJANGO_SECRET_KEY"] = "test-only-not-for-deployment-" + "x" * 60
os.environ["DJANGO_ALLOWED_HOSTS"] = "testserver,localhost,127.0.0.1"
os.environ["DJANGO_SECURE_SSL_REDIRECT"] = "false"
os.environ["DJANGO_TRUST_PROXY_HEADERS"] = "false"
os.environ["INQUIRY_EMAIL_ENABLED"] = "false"
os.environ["DB_ENGINE"] = "sqlite"
os.environ["EMAIL_USE_SSL"] = "false"
os.environ["EMAIL_USE_TLS"] = "true"
os.environ["EMAIL_PORT"] = "587"
os.environ["SITE_URL"] = "https://example.test"
os.environ["DJANGO_SECURE_HSTS_SECONDS"] = "0"
os.environ["INQUIRY_RATE_LIMIT"] = "10"
os.environ["INQUIRY_RATE_WINDOW_SECONDS"] = "600"
from .settings import *  # noqa: F403,F401
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
STORAGES = {"staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}}
SITE_URL = "https://example.test"
SECURE_HSTS_SECONDS = 0
INQUIRY_RATE_LIMIT = 10
INQUIRY_RATE_WINDOW_SECONDS = 600
