from healthharmony.app.settings import env

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-s(5zc6(qerhzjavz+s-2t=2e*sud4*)8_5g74b#dw(um4%np2+"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "HOST": "aws-0-ap-southeast-1.pooler.supabase.com",
        "PORT": 6543,
        "USER": "postgres.eplhequpinproconhfdc",
        "PASSWORD": "iw21H2VytOlXQXKw",
    }
}

# AWS Configuration for Static files
AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY")

AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")

AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")

AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"


AWS_S3_FILE_OVERWRITE = False


# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'


STORAGES = {
    "default": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
    "staticfiles": {"BACKEND": "storages.backends.s3boto3.S3Boto3Storage"},
}

MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
