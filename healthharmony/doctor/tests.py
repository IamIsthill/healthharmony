from django.test import TestCase
import json
import pandas as pd
from io import StringIO
from textacy import text_stats as ts
from textacy import preprocessing as pre
import textacy as t
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB, ComplementNB
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import VotingClassifier
from imblearn.pipeline import Pipeline as imbpipeline
from imblearn.over_sampling import SMOTE
from sklearn.metrics import accuracy_score, classification_report

import threading
from datetime import date

from healthharmony.users.models import User
from healthharmony.treatment.models import Illness
from healthharmony.staff.forms import EditInventoryForm
from healthharmony.inventory.models import InventoryDetail, QuantityHistory


# Create your tests here.
class StaffUpdateInventoryFormTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create(
            first_name="Charles",
            last_name="Bercasio",
            email="bercasiocharles@gmail.com",
            year=4,
            section="A",
            program="Bachelor of Science Major in Information Technology",
        )
        cls.item1 = InventoryDetail.objects.create(
            item_no=1001,
            unit="pcs.",
            item_name="Paracetamol",
            category="Medicine",
            description=None,
            expiration_date=date(2222, 1, 1),
            added_by=cls.staff,
        )

    def test_date(self):
        inventory = InventoryDetail.objects.get(id=1)
        expected = "2222-01-01"
        output = inventory.expiration_date.isoformat()
        self.assertEqual(expected, output)


# class PredictorTestCase(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         cls.user = User.objects.create(
#             first_name="Charles",
#             last_name="Bercasio",
#             email="bercasiocharles@gmail.com",
#             year=4,
#             section="A",
#             program="Bachelor of Science Major in Information Technology",
#         )

#         cls.doctor = User.objects.create(
#             first_name="Jane", last_name="Smith", email="janesmith@gmail.com"
#         )

#         cls.illness1 = Illness.objects.create(
#             patient=cls.user,
#             issue="Persistent cough",
#             doctor=cls.doctor,
#             diagnosis="Chronic Bronchitis",
#         )

#         cls.illness2 = Illness.objects.create(
#             patient=cls.user,
#             issue="Maraming marami",
#             doctor=cls.doctor,
#             diagnosis="May sakit",
#         )

#         cls.illness3 = Illness.objects.create(
#             patient=cls.user,
#             issue="Sharp chest pain",
#             doctor=cls.doctor,
#             diagnosis="Heart Disease",
#         )

#         cls.illness4 = Illness.objects.create(
#             patient=cls.user,
#             issue="Unusual fatigue",
#             doctor=cls.doctor,
#             diagnosis="Anemia",
#         )

#         cls.illness5 = Illness.objects.create(
#             patient=cls.user,
#             issue="Nausea and vomiting",
#             doctor=cls.doctor,
#             diagnosis="Gastritis",
#         )

#         cls.illness6 = Illness.objects.create(
#             patient=cls.user,
#             issue="Headache and fever",
#             doctor=cls.doctor,
#             diagnosis="Flu",
#         )

#     def test_number_illness(self):
#         try:
#             illness = Illness.objects.all().count() or 0
#         except:  # noqa: 722
#             illness = 0
#         expected = 6
#         self.assertEqual(illness, expected)

#     def test_illness_issue_diag(self):
#         try:
#             illness = Illness.objects.all().values("pk", "issue", "diagnosis")
#             illness = list(illness)
#             illness = json.dumps(illness)
#             illness = StringIO(illness)
#             df = pd.read_json(illness)
#         except:  # noqa: 722
#             illness = None

#         preproc = pre.make_pipeline(
#             pre.remove.html_tags,
#             pre.replace.urls,
#             pre.normalize.unicode,
#             pre.remove.punctuation,
#             pre.replace.emojis,
#             pre.normalize.whitespace,
#         )

#         def string_lemma(lemmas):
#             return " ".join(lemmas)

#         issue = []

#         # def process_text(text):
#         #     text = row.issue.replace("\n", "")
#         #     doc = t.make_spacy_doc(preproc(text), lang="en_core_web_sm")
#         #     lemma = [i.lemma_ for i in doc]
#         #     issue.append(string_lemma(lemma))

#         for index, row in df.iterrows():
#             text = row.issue.replace("\n", "")
#             doc = t.make_spacy_doc(preproc(text), lang="en_core_web_sm")
#             lemma = [i.lemma_ for i in doc]
#             issue.append(string_lemma(lemma))

#         df["iss_lem"] = issue

#         base_classifiers = [
#             ("MultinomialNB", MultinomialNB()),
#             ("ComplementNB", ComplementNB()),
#             (
#                 "LinearSVC",
#                 LinearSVC(dual="auto", random_state=42),
#             ),  # Explicitly set the `dual` parameter
#             ("RandomForest", RandomForestClassifier(random_state=42)),
#             ("GradientBoosting", GradientBoostingClassifier(random_state=42)),
#             ("LogisticRegression", LogisticRegression(max_iter=1000, random_state=42)),
#             ("KNeighbors", KNeighborsClassifier(n_neighbors=1)),
#             ("DecisionTree", DecisionTreeClassifier(random_state=42)),
#         ]

#         voting_clf = VotingClassifier(estimators=base_classifiers, voting="hard")
#         X, y = df.iss_lem.str.lower(), df.diagnosis
#         X_train, X_test, y_train, y_test = train_test_split(
#             X, y, test_size=0.2, random_state=42
#         )

#         model = imbpipeline(
#             [
#                 ("tfidf", TfidfVectorizer(stop_words="english")),
#                 ("smote", SMOTE(random_state=42)),
#                 ("clf", voting_clf),
#             ]
#         )
#         model.fit(X_train, y_train)
#         model_pred = model.predict(X_test)

#         print("")
#         print(model.predict(["fever"]))
#         print(f"Score: {accuracy_score(y_test, model_pred):.2f}")
#         print(classification_report(y_test, model_pred, zero_division=0))

#         self.assertIsNotNone(illness)
