# forms.py
from django import forms
from django.contrib import messages
import secrets
import string
import logging
from django.db.models import Sum

from healthharmony.users.models import User, Department
from healthharmony.models.bed.models import Ambulansya, WheelChair
from healthharmony.models.inventory.models import QuantityHistory, InventoryDetail
from healthharmony.administrator.models import Log

logger = logging.getLogger(__name__)


# Create your views here.
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for i in range(length))


class PatientForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ["password", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        # Generate a random password
        random_password = generate_password()
        user.set_password(random_password)
        if commit:
            user.save()
        return user


class AddInventoryForm(forms.Form):
    item_no = forms.IntegerField(required=False)
    unit = forms.CharField(required=False, max_length=15)
    item_name = forms.CharField(max_length=100, required=True)
    category = forms.CharField(max_length=20, required=False)
    description = forms.CharField(required=False)
    expiration_date = forms.DateField(required=False)
    quantity = forms.IntegerField(required=False)

    def save(self, request):
        try:
            # Extract cleaned data
            expiration_date = self.cleaned_data.get("expiration_date")
            quantity = self.cleaned_data.get("quantity")
            category = self.cleaned_data.get("category")

            # Create InventoryDetail object
            item = InventoryDetail.objects.create(
                added_by=request.user,
                item_no=self.cleaned_data.get("item_no"),
                item_name=self.cleaned_data.get("item_name"),
                unit=self.cleaned_data.get("unit"),
                category=category if category else None,
                description=self.cleaned_data.get("description"),
                expiration_date=expiration_date if expiration_date else None,
            )

            # Log inventory addition
            Log.objects.create(
                user=request.user,
                action=f"Successfully added new inventory record[id:{item.id}]",
            )
            logger.info(f"Successfully added new inventory record[id:{item.id}]")

            # Create QuantityHistory if quantity is provided
            if quantity:
                item_quantity = QuantityHistory.objects.create(
                    inventory=item,  # Assuming QuantityHistory has a ForeignKey to InventoryDetail
                    changed_by=request.user,
                    updated_quantity=quantity,
                )

                # Log quantity history addition
                Log.objects.create(
                    user=request.user,
                    action=f"Successfully added new quantity history record[id:{item_quantity.id}]",
                )
                logger.info(
                    f"Successfully added new quantity history record[id:{item_quantity.id}]"
                )

            messages.success(request, "New inventory item was added successfully.")

        except Exception as e:
            logger.error(f"Failed to add a new inventory record: {str(e)}")
            messages.error(request, "Failed to add a new inventory record.")


class EditInventoryForm(forms.Form):
    item_name = forms.CharField(required=True)
    quantity = forms.IntegerField(required=False)
    item_no = forms.IntegerField(required=False)
    unit = forms.CharField(required=False)
    category = forms.CharField(required=False)
    expiration_date = forms.DateField(required=False)
    description = forms.CharField(required=False)

    def save(self, request, pk):
        try:
            pk = int(pk)
            # Get inventory item
            inventory_item = InventoryDetail.objects.get(id=pk)

            # Get related quantity of the fetched inventory item
            quantities_sum = inventory_item.quantities.aggregate(
                total_quantity=Sum("updated_quantity")
            )

            # Reassign the total quantity
            total_quantity = (
                quantities_sum["total_quantity"]
                if quantities_sum["total_quantity"] is not None
                else 0
            )

            # Get form data
            expiration_date = self.cleaned_data.get("expiration_date")
            quantity = self.cleaned_data.get("quantity")
            category = self.cleaned_data.get("category")

            inventory_item.expiration_date = (
                expiration_date if expiration_date else None
            )
            inventory_item.item_no = self.cleaned_data.get("item_no")
            inventory_item.unit = self.cleaned_data.get("unit")
            inventory_item.item_name = self.cleaned_data.get("item_name")
            inventory_item.category = category if category else None
            inventory_item.description = self.cleaned_data.get("description")
            if total_quantity != quantity:
                # Get the difference between total and posted quantity
                quantity = quantity if quantity else 0
                diff_quantity = 0
                if total_quantity > quantity:
                    diff_quantity = -(total_quantity - quantity)
                else:
                    diff_quantity = quantity - total_quantity
                item_quantity = QuantityHistory.objects.create(
                    inventory=inventory_item,
                    changed_by=request.user,
                    updated_quantity=diff_quantity,
                )
                Log.objects.create(
                    user=request.user,
                    action=f"Successfully updated quantity history record[id:{item_quantity.id}]",
                )
                logger.info(
                    f"Successfully updated quantity history record[id:{item_quantity.id}]"
                )
            inventory_item.full_clean()
            inventory_item.save()

            Log.objects.create(
                user=request.user,
                action=f"Successfully updated inventory record[id:{inventory_item.id}]",
            )
            logger.info(
                f"Successfully updated inventory record[id:{inventory_item.id}]"
            )
        except Exception as e:
            messages.error(
                request, "Failed to update inventory record. Please try again"
            )
            logger.error(f"Failed to update inventory record: {str(e)}")


class DeleteInventoryForm(forms.Form):
    def save(self, request, pk):
        try:
            pk = int(pk)
            item = InventoryDetail.objects.get(id=pk)
            old_item = item
            item.delete()
            messages.success(
                request, f"Successfully deleted inventory item {old_item.item_name}"
            )
            Log.objects.create(
                user=request.user,
                action=f"Successfully deleted inventory record[id:{old_item.id}]",
            )
        except Exception as e:
            messages.error(
                request, "Failed to delete inventory record. Please try again"
            )
            logger.error(f"Failed to delete inventory record: {str(e)}")


class DeleteDepartmentForm(forms.Form):
    def save(self, request, pk):
        try:
            department = Department.objects.get(id=int(pk))
            if department:
                department.delete()
                messages.success(
                    request, f"Success! {department.department} has been removed."
                )
                Log.objects.create(
                    user=request.user,
                    action=f"Deleted department instance[id:{department.id}]",
                )
                logger.info(
                    f"{request.user.email} has deleted department instance[id={department.id}]"
                )
            else:
                messages.error(request, "Failed to find department. Please try again")
                logger.error("Failed to find deparment instance")
        except Exception as e:
            messages.error(request, "Failed to delete department. Please try again")
            logger.error(f"Failed to delete department instance: {str(e)}")


class EditDepartmentForm(forms.Form):
    department_name = forms.CharField(required=True)

    def save(self, request, pk):
        try:
            department = Department.objects.get(id=int(pk))
            if department:
                department.department = self.cleaned_data.get("department_name")
                department.full_clean()
                department.save()
                messages.success(request, "Success! Department name has been updated")
                logger.info(
                    f"{request.user.email} has updated department instance[id:{department.id}]"
                )
                Log.objects.create(
                    user=request.user,
                    action=f"{request.user.email} has updated the department name of instance[id:{department.id}]",
                )
            else:
                messages.error(request, "Failed to update. Department not found")
                logger.info(f"{request.user.email} failed to find department instance")
        except Exception as e:
            messages.error("Failed to update department")
            logger.info(
                f"{request.user.email} faield to update department instance: {str(e)}"
            )


class CreateUpdateAmbulance(forms.Form):
    ambulance = forms.CharField(required=True)

    def save(self, request):
        status = self.cleaned_data.get("ambulance")

        # Set status to TRUE if 'available' else to FALSE if not
        status = True if status == "available" else False

        # Get all ambulance instance and delete them
        try:
            ambulances = Ambulansya.objects.all()
            for ambulance in ambulances:
                ambulance.delete()
        except Exception as e:
            logger.info(f"Failed to fetch ambulances and delete them: {str(e)}")
            messages.error(
                request, "System faced an unexpected issue. Please reload page."
            )

        # Create the ambulance instance
        try:
            ambulance = Ambulansya.objects.create(
                is_avail=status  # The status set earlier
            )

            # Log and inform user
            Log.objects.create(
                user=request.user,
                action=f"Updated ambulance instance[{str(ambulance.id)}]",
            )
            messages.success(request, "Successfully updated ambulance availability!")
        except Exception as e:
            logger.info(f"Failed to create ambulance instance: {str(e)}")
            messages.error(
                request, "System faced an unexpected issue. Please reload page."
            )


class CreateWheelChairQuantity(forms.Form):
    avail = forms.IntegerField(required=False)
    unavail = forms.IntegerField(required=False)

    def save(self, request):
        # Fetch data from form
        avail_wheelchair = self.cleaned_data.get("avail")
        not_avail_wheelchair = self.cleaned_data.get("unavail")

        # Create the wheelchaur
        try:
            logger.warning(f"{avail_wheelchair} {not_avail_wheelchair}")
            if avail_wheelchair != 0:
                avail_wheelchair_instance = WheelChair.objects.create(
                    is_avail=True,
                    quantity=avail_wheelchair or 0,
                    created_by=request.user,
                )

                Log.objects.create(
                    user=request.user,
                    action=f"Created available wheelchairs[{str(avail_wheelchair_instance.id)}]",
                )
                logger.info(
                    f"{request.user} created available wheelchairs[{str(avail_wheelchair_instance.id)}]"
                )

            if not_avail_wheelchair != 0:
                not_avail_wheelchair_instance = WheelChair.objects.create(
                    is_avail=False,
                    quantity=not_avail_wheelchair or 0,
                    created_by=request.user,
                )

                Log.objects.create(
                    user=request.user,
                    action=f"Created unavailable wheelchairs[{str(not_avail_wheelchair_instance.id)}]",
                )
                logger.info(
                    f"{request.user} created unavailable wheelchairs[{str(not_avail_wheelchair_instance.id)}]"
                )

            messages.success(request, "Successfully updated wheelchair availability!")

        except Exception as e:
            messages.error(
                request, "System faced an unexpected issue. Please reload page."
            )
            logger.info(f"Failed to create new wheelchair instance: {str(e)}")
