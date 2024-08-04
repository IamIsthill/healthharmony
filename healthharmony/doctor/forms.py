from django import forms
import json
import logging
from django.core.serializers import serialize

from healthharmony.administrator.models import Log, DataChangeLog
from healthharmony.inventory.models import InventoryDetail
from healthharmony.treatment.models import Illness, Category
from healthharmony.users.models import User

logger = logging.getLogger(__name__)


class UpdateIllness(forms.Form):
    """
    Form to update an existing Illness instance.

    Fields:
    - id: IntegerField to identify the Illness instance.
    - issue: Textarea for updating the issue description.
    - category: CharField for specifying the category name.
    - diagnosis: Textarea for updating the diagnosis description.
    """

    id = forms.IntegerField(required=True)
    issue = forms.CharField(widget=forms.Textarea(attrs={"rows": 4, "cols": 15}))
    category = forms.CharField(max_length=100)
    diagnosis = forms.CharField(widget=forms.Textarea(attrs={"rows": 4, "cols": 15}))

    def save(self, request):
        """
        Save the updated Illness instance and create logs for changes.

        Parameters:
        - request: HttpRequest object to get the current user (doctor).

        This method will:
        1. Retrieve the Illness instance by ID.
        2. Get or create the Category instance.
        3. Update the Illness fields and save the changes.
        4. Log the creation of new categories and changes to the illness.
        5. Handle exceptions and log errors.
        """
        doctor = request.user
        try:
            logger.info(
                "Attempting to retrieve Illness instance with ID %s",
                self.cleaned_data["id"],
            )
            illness = Illness.objects.get(id=self.cleaned_data.get("id"))
            old_illness = Illness.objects.get(
                id=self.cleaned_data.get("id")
            )  # Store the old state for logging purposes

            logger.info(
                "Attempting to get or create Category with name %s",
                self.cleaned_data["category"],
            )
            category, created = Category.objects.get_or_create(
                category=self.cleaned_data["category"]
            )

            if created:
                logger.info("New Category created with ID %s", category.id)
                DataChangeLog.objects.create(
                    table="Category",
                    record_id=category.id,
                    action="Create",
                    new_value=serialize("json", [category]),
                    changed_by=doctor,
                )
            else:
                # Update the Illness instance fields
                illness.issue = self.cleaned_data["issue"]
                illness.category = category
                illness.diagnosis = self.cleaned_data["diagnosis"]
                illness.doctor = doctor

                logger.info(
                    "Saving the updated Illness instance with ID %s", illness.id
                )
                illness.save()

                logger.info(
                    "Logging the changes to the Illness instance with ID %s", illness.id
                )
                DataChangeLog.objects.create(
                    table="Illness",
                    record_id=illness.id,
                    action="Update",
                    old_value=serialize("json", [old_illness]),
                    new_value=serialize("json", [illness]),
                    changed_by=doctor,
                )
        except Illness.DoesNotExist:
            logger.error(
                "Illness instance with ID %s does not exist", self.cleaned_data["id"]
            )
        except Exception as e:
            logger.error("An error occurred while updating the Illness instance: %s", e)
            raise
