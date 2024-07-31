from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from .forms import UserCreationForm
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required(login_url="account_login")
def login_redirect(request):
    if request.user.is_authenticated:
        if request.user.access == 3:
            next_url = reverse("doctor-overview")
        if request.user.access == 4:
            next_url = reverse("admin-overview")
        elif request.user.access == 2:
            next_url = reverse("staff-overview")
        elif request.user.access == 1:
            next_url = reverse("patient-overview")
        else:
            next_url = reverse("home")
        return redirect(next_url)
    return redirect("account_login")


def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)
            messages.success(request, "Sucessful registration")
            return render(request, "users/register.html")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
                    return render(request, "users/register.html")
    return render(request, "users/register.html")


def normal_login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist.")
            return redirect("account_login")

        user = authenticate(request, email=user.email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            # Redirect to the appropriate page after login
            if user.access == 4:
                next_url = "admin-overview"
            if user.access == 3:
                next_url = "doctor-overview"
            if user.access == 2:
                next_url = "staff-overview"
            if user.access == 1:
                next_url = "patient-overview"
            return redirect(next_url)
        else:
            messages.error(request, "Invalid password.")
            return redirect("account_login")


def logout_view(request):
    logout(request)
    return redirect("home")


def google_login_view(request):
    if request.method == "POST":
        if request.user.access == 3:
            next_url = reverse("doctor-overview")
        elif request.user.access == 2:
            next_url = reverse("staff-overview")
        elif request.user.access == 1:
            next_url = reverse("patient-overview")
        else:
            next_url = reverse("home")
        return redirect(f"{reverse('google_login')}?next={next_url}")
    return render(request, "users/google-login.html")


from django.contrib.auth.forms import SetPasswordForm
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from django.http import Http404

User = get_user_model()


class PasswordResetConfirmView(FormView):
    # template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy("password_reset_complete")
    form_class = SetPasswordForm
    token_generator = default_token_generator

    def get_user(self, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        return user

    def dispatch(self, request, *args, **kwargs):
        self.user = self.get_user(kwargs["uidb64"])
        if self.user is not None and self.token_generator.check_token(
            self.user, kwargs["token"]
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404("Invalid token or user does not exist")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
