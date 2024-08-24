from django.test import TestCase, RequestFactory
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
from django.urls import reverse
from django.utils import timezone
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest

from healthharmony.users.models import User
from healthharmony.treatment.models import Illness
from healthharmony.staff.forms import EditInventoryForm, DeleteInventoryForm
from healthharmony.inventory.models import InventoryDetail, QuantityHistory
from healthharmony.administrator.models import Log


# Create your tests here.
class EditInventoryFormTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create(
            email="bercasiocharles@gmail.com", password="12345"
        )

        # Create an inventory item
        self.inventory = InventoryDetail.objects.create(
            item_no=1,
            unit="pcs",
            item_name="Test Item",
            category="Medicine",
            description="Test Description",
            expiration_date=timezone.now(),
            added_by=self.user,
        )
        self.factory = RequestFactory()

    def test_save_form_valid(self):
        request = self.factory.post("/some-url/")
        request.user = self.user
        # New data to update the inventory
        data = {
            "item_no": 2,
            "unit": "box",
            "item_name": "Updated Item",
            "category": "Supply",
            "description": "Updated Description",
            "expiration_date": "2025-01-01",
            "quantity": 100,
        }

        # Instantiate form with data
        form = EditInventoryForm(data=data)

        # Check form is valid
        self.assertTrue(form.is_valid())

        # Call the save method
        form.save(request, pk=self.inventory.pk)

        # Fetch the updated inventory item
        updated_inventory = InventoryDetail.objects.get(pk=self.inventory.pk)

        # Assertions to check if the fields are updated correctly
        self.assertEqual(updated_inventory.item_no, 2)
        self.assertEqual(updated_inventory.unit, "box")
        self.assertEqual(updated_inventory.item_name, "Updated Item")
        self.assertEqual(updated_inventory.category, "Supply")
        self.assertEqual(updated_inventory.description, "Updated Description")
        self.assertEqual(
            updated_inventory.expiration_date, timezone.datetime(2025, 1, 1).date()
        )

        # Check if QuantityHistory is created
        quantity_history = QuantityHistory.objects.filter(
            inventory=updated_inventory
        ).first()
        self.assertIsNotNone(quantity_history)
        self.assertEqual(quantity_history.updated_quantity, 100)

    def test_save_form_invalid(self):
        request = self.factory.post("/some-url/")
        request.user = self.user
        # Invalid data (missing required fields)
        data = {
            "item_name": "",  # Missing required item_name
            "category": "Supply",
            "description": "Updated Description",
            "expiration_date": "2025-01-01",
            "quantity": 100,
        }

        # Instantiate form with data
        form = EditInventoryForm(data=data)

        # Check form is invalid
        self.assertFalse(form.is_valid())

        # Try saving (should not update anything)
        with self.assertRaises(Exception):
            form.save(request, pk=self.inventory.pk)


class DeleteInventoryFormTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create(
            email="bercasiocharles@gmail.com", password="12345"
        )
        # Create a test inventory item
        self.inventory_item = InventoryDetail.objects.create(
            item_no=1,
            unit="pcs",
            item_name="Test Item",
            category="Medicine",
            description="Test Description",
            expiration_date=timezone.now(),
            added_by=self.user,
        )

        self.quantity = QuantityHistory.objects.create(
            inventory=self.inventory_item, changed_by=self.user, updated_quantity=10
        )
        self.factory = RequestFactory()
        self.request = HttpRequest()
        self.request.user = self.user
        self.request.session = {}
        self.request._messages = FallbackStorage(self.request)

    def test_successful_deletion(self):
        form = DeleteInventoryForm()
        pk = 1

        form.save(self.request, pk)

        # Test if the item is deleted
        with self.assertRaises(InventoryDetail.DoesNotExist):
            InventoryDetail.objects.get(pk=self.inventory_item.pk)

        # Check if a success message is added
        messages = list(self.request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0].message,
            f"Successfully deleted inventory item {self.inventory_item.item_name}",
        )

    def test_deletion_with_invalid_pk(self):
        form = DeleteInventoryForm()  # Non-existent PK
        pk = 900

        form.save(self.request, pk)

        # Ensure no items were deleted
        self.assertEqual(InventoryDetail.objects.count(), 1)

        # Check if an error message is added
        messages = list(self.request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0].message, "Failed to delete inventory record. Please try again"
        )

    def test_deletion_with_no_pk(self):

        form = DeleteInventoryForm()  # Missing PK
        pk = ""
        form.save(self.request, pk)
        self.assertTrue(
            InventoryDetail.objects.filter(pk=self.inventory_item.pk).exists()
        )

        # Check if an error message is added
        messages = list(self.request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            messages[0].message, "Failed to delete inventory record. Please try again"
        )

        # Ensure no log entry was created
        self.assertEqual(Log.objects.filter(user=self.user).count(), 0)


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
