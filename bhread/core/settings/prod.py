import os
from pathlib import Path

from .base import *

DEBUG = False

ALLOWED_HOSTS = [".bhread.com"]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

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
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

INTERNAL_IPS = []
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
