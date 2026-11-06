#!/usr/bin/env python
"""Create local-only settings with a random key, then initialise SQLite.

Does not overwrite .env. Does not install packages or create an admin password.
Run after installing requirements.txt in your virtual environment.
"""
import os
import secrets
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    if sys.version_info < (3, 12):
        raise SystemExit("Use Python 3.12 or newer. Python 3.12/3.13 are recommended for this package.")
    try:
        import django  # noqa: F401
        from dotenv import dotenv_values
    except ImportError:
        raise SystemExit("First run: python -m pip install -r requirements.txt")
    env_file = ROOT / ".env"
    if not env_file.exists():
        content = "\n".join([
            "# LOCAL DEVELOPMENT ONLY. Never publish this file.",
            "DJANGO_DEBUG=true",
            "DJANGO_SECRET_KEY=" + secrets.token_urlsafe(64),
            "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,[::1]",
            "DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000",
            "SITE_URL=http://127.0.0.1:8000",
            "DJANGO_SECURE_SSL_REDIRECT=false",
            "DJANGO_TRUST_PROXY_HEADERS=false",
            "DB_ENGINE=sqlite", "SQLITE_PATH=db.sqlite3", "INQUIRY_EMAIL_ENABLED=false", "",
        ])
        fd = os.open(env_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        print("Created local .env with a unique secret key.")
    values = dotenv_values(env_file)
    debug = os.environ.get("DJANGO_DEBUG", values.get("DJANGO_DEBUG", "false"))
    engine = os.environ.get("DB_ENGINE", values.get("DB_ENGINE", "sqlite"))
    if str(debug).lower() not in {"true", "1", "yes"} or engine != "sqlite":
        raise SystemExit("Existing settings are not local SQLite development settings; left unchanged. Use the deployment instructions.")
    subprocess.run([sys.executable, "manage.py", "check"], cwd=ROOT, check=True)
    subprocess.run([sys.executable, "manage.py", "migrate", "--noinput"], cwd=ROOT, check=True)
    print("Ready. Create your admin: python manage.py createsuperuser")
    print("Start: python manage.py runserver 127.0.0.1:8000")

if __name__ == "__main__":
    main()
