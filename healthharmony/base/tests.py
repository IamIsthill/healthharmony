from django.test import TestCase
from healthharmony.doctor.models import ModelLog


# Create your tests here.
class BaseTest(TestCase):
    def test_check_model_log(self):
        logs = ModelLog.objects.all()
        expected = 0
        self.assertEqual(logs.count(), expected)
