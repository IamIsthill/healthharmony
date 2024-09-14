from django import forms
from healthharmony.administrator.models import Log
from healthharmony.users.models import User
from healthharmony.models.treatment.models import Certificate
import logging
from django.contrib import messages


logger = logging.getLogger(__name__)


class UpdateProfileInfo(forms.Form):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    contact = forms.IntegerField(required=False)
    year = forms.IntegerField(max_value=5, required=False)
    section = forms.CharField(max_length=10, required=False)
    program = forms.CharField(max_length=50, required=False)
    sex = forms.CharField(max_length=10, required=False)
    DOB = forms.DateField(required=False)

    def save(self, request, pk):

        try:
            user = User.objects.get(id=int(pk))
            user.first_name = self.cleaned_data.get("first_name", user.first_name)
            user.last_name = self.cleaned_data.get("last_name", user.last_name)
            user.contact = self.cleaned_data.get("contact", user.contact)
            user.year = self.cleaned_data.get("year", user.year)
            user.section = self.cleaned_data.get("section", user.section)
            user.program = self.cleaned_data.get("program", user.program)
            user.sex = self.cleaned_data.get("sex", user.sex)
            user.DOB = self.cleaned_data.get("DOB", user.DOB)

            # Handle profile image upload
            if "profile" in request.FILES:
                user.profile = request.FILES["profile"]

            # Save the updated user
            user.save()

            # Log the update
            Log.objects.create(user=user, action="Updated profile information")
            logger.info(f"{request.user.email} successfully updated patient profile")
        except Exception as e:
            # Handle any errors that occur during the save process
            logger.warning(
                f"{request.user.email} failed to update patient profile: {str(e)}"
            )

            raise ValueError(f"Failed to update profile: {e}")

        return user


class CreateCertificateForm(forms.Form):
    purpose = forms.CharField(max_length=500)

    def save(self, request):
        patient = request.user
        purpose = self.cleaned_data.get("purpose")

        try:

            medcert = Certificate.objects.create(patient=patient, purpose=purpose)

            Log.objects.create(
                user=patient,
                action=f"{request.user.email} issued a medical certificate request[{medcert.id}]",
            )

            logger.info(
                f"{request.user.email} has issued a new medical certificate request[{medcert.id}]"
            )
            messages.success(request, "Successfully issued a request!")

        except Exception as e:
            logger.warning(
                f"{request.user.email} failed to create medical certificate request: {(e)}"
            )
            messages.error(request, "Failed to issue the request. Please try again")
