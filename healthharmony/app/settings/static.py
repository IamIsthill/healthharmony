from healthharmony.app.settings import BASE_DIR, env
import os

STATIC_URL = "static/"
MEDIA_URL = "media/"

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_ROOT = BASE_DIR / "healthharmony/media"
STATICFILES_DIRS = [BASE_DIR / "healthharmony/static", BASE_DIR / "node_modules"]
