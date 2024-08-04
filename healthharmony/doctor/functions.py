from healthharmony.treatment.models import Illness

import logging
import pandas as pd
import joblib
import json
from io import StringIO
from textacy import preprocessing as pre
import textacy as t

from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB, ComplementNB
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import VotingClassifier

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as imbpipeline
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

logger = logging.getLogger(__name__)


def get_illness_data():
    """
    Fetches all illness data from the database.

    This function retrieves all entries from the Illness model in the database.
    It logs an informational message if the data is successfully fetched.
    If an exception occurs, it logs an error message and returns None.

    Returns:
        pd.DataFrame or None: A pandas DataFrame containing all entries from the Illness model,
                              or None if an exception occurred.

    Raises:
        Exception: If there is an error fetching data from the database.
    """
    try:
        data = Illness.objects.all().values("pk", "issue", "diagnosis")
        logger.info("Illness data was successfully fetched.")
        data = list(data)
        data = json.dumps(data)
        data = StringIO(data)
        df = pd.read_json(data)
        return df
    except Exception as e:
        logger.error(f"Illness data not fetched: {e}")
        return None


def string_lemma(lemmas):
    """
    Converts a list of lemmas into a single string.

    This function takes a list of lemmas (base forms of words) and concatenates them into
    a single space-separated string.

    Args:
        lemmas (list of str): A list of lemmas.

    Returns:
        str: A space-separated string of lemmas.
    """
    return " ".join(lemmas)


# Define the text preprocessing pipeline
preproc = pre.make_pipeline(
    pre.remove.html_tags,
    pre.replace.urls,
    pre.normalize.unicode,
    pre.remove.punctuation,
    pre.replace.emojis,
    pre.normalize.whitespace,
)
"""
Pipeline: A text preprocessing pipeline using textacy.preprocessing.

This pipeline performs the following preprocessing steps:
    1. Removes HTML tags.
    2. Replaces URLs with a placeholder.
    3. Normalizes unicode characters.
    4. Removes punctuation.
    5. Replaces emojis with a placeholder.
    6. Normalizes whitespace.

Returns:
    function: A function that applies the preprocessing steps to input text.
"""


def get_processed_issues(df, issues):
    """
    Processes issues from the DataFrame by lemmatizing text.

    This function takes a DataFrame containing issue texts and processes each issue by:
    1. Removing newline characters.
    2. Preprocessing the text using a pipeline.
    3. Lemmatizing the processed text.
    4. Appending the lemmatized text to a list.

    Args:
        df (pd.DataFrame): The DataFrame containing issue texts. It must have a column named 'issue'.
        issues (list): A list to which the processed (lemmatized) issues will be appended.

    Returns:
        list: The updated list of processed (lemmatized) issues.
    """
    for index, row in df.iterrows():
        text = row.issue.replace("\n", "")
        doc = t.make_spacy_doc(preproc(text), lang="en_core_web_sm")
        lemma = [i.lemma_ for i in doc]
        issues.append(string_lemma(lemma))
    return issues


def get_voting_clf():
    """
    Creates and returns a VotingClassifier with various base classifiers.

    The VotingClassifier combines multiple base classifiers to form a stronger overall model.
    This function sets up a VotingClassifier with a range of base classifiers including Naive Bayes, SVM, Random Forest, and others.

    Returns:
        VotingClassifier: A VotingClassifier instance with the specified base classifiers.
    """
    base_classifiers = [
        ("MultinomialNB", MultinomialNB()),
        ("ComplementNB", ComplementNB()),
        ("LinearSVC", LinearSVC(dual="auto", random_state=42)),
        ("RandomForest", RandomForestClassifier(random_state=42)),
        ("GradientBoosting", GradientBoostingClassifier(random_state=42)),
        ("LogisticRegression", LogisticRegression(max_iter=1000, random_state=42)),
        ("KNeighbors", KNeighborsClassifier(n_neighbors=1)),
        ("DecisionTree", DecisionTreeClassifier(random_state=42)),
    ]
    voting_clf = VotingClassifier(estimators=base_classifiers, voting="hard")
    return voting_clf


def get_model(voting_clf, df):
    """
    Trains a pipeline model for diagnosis prediction.

    This function prepares and trains a machine learning pipeline model using the provided VotingClassifier.
    The pipeline includes TF-IDF vectorization, SMOTE for handling class imbalance, and the provided classifier.

    Args:
        voting_clf (VotingClassifier): The VotingClassifier instance to use as the base classifier in the pipeline.
        df (pd.DataFrame): The DataFrame containing the data for training. It must have columns 'iss_lem' and 'diagnosis'.

    Returns:
        imbpipeline: The trained machine learning pipeline.
    """
    X, y = df.iss_lem.str.lower(), df.diagnosis
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = imbpipeline(
        [
            ("tfidf", TfidfVectorizer(stop_words="english")),
            ("smote", SMOTE(random_state=42)),
            ("clf", voting_clf),
        ]
    )
    model.fit(X_train, y_train)
    return model


def train_diagnosis_predictor():
    """
    Fetches data, trains the model, and saves it to a file.

    This function:
    1. Fetches illness data from the database.
    2. Processes and lemmatizes the issue texts.
    3. Trains a machine learning model using a pipeline and VotingClassifier.
    4. Saves the trained model to a file.

    The model is saved to "healthharmony/static/assets/models/diagnosis_predictor.joblib".

    Returns:
        None
    """
    df = get_illness_data()

    if df is None:
        return
    issues = []
    df["iss_lem"] = get_processed_issues(df, issues)
    voting_clf = get_voting_clf()
    model = get_model(voting_clf, df)

    joblib.dump(model, "healthharmony/static/assets/models/diagnosis_predictor.joblib")


def predict_diagnosis(issue):
    text = issue.replace("\n", "")
    doc = t.make_spacy_doc(preproc(text), lang="en_core_web_sm")
    text = [i.lemma_ for i in doc]

    model_path = "healthharmony/static/assets/models/diagnosis_predictor.joblib"
    model = joblib.load(model_path)

    diagnosis = model.predict([string_lemma(text)])

    return diagnosis[0]


if __name__ == "__main__":
    train_diagnosis_predictor()
