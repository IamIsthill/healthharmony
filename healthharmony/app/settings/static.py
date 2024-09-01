from healthharmony.app.settings import BASE_DIR, env
import os

STATIC_URL = "static/"

STATICFILES_DIRS = [BASE_DIR / "healthharmony/static", BASE_DIR / "node_modules"]

if not env.bool("PROD", default=False):
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    MEDIA_ROOT = BASE_DIR / "healthharmony/media"
    MEDIA_URL = "media/"


# STATICFILES_FINDERS = [
#     "django.contrib.staticfiles.finders.FileSystemFinder",
#     "django.contrib.staticfiles.finders.AppDirectoriesFinder",
# ]
