from django.shortcuts import render, redirect
from django.contrib.auth import authenticate,login, logout
from django.contrib import messages
from .forms import UserCreationForm

# Create your views here.
def register_view(request):
    if request.method == "POST":
        form =UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Sucessful registration')
            return render(request, 'users/register.html')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
                    return render(request, 'users/register.html')


    return render(request, 'users/register.html')

def login_view(request):
    return render(request, 'users/login.html')
