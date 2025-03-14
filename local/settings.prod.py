from healthharmony.app.settings import env

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("APP_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = [
    "healthharmony.duckdns.org",
    "localhost",
    "127.0.0.1",
    "3.25.66.252",  # Change the IP everytime
]

if not DEBUG:
    CSRF_TRUSTED_ORIGINS = [
        "https://healthharmony.duckdns.org",
        "http://healthharmony.duckdns.org",
    ]

else:
    CSRF_TRUSTED_ORIGINS = [
        "http://127.0.0.1:8000",
        "http://127.0.0.1",
        "http://localhost",
        "http://localhost:8000",
    ]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "HOST": env("DATABASE_HOST"),
        # "HOST": "35.240.250.37",
        "PORT": 6543,
        "USER": env("DATABASE_USER"),
        # "USER": "healthharmony",
        # "PASSWORD": env("GOOGLE_DB_PASSWORD"),
        "PASSWORD": env("DATABASE_PASSWORD"),
    }
}

if env.bool("AWS_DB", False):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",
            "HOST": env("AWS_DB_HOST"),
            "PORT": env("AWS_DB_PORT"),
            "USER": env("AWS_DB_USER"),
            "PASSWORD": env("AWS_DB_PASS"),
        }
    }


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# AWS Configuration for Static files
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY")

AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")

AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")

AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

AWS_S3_FILE_OVERWRITE = False


STORAGES = {
    "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
    "staticfiles": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
}

MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

if env.bool("IN_DOCKER", True):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "postgres",  # Default database name for PostgreSQL
            "USER": "postgres",  # Default PostgreSQL user
            "PASSWORD": "12345678",  # The password you set
            "HOST": "localhost",  # or '127.0.0.1'
            "PORT": "5432",  # Default PostgreSQL port
        }
    }

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://0.0.0.0:6379/",
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
