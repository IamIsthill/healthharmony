from healthharmony.treatment.models import Illness
from healthharmony.administrator.models import Log

import logging
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib


logger = logging.getLogger(__name__)


def get_illness_data():
    """
    Fetches all illness data from the database.

    This function retrieves all entries from the Illness model in the database.
    It logs an informational message if the data is successfully fetched.
    If an exception occurs, it logs an error message and returns None.

    Returns:
        QuerySet or None: A Django QuerySet containing all entries from the Illness model,
                          or None if an exception occurred.

    Raises:
        Exception: If there is an error fetching data from the database.
    """
    try:
        data = Illness.objects.all().values("")
        logger.info("Illness data was successfully fetched.")
        return list(data)
    except Exception as e:
        logger.error(f"Illness data not fetched: {e}")
        return None


def train_diagnosis_predictor(context):
    data = get_illness_data()

    if data is None:
        return

    # df = pd.DataFrame(data)
