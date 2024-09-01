from healthharmony.app.settings import BASE_DIR, env

if not env.bool("PROD"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
