from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from .models import User
from allauth.account.forms import SignupForm, LoginForm
from django.core.exceptions import ValidationError
from .validators import validate_dhvsu_email


class UserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model=User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']

    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
class GoogleSignUpForm(SignupForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        validate_dhvsu_email(email)
        return email

class GoogleLoginForm(LoginForm):
    def clean(self):
        super().clean()
        email = self.cleaned_data.get('login')
        try:
            validate_dhvsu_email(email)
        except ValidationError as e:
            self.add_error('login', e)