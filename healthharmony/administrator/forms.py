from healthharmony.users.models import User, Department
from healthharmony.administrator.models import Log
from django.core.mail import EmailMessage

from django import forms
from django.contrib import messages
import logging

from healthharmony.staff.views import generate_password
from healthharmony.app.settings import env


logger = logging.getLogger("administrator")


class AdminUserCreationForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)
    access = forms.CharField(required=False)
    department = forms.CharField(required=False)

    def save(self, request):
        try:
            department_name = self.cleaned_data["department"]
            first_name = self.cleaned_data["first_name"]
            last_name = self.cleaned_data["last_name"]
            email = self.cleaned_data["email"]
            access = self.cleaned_data["access"]

            user, created = User.objects.get_or_create(email=email)

            if not created:
                logger.info(
                    f"{request.user.email} tried creating a new account with an already existing email"
                )
                messages.error(request, f"User with email[{email}] already exists.")
                return

            department, created = Department.objects.get_or_create(
                department=department_name
            )
            if created:
                Log.objects.create(
                    user=request.user, action="Created a new department instance"
                )

            user.first_name = first_name
            user.last_name = last_name
            user.access = access
            user.department = department

            password = generate_password()
            user.set_password(password)
            user.save()

            subject = "Welcome to HealthHarmony!"
            body = f"<h1>This is your password {password}</h1><p>With HTML content</p>"
            from_email = env("EMAIL_ADD")
            recipient_list = [user.email]
            email = EmailMessage(subject, body, from_email, recipient_list)
            email.content_subtype = "html"
            email.send()

            user.save()

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
