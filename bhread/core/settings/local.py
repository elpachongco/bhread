import os
import socket
from pathlib import Path

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": (Path(os.environ.get("POSTGRES_PASSWORD_FILE")))
        .read_text()
        .strip("\n"),
        "HOST": "0.0.0.0",
        "PORT": 5432,
        "TEST": {
            "NAME": "POSTGRES_TESTING",
            "USER": "POSTGRES",
            "PASSWORD": "POSTGRES",
        },
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

INSTALLED_APPS += [
    "debug_toolbar",
    "django_browser_reload",
]

MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",  # See docs for position
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())

INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
    "127.0.0.1",
    "10.0.2.2",
]
