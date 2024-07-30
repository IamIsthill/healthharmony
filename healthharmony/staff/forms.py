# forms.py
from django import forms
from healthharmony.users.models import User
from healthharmony.users.forms import UserCreationForm
import secrets
import string

# Create your views here.
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for i in range(length))

class PatientForm(forms.ModelForm):
    class Meta:
        model = User
        exclude = ['password', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        # Generate a random password
        random_password = generate_password()
        user.set_password(random_password)
        if commit:
            user.save()
        return user
  
