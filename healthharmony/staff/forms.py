# forms.py
from django import forms
from django.contrib import messages
import secrets
import string
import logging

from healthharmony.users.models import User
from healthharmony.inventory.models import QuantityHistory, InventoryDetail
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


class EditQuantityForm(forms.Form):
    item_no = forms.IntegerField(required=False)
    unit = forms.CharField(required=False, max_length=15)
    item_name = forms.CharField(max_length=100, required=True)
    category = forms.CharField(max_length=20, required=False)
    description = forms.CharField(required=False)
    expiration_date = forms.DateField(required=False)
    quantity = forms.IntegerField(required=False)

    # def save(self, request):
