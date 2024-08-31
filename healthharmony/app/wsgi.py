"""
WSGI config for main project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
from environ import Env
from healthharmony.app.settings import BASE_DIR
from whitenoise import WhiteNoise
from django.core.wsgi import get_wsgi_application

env = Env()
Env.read_env(env_file=".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthharmony.app.settings")

application = get_wsgi_application()

if env.bool("PROD"):
    print("WSGI:Collecting static files in folder ['staticfiles']")
    application = WhiteNoise(application, root=os.path.join(BASE_DIR, "staticfiles"))  # type: ignore
