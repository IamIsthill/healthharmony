from django import forms
import json
import logging
from django.core.serializers import serialize
from django.contrib import messages


from healthharmony.administrator.models import Log, DataChangeLog
from healthharmony.models.inventory.models import InventoryDetail
from healthharmony.models.treatment.models import Illness, Category
from healthharmony.users.models import User

logger = logging.getLogger(__name__)


class UpdateIllness(forms.Form):
    illness_id = forms.IntegerField(required=True)
    issue = forms.Textarea()
    diagnosis = forms.Textarea()
    category = forms.CharField(max_length=100, required=True)

    def save(self, request):
        illness_id = self.cleaned_data.get("illness_id")
        issue = self.cleaned_data.get("issue")
        diagnosis = self.cleaned_data.get("diagnosis")
        category = self.cleaned_data.get("category")
        try:
            old_illness = Illness.objects.get(pk=illness_id)
            category, created = Category.objects.get_or_create(category=category)
            if created:
                logger.info(
                    f"{request.user.email} created a new category instance[id:{category.id}]"
                )
            new_illness = Illness.objects.update_or_create(
                id=illness_id, issue=issue, diagnosis=diagnosis, category=category
            )
            DataChangeLog.objects.create(
                table="Illness",
                record_id=new_illness.id,
                action="update",
                changed_by=request.user,
                old_value=serialize("json", [old_illness]),
                new_value=serialize("json", [new_illness]),
            )
            messages.success(request, "Successfully updated illness case!")

        except Exception as e:
            logger.warning(
                f"{request.user.email} failed to update illness instance[id:{illness_id}]: {str(e)}"
            )
            messages.error(
                request, "Failed to update the illness case. Please try again."
            )
