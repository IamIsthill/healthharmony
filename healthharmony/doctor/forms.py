from django import forms
import json
import logging
from django.core.serializers import serialize
from django.contrib import messages
from django.db.models import Sum


from healthharmony.administrator.models import Log, DataChangeLog
from healthharmony.models.inventory.models import InventoryDetail, QuantityHistory
from healthharmony.models.treatment.models import (
    Illness,
    Category,
    IllnessTreatment,
    DoctorDetail,
    IllnessNote,
)
from healthharmony.users.models import User, Department

logger = logging.getLogger(__name__)


class UpdateIllness(forms.Form):
    illness_id = forms.IntegerField(required=True)
    issue = forms.CharField(required=True)
    diagnosis = forms.CharField(required=True)
    category = forms.CharField(required=True)

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

        # remove old treatments
        # delete_old_treatments(request, illness)

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
            # check first the quantity if it is greater than the one in stock
            try:
                total_quantity = inventory_instance.quantities.aggregate(
                    total_quantity=Sum("updated_quantity")
                )

                total_quantity = (
                    total_quantity["total_quantity"]
                    if total_quantity["total_quantity"] is not None
                    else 0
                )

                if int(total_quantity) < int(item_quantity):
                    messages.error(
                        request, "Inventory stock is lesser than the inputted quantity."
                    )
                    return

            except Exception as e:
                logger.error(
                    f"Inventory stock is lesser than the inputted quantity: {str(e)}"
                )
                messages.error(
                    request, "System faced an unexpected error. Please reload page."
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
            if total_quantity != item_quantity:
                item_quantity = int(item_quantity) if item_quantity else 0

                update_inventory(inventory_instance, -(item_quantity), request)

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


def delete_old_treatments(request, illness):
    try:
        treatments = IllnessTreatment.objects.filter(illness=illness)
        for treatment in treatments:
            treatment.delete()
    except Exception as e:
        logger.warning(
            f"Failed to deleted related treatment records for illness case[{illness.id}]: {str(e)}"
        )
        messages.error(request, "Failed to update treatments")
        return


def update_inventory(inventory_instance, item_quantity, request):
    # Now update your inventory table
    try:
        QuantityHistory.objects.create(
            inventory=inventory_instance,
            updated_quantity=item_quantity,
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

        try:
            # Find the related instance first
            updated_sched, created = DoctorDetail.objects.get_or_create(doctor=doctor)

            # If start and end is avail, update them
            if time_start and time_end:
                updated_sched.time_avail_start = time_start
                updated_sched.time_avail_end = time_end
                updated_sched.save()

                logger.info(
                    f"{request.user.email} has updated doctor sched with id[{updated_sched.id}]"
                )
                messages.success(request, "Successfully updated your schedule.")

        except Exception as e:
            logger.warning(
                f"{request.user.email} failed to update the doctor instance: ${str(e)}"
            )
            messages.error(request, "Failed to update date")


class UpdateDoctorAvail(forms.Form):
    is_avail = forms.BooleanField(required=True)

    def save(self, request):
        doctor = request.user
        is_avail = request.POST.get("is_avail")
        logger.info(is_avail)

        try:
            updated_sched, created = DoctorDetail.objects.get_or_create(doctor=doctor)

            if is_avail == "yes":
                updated_sched.avail = True
            elif is_avail == "no":
                updated_sched.avail = False

            updated_sched.save()

            logger.info(
                f"{request.user.email} has updated doctor sched with id[{updated_sched.id}]"
            )
            messages.success(request, "Successfully updated your availability.")

        except Exception as e:
            logger.warning(
                f"{request.user.email} failed to update the doctor instance: ${str(e)}"
            )
            messages.error(request, "Failed to update date")


class UpdateUserDetails(forms.Form):
    patient_id = forms.IntegerField(required=True)
    DOB = forms.DateField(required=True)
    sex = forms.CharField(required=True)
    contact = forms.CharField(required=True)
    year = forms.IntegerField(required=True)
    section = forms.CharField(required=True)
    program = forms.CharField(required=True)
    department = forms.CharField(required=True)

    def save(self, request):
        patient_id = self.cleaned_data.get("patient_id")
        DOB = self.cleaned_data.get("DOB")
        sex = self.cleaned_data.get("sex")
        contact = self.cleaned_data.get("contact")
        year = self.cleaned_data.get("year")
        section = self.cleaned_data.get("section")
        program = self.cleaned_data.get("program")
        department = self.cleaned_data.get("department")

        try:
            user = User.objects.get(id=int(patient_id))

            if user:
                department, created = Department.objects.get_or_create(
                    department=department
                )

                if created:
                    Log.objects.create(
                        user=request.user,
                        action=f"{request.user.email} created a new department instance[{department.id}]",
                    )
                    logger.info(
                        f"{request.user.email} created a new department instance[{department.id}]"
                    )

                user.DOB = DOB
                user.sex = sex
                user.contact = contact
                user.year = year
                user.section = section
                user.program = program
                user.department = department

                user.save()

                Log.objects.create(
                    user=request.user,
                    action=f"{request.user.email} updated user information.",
                )
                logger.info(f"{request.user.email} updated user information.")
                messages.success(request, "Successfully updated patient information")

            else:
                logger.info(
                    f"{request.user.email} failed to find patient[{patient_id}]"
                )
                messages.error(
                    request, "Failed to find the correct patient. Please try again"
                )

        except Exception as e:
            logger.info(
                f"{request.user.email} failed to update patient information: {str(e)}"
            )
            messages.error(
                request, "Failed to update patient information. Please try again."
            )


class UpdateUserVital(forms.Form):
    patient_id = forms.IntegerField(required=True)
    blood_type = forms.CharField(required=False)
    height = forms.IntegerField(required=True)
    weight = forms.IntegerField(required=True)

    def save(self, request):
        patient_id = self.cleaned_data.get("patient_id")
        blood_type = self.cleaned_data.get("blood_type")
        height = self.cleaned_data.get("height")
        weight = self.cleaned_data.get("weight")

        try:
            user = User.objects.get(id=int(patient_id))

            if user:
                user.blood_type = blood_type
                user.height = height
                user.weight = weight

                user.save()

                Log.objects.create(
                    user=request.user,
                    action=f"{request.user.email} updated user information.",
                )
                logger.info(f"{request.user.email} updated user information.")
                messages.success(request, "Successfully updated patient information")

            else:
                logger.info(
                    f"{request.user.email} failed to find patient[{patient_id}]"
                )
                messages.error(
                    request, "Failed to find the correct patient. Please try again"
                )

        except Exception as e:
            logger.info(
                f"{request.user.email} failed to update patient information: {str(e)}"
            )
            messages.error(
                request, "Failed to update patient information. Please try again."
            )


class CreateNotesToCase(forms.Form):
    illness_id = forms.IntegerField(required=True)
    message = forms.CharField(required=True)

    def save(self, request):
        illness_id = self.cleaned_data.get("illness_id")
        message = self.cleaned_data.get("message")

        try:
            illness = Illness.objects.get(id=int(illness_id))
        except Exception as e:
            logger.info(f"Failure to find illness: {str(e)}")
            messages.error(request, "Failed to related case.")
            return

        try:
            created_note = IllnessNote.objects.create(
                patient=illness.patient,
                attached_to=illness,
                notes=message,
                noted_by=request.user,
            )
        except Exception as e:
            logger.info(f"Failure to create case note: {str(e)}")
            messages.error(request, "Failed to create case note.")
            return

        Log.objects.create(
            user=request.user, action=f"Created a new case note[{created_note.id}]"
        )
        logger.info(f"Created a new case note[{created_note.id}]")
        messages.success(request, "Successfully sent a case note!")
