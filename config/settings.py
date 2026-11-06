"""Settings for the standalone BURO site. Secrets are read from .env/environment."""
import os
from pathlib import Path
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=False)

def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default)).strip().lower()
    if value not in {"true", "false", "1", "0", "yes", "no"}:
        raise ImproperlyConfigured(f"{name}: use true/false.")
    return value in {"true", "1", "yes"}

def env_list(name: str, default: str = "") -> list[str]:
    return [item.strip() for item in os.getenv(name, default).split(",") if item.strip()]

DEBUG = env_bool("DJANGO_DEBUG")
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY or SECRET_KEY.startswith("CHANGE_ME") or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured("Set a unique DJANGO_SECRET_KEY (50+ characters); see README_RU.md.")
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,[::1]" if DEBUG else "")
if not ALLOWED_HOSTS or (not DEBUG and "*" in ALLOWED_HOSTS):
    raise ImproperlyConfigured("Set explicit DJANGO_ALLOWED_HOSTS; wildcard is not allowed in production.")
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")
SITE_URL = os.getenv("SITE_URL", "https://bp15.ru").rstrip("/")
site_parts = urlsplit(SITE_URL)
if site_parts.scheme not in {"http", "https"} or not site_parts.hostname or site_parts.username or site_parts.password or site_parts.path or site_parts.query or site_parts.fragment:
    raise ImproperlyConfigured("SITE_URL must be a full origin, e.g. https://bp15.ru (no path).")

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "website.apps.WebsiteConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "website.context_processors.site_context",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").strip()
if DB_ENGINE == "postgresql":
    required = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST"]
    if any(not os.getenv(name) for name in required):
        raise ImproperlyConfigured("PostgreSQL needs DB_NAME, DB_USER, DB_PASSWORD and DB_HOST.")
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DB_NAME"], "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"], "HOST": os.environ["DB_HOST"],
        "PORT": os.getenv("DB_PORT", "5432"), "CONN_MAX_AGE": 60,
        "OPTIONS": {"sslmode": os.getenv("DB_SSLMODE", "prefer")},
    }}
elif DB_ENGINE == "sqlite":
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / os.getenv("SQLITE_PATH", "db.sqlite3"),
        "OPTIONS": {"timeout": 20},
    }}
else:
    raise ImproperlyConfigured("DB_ENGINE must be sqlite or postgresql.")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Keep /assets/ URLs compatible with the supplied static site.
STATIC_URL = "/assets/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
WHITENOISE_MAX_AGE = 0  # Manifest-versioned resources still receive immutable caching.

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True  # AJAX reads the masked token in the form, not the cookie.
CSRF_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", not DEBUG)
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "0"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_HSTS_INCLUDE_SUBDOMAINS")
SECURE_HSTS_PRELOAD = env_bool("DJANGO_HSTS_PRELOAD")
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
X_FRAME_OPTIONS = "SAMEORIGIN"
TRUST_PROXY_HEADERS = env_bool("DJANGO_TRUST_PROXY_HEADERS")
if TRUST_PROXY_HEADERS:
    # Enable only behind a trusted proxy which overwrites these headers.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
DATA_UPLOAD_MAX_MEMORY_SIZE = 64 * 1024
DATA_UPLOAD_MAX_NUMBER_FIELDS = 30
CSRF_FAILURE_VIEW = "website.views.csrf_failure"

INQUIRY_RATE_LIMIT = int(os.getenv("INQUIRY_RATE_LIMIT", "10"))
INQUIRY_RATE_WINDOW_SECONDS = int(os.getenv("INQUIRY_RATE_WINDOW_SECONDS", "600"))
if INQUIRY_RATE_LIMIT < 1 or INQUIRY_RATE_WINDOW_SECONDS < 1:
    raise ImproperlyConfigured("Inquiry rate limit/window must be positive.")

# Without SMTP configuration, requests are stored in the admin; no mail is sent.
INQUIRY_EMAIL_ENABLED = env_bool("INQUIRY_EMAIL_ENABLED")
INQUIRY_RECIPIENTS = env_list("INQUIRY_RECIPIENTS")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL")
EMAIL_TIMEOUT = 8
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "")
if EMAIL_USE_TLS and EMAIL_USE_SSL:
    raise ImproperlyConfigured("Choose EMAIL_USE_TLS or EMAIL_USE_SSL, not both.")
if INQUIRY_EMAIL_ENABLED and (not INQUIRY_RECIPIENTS or not EMAIL_HOST or not DEFAULT_FROM_EMAIL):
    raise ImproperlyConfigured("Email notifications need INQUIRY_RECIPIENTS, EMAIL_HOST and DEFAULT_FROM_EMAIL.")

LOGGING = {
    "version": 1, "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {"website": {"handlers": ["console"], "level": "INFO", "propagate": False}},
}
