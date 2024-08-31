from healthharmony.app.settings import BASE_DIR
import os

STATIC_URL = "static/"


STATICFILES_DIRS = [BASE_DIR / "healthharmony/static", BASE_DIR / "node_modules"]

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "healthharmony/media"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]
