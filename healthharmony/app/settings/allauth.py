from healthharmony.app.settings import env


SITE_ID = 1
# if env.bool("PROD", True):
#     SOCIALACCOUNT_PROVIDERS = {
#         "google": {
#             "SCOPE": ["profile", "email"],
#             "AUTH_PARAMS": {"access_type": "online"},
#             "APP": {
#                 "client_id": env("CLIENT_ID"),  # type: ignore # noqa: F821
#                 "secret": env("CLIENT_SECRET"),  # type: ignore # noqa: F821
#                 "key": "",
#             },
#             "OAUTH_PKCE_ENABLED": True,
#             "REDIRECT_URI": "http://healthharmony.duckdns.org/accounts/google/login/callback/",
#         }
#     }
# else:
#     SOCIALACCOUNT_PROVIDERS = {
#         "google": {
#             "SCOPE": ["profile", "email"],
#             "AUTH_PARAMS": {"access_type": "online"},
#             "APP": {
#                 "client_id": env("CLIENT_ID"),  # type: ignore # noqa: F821
#                 "secret": env("CLIENT_SECRET"),  # type: ignore # noqa: F821
#                 "key": "",
#             },
#             "OAUTH_PKCE_ENABLED": True,
#             "REDIRECT_URI": "http://127.0.0.1:8000/accounts/google/login/callback/",
#         }
#     }

# # LOGIN_REDIRECT_URL = "/"
# LOGOUT_REDIRECT_URL = "/"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True  # Log in agad user once na reset
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[HealthHarmony]"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

if env.bool("PROD", True):
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"


ACCOUNT_FORMS = {
    "signup": "healthharmony.users.forms.CustomSignUpForm",
    # "login": "healthharmony.users.forms.GoogleLoginForm",
    "reset_password_from_key": "allauth.account.forms.ResetPasswordKeyForm",
}
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
