"""
ASGI config for main project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from healthharmony.app.settings import BASE_DIR

from django.core.asgi import get_asgi_application
from whitenoise import WhiteNoise
from environ import Env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthharmony.app.settings")

env = Env()
Env.read_env(env_file=".env")

application = get_asgi_application()

# if env.bool('PROD'):
#     print("ASGI: Collecting static files in folder ['staticfiles']")
#     application = WhiteNoise(application, root=os.path.join(BASE_DIR, 'staticfiles')) # type: ignore
