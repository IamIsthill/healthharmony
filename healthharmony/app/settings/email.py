from healthharmony.app.settings import env


# For sending email to user
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_ADD")
EMAIL_HOST_PASSWORD = env("EMAIL_PASS")
