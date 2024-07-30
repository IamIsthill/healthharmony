from healthharmony.users.models import User, Department
from healthharmony.administrator.models import Log

from django import forms
from django.contrib import messages
import logging


logger = logging.getLogger("administrator")


class AdminUserCreationForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=False)
    access = forms.CharField(max_length=30, required=False)
    department = forms.CharField(max_length=100, required=False)

    def save(self, request):
        try:
            department_name = self.cleaned_data["department"]
            first_name = self.cleaned_data["first_name"]
            last_name = self.cleaned_data["last_name"]
            email = self.cleaned_data["email"]
            access = self.cleaned_data["access"]

            department, created = Department.objects.get_or_create(
                department=department_name
            )
            if created:
                Log.objects.create(
                    user=request.user, action="Created a new department instance"
                )

            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                access=access,
                department=department,
            )
            messages.success(request, "User created successfully.")
        except ValueError as ve:
            messages.error(request, f"Input error: {ve}")
            logger.error(f"Input error: {ve}")
        except Department.DoesNotExist:
            messages.error(request, "Department does not exist.")
            logger.error("Department does not exist.")
        except User.DoesNotExist:
            messages.error(request, "User creation failed due to a related error.")
            logger.error("User creation failed due to a related error.")
        except Exception as e:
            messages.error(request, "System failed to create a new user.")
            logger.error(f"Unexpected error: {e}")

        return user
