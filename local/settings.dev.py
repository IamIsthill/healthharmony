from healthharmony.app.settings.logging import LOGGING
from healthharmony.app.settings import BASE_DIR
import os


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-s(5zc6(qerhzjavz+s-2t=2e*sud4*)8_5g74b#dw(um4%np2+"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "localhost",
    "localhost:8000",
    "127.0.0.1",
    "127.0.0.1:8000",
]

LOGGING["formatters"]["colored"] = {  # type: ignore noqa: F821
    "()": "colorlog.ColoredFormatter",
    "format": "%(log_color)s%(asctime)s %(levelname)s %(name)s %(bold_white)s%(message)s",
}

LOGGING["loggers"]["healthharmony"]["level"] = "DEBUG"  # type: ignore
LOGGING["handlers"]["console"]["level"] = "DEBUG"  # type: ignore
LOGGING["handlers"]["console"]["formatter"] = "colored"  # type: ignore

CSRF_TRUSTED_ORIGINS = [
    "http://healthharmony.duckdns.org:8000",
    "http://healthharmony.duckdns.org",
    "http://127.0.0.1:8000",
    "http://127.0.0.1",
    "http://localhost",
    "http://localhost:8000",
]
