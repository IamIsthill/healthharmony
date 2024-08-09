from healthharmony.app.settings import BASE_DIR

STATIC_URL = "static/"

STATICFILES_DIRS = [BASE_DIR / "healthharmony/static", BASE_DIR / "node_modules"]

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "healthharmony/media"
