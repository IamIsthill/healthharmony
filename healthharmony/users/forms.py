from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from healthharmony.users.models import User
from allauth.account.forms import SignupForm, LoginForm
from django import forms
from healthharmony.administrator.models import Log
import logging

# from allauth.socialaccount.models import SocialAccount
import requests
from django.core.files.base import ContentFile
from uuid import uuid4


logger = logging.getLogger("__name__")


class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class CustomSignUpForm(SignupForm):
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")

    # def save(self, request):
    #     user = super(CustomSignUpForm, self).save(request)
    #     user.email = self.cleaned_data["email"]
    #     user.first_name = self.cleaned_data["first_name"]
    #     user.last_name = self.cleaned_data["last_name"]
    #     user.save()

    #     Log.objects.create(
    #         user = request.user,
    #         action = f"New user {user.email} has been created"
    #     )

    #     logger.info(f"New user {user.email} has been created")

    #     # social_account = SocialAccount.objects.get(user=user, provider="google")
    #     # extra_data = social_account.extra_data
    #     # picture_url = extra_data.get("picture")
    #     # print(picture_url)

    #     # if picture_url:
    #     #     response = requests.get(picture_url)
    #     #     if response.status_code == 200:
    #     #         user.profile.save(
    #     #             f"{uuid4()}.jpg", ContentFile(response.content), save=True
    #     #         )

    #     return user


# class GoogleLoginForm(LoginForm):
#     def clean(self):
#         super().clean()
#         email = self.cleaned_data.get("login")
#         return email
