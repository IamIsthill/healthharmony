from django.test import TestCase
import json
import pandas as pd
from io import StringIO
from textacy import text_stats as ts
import textacy as t
from textacy import preprocessing as pre, extract as ext
from functools import partial
from sklearn.preprocessing import FunctionTransformer

from healthharmony.users.models import User
from healthharmony.treatment.models import Illness


# Create your tests here.
class PredictorTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            first_name="Charles",
            last_name="Bercasio",
            email="bercasiocharles@gmail.com",
            year=4,
            section="A",
            program="Bachelor of Science Major in Information Technology",
        )

        cls.doctor = User.objects.create(
            first_name="Jane", last_name="Smith", email="janesmith@gmail.com"
        )

        cls.illness1 = Illness.objects.create(
            patient=cls.user,
            issue="Persistent cough",
            doctor=cls.doctor,
            diagnosis="Chronic Bronchitis",
        )

        cls.illness2 = Illness.objects.create(
            patient=cls.user,
            issue="Maraming marami",
            doctor=cls.doctor,
            diagnosis="May sakit",
        )

        cls.illness3 = Illness.objects.create(
            patient=cls.user,
            issue="Sharp chest pain",
            doctor=cls.doctor,
            diagnosis="Heart Disease",
        )

        cls.illness4 = Illness.objects.create(
            patient=cls.user,
            issue="Unusual fatigue",
            doctor=cls.doctor,
            diagnosis="Anemia",
        )

        cls.illness5 = Illness.objects.create(
            patient=cls.user,
            issue="Nausea and vomiting",
            doctor=cls.doctor,
            diagnosis="Gastritis",
        )

        cls.illness6 = Illness.objects.create(
            patient=cls.user,
            issue="Headache and fever",
            doctor=cls.doctor,
            diagnosis="Flu",
        )

    def test_number_illness(self):
        try:
            illness = Illness.objects.all().count() or 0
        except:  # noqa: 722
            illness = 0
        expected = 6
        self.assertEqual(illness, expected)

    def test_illness_issue_diag(self):
        try:
            illness = Illness.objects.all().values("pk", "issue", "diagnosis")
            illness = list(illness)
            illness = json.dumps(illness)
            illness = StringIO(illness)
            df = pd.read_json(illness)
        except:  # noqa: 722
            illness = None

        preproc = pre.make_pipeline(
            pre.remove.html_tags,
            pre.replace.urls,
            pre.normalize.unicode,
            pre.remove.punctuation,
            pre.replace.emojis,
            pre.normalize.whitespace,
        )

        def string_lemma(lemmas):
            return " ".join(lemmas)

        issue = []

        for index, row in df.iterrows():
            text = row.issue.replace("\n", "")
            doc = t.make_spacy_doc(preproc(text), lang="en_core_web_sm")
            lemma = [i.lemma_ for i in doc]
            issue.append(string_lemma(lemma))

        df["iss_lem"] = issue

        print("")
        print(df.head())

        self.assertIsNotNone(illness)
