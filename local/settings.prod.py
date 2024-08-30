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
