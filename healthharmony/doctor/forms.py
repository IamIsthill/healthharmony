from django import forms
import json
import logging
from django.core.serializers import serialize
from django.contrib import messages


from healthharmony.administrator.models import Log, DataChangeLog
from healthharmony.models.inventory.models import InventoryDetail, QuantityHistory
from healthharmony.models.treatment.models import (
    Illness,
    Category,
    IllnessTreatment,
    DoctorDetail,
)
from healthharmony.users.models import User

logger = logging.getLogger(__name__)


class UpdateIllness(forms.Form):
    illness_id = forms.IntegerField(required=True)
    issue = forms.CharField(max_length=500, required=True)
    diagnosis = forms.CharField(max_length=500, required=True)
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
            new_illness = Illness.objects.get(id=illness_id)
            new_illness.issue = issue
            new_illness.diagnosis = diagnosis
            new_illness.illness_category = category
            new_illness.doctor = request.user
            new_illness.save()

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


class UpdateTreatmentForIllness(forms.Form):
    illness_id = forms.IntegerField(required=True)
    inventory_item = forms.CharField(max_length=None)
    inventory_quantity = forms.CharField(max_length=None)

    def save(self, request):
        illness_id = self.cleaned_data.get("illness_id")

        # List ng input fields with same name
        inventory_items = request.POST.getlist("inventory_item")
        inventory_quantities = request.POST.getlist("inventory_quantity")

        # list should have same length
        if len(inventory_items) != len(inventory_quantities):
            raise forms.ValidationError("Mismatched inventory items and quantities.")

        # Get yung illness first
        try:
            illness = Illness.objects.get(id=int(illness_id))
        except Exception as e:
            logger.info(
                f"{request.user.email} tried to fetched illness instance[id:{illness_id}] but found none: {str(e)}"
            )
            messages.error(request, "Illness case was not found.")
            return

        # Join the two list then update the db heheh
        for item_name, item_quantity in zip(inventory_items, inventory_quantities):
            # Hanapin muna ang inventory item
            try:
                inventory_instance = InventoryDetail.objects.get(item_name=item_name)
            except Exception as e:
                logger.info(
                    f"{request.user.email} failed to find inventory instance with item_name[{item_name}]: {str(e)}"
                )
                messages.error(
                    request,
                    "Failed to find the related inventory item for prescription",
                )
                return

            # With inventory item, now create yung treatments
            try:
                IllnessTreatment.objects.create(
                    illness=illness,
                    inventory_detail=inventory_instance,
                    quantity=-(int(item_quantity)),
                )
            except Exception as e:
                logger.info(
                    f"{request.user.email} failed to add prescriptions to illness instance[id={illness_id}]: {str(e)}"
                )
                messages.error(
                    request,
                    "Failed to add prescription/s to the patient's case. Please try again.",
                )
                return

            # Now update your inventory table
            update_inventory(inventory_instance, item_quantity, request)

        # If everything is okay, log the event and add message
        logger.info(
            f"{request.user.email} successfully added prescription records to illness instance[id={illness_id}]"
        )
        messages.success(request, "Successfully added prescriptions.")

        Log.objects.create(
            user=request.user,
            action=f"Added prescriptions to illness instance[id={illness_id}]",
        )

        return


def update_inventory(inventory_instance, item_quantity, request):
    # Now update your inventory table
    try:
        QuantityHistory.objects.create(
            inventory=inventory_instance,
            updated_quantity=-(int(item_quantity)),
            changed_by=request.user,
        )
    except Exception as e:
        logger.error(f"Failed to update the inventory: {str(e)}")


class UpdateDoctorSched(forms.Form):
    time_start = forms.TimeField()
    time_end = forms.TimeField()

    def save(self, request):
        doctor = request.user

        time_start = request.POST.get("time_start")
        time_end = request.POST.get("time_end")
        is_avail = request.POST.get("is_avail")

        try:
            # Find the related instance first
            updated_sched = DoctorDetail.objects.get(doctor=doctor)

            # If start and end is avail, update them
            if time_start and time_end:
                updated_sched.time_avail_start = time_start
                updated_sched.time_avail_end = time_end
                updated_sched.save()

                logger.info(
                    f"{request.user.email} has updated doctor sched with id[{updated_sched.id}]"
                )
                messages.success(request, "Successfully updated your schedule.")

            # Else check kung avail yung 'is_avail' then update it
            elif is_avail:
                updated_sched.avail = is_avail
                updated_sched.save()

                logger.info(
                    f"{request.user.email} has updated doctor sched with id[{updated_sched.id}]"
                )
                messages.success(request, "Successfully updated your availability.")

        except Exception as e:
            logger.warning(
                f"{request.user.email} failed to update the doctor instance: ${str(e)}"
            )
            messages.error(request, "Failed to up")
