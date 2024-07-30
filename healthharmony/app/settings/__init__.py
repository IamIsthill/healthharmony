from split_settings.tools import include, optional
import environ


env = environ.Env()
environ.Env.read_env()

include(
    "base_settings.py",
    "allauth.py",
    "email.py",
    "logging.py",
)
