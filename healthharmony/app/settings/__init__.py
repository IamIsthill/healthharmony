from split_settings.tools import include, optional
import environ
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

env = environ.Env()
environ.Env.read_env(env_file="healthharmony/.env")

try:
    PROD = env.bool("PROD", default=False)
    logger.info(f"PROD environment variable is set to: {PROD}")

    SETTINGS_PATH = (
        BASE_DIR / "prod/settings.prod.py"
        if PROD
        else BASE_DIR / "local/settings.dev.py"
    )

    include(
        "base_settings.py",
        "database.py",
        "allauth.py",
        "email.py",
        "logging.py",
        SETTINGS_PATH,
    )

except Exception as e:
    logger.error(f"Error in settings configuration: {str(e)}")
    raise
