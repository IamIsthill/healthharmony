from healthharmony.app.settings import env


SITE_ID = 1
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "APP": {
            "client_id": env("CLIENT_ID"),
            "secret": env("CLIENT_SECRET"),
            "key": "",
        },
        "OAUTH_PKCE_ENABLED": True,
        "REDIRECT_URI": "http://127.0.0.1:7000/accounts/google/login/callback/",
    }
}

# LOGIN_REDIRECT_URL = "patient/"
LOGOUT_REDIRECT_URL = "/"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_ADAPTER = "healthharmony.users.adapters.MySocialAccountAdapter"

ACCOUNT_FORMS = {
    "signup": "healthharmony.users.forms.GoogleSignUpForm",
    "login": "healthharmony.users.forms.GoogleLoginForm",
}
