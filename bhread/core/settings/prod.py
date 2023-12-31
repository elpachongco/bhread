import os
from pathlib import Path

from .base import *

DEBUG = False

ALLOWED_HOSTS = [".bhread.com", "localhost", "137.184.189.131", "127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": (Path(os.environ.get("POSTGRES_PASSWORD_FILE")))
        .read_text()
        .strip("\n"),
        "HOST": "db",
        "PORT": 5432,
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis:6379",
    }
}

INTERNAL_IPS = []
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = ["https://bhread.com", "https://www.bhread.com"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
