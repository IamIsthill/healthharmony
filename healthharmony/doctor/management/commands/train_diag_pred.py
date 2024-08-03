from django.core.management.base import BaseCommand
from healthharmony.doctor.functions import train_diagnosis_predictor


class Command(BaseCommand):
    help = "Train the diagnosis predictor model and save it"

    def handle(self, *args, **kwargs):
        train_diagnosis_predictor()
        self.stdout.write(
            self.style.SUCCESS(
                "Successfully trained and saved the diagnosis predictor model"
            )
        )
