from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from .models import User
from allauth.account.forms import SignupForm, LoginForm
from django.core.exceptions import ValidationError
from django import forms


class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model=User
        fields = ['email', 'password1', 'password2']

    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    

class GoogleSignUpForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')

    def save(self, request):
        user = super(GoogleSignUpForm, self).save(request)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user

    
class GoogleLoginForm(LoginForm):
    def clean(self):
        super().clean()
        email = self.cleaned_data.get('login')
        return email