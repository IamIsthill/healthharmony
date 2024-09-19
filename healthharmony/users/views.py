from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from .forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.backends import ModelBackend
import logging

from healthharmony.administrator.models import Log
from healthharmony.patient.functions import get_social_picture
from healthharmony.patient.forms import UpdateProfileInfo


logger = logging.getLogger(__name__)


@login_required(login_url="account_login")
def user_profile(request):
    picture = get_social_picture(request.user)
    context = {"picture": picture}
    if request.method == "POST":
        form = UpdateProfileInfo(request.POST, files=request.FILES)
        if form.is_valid():
            try:
                user = form.save(request, request.user.id)
                messages.success(request, "Profile updated successfully!")
                context.update({"user": user})
                return redirect("patient-profile", request.user.id)
            except ValueError as e:
                messages.error(request, str(e))
    return render(request, "profile.html", context)


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
    """
    Handles user login based on email and password. Authenticates the user and logs the login attempt.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the appropriate page based on user access level.
    """
    if request.method.lower() == "post":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect("account_login")

        user = get_user(request, email, password)

        if user is not None:
            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)
            if "email" not in request.session:
                request.session["email"] = request.user.email
            create_log_user(user)
            messages.success(request, "Login successful!")

            # Redirect based on user access level
            if user.access == 4:
                next_url = "admin-overview"
            elif user.access == 3:
                next_url = "doctor-overview"
            elif user.access == 2:
                next_url = "staff-overview"
            elif user.access == 1:
                next_url = "patient-overview"
            else:
                next_url = "home"  # Default fallback

            return redirect(next_url)
        else:
            messages.error(request, "Invalid password.")
            return redirect("account_login")


def logout_view(request):
    """
    Logs out the user, creates a log entry, and redirects to the home page.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponseRedirect: Redirects to the home page after logout.
    """
    try:
        Log.objects.create(user=request.user, action="User has logged out")
    except Exception as e:
        # Log the error if logging fails
        logger.error("Failed to create log entry for logout: %s", str(e))
    request.session.pop("email", None)
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


def create_log_user(user):
    try:
        Log.objects.create(user=user, action="User has logged in")
    except Exception as e:
        logger.error("Failed to create log entry for login: %s", str(e))
        return redirect("account_login")


def get_user(request, email, password):
    try:
        user = User.objects.get(email=email)
        user = authenticate(
            request, email=user.email, password=password, backend=ModelBackend
        )
        return user
    except User.DoesNotExist:
        messages.error(request, "User with this email does not exist.")
        return None

    # user = authenticate(request, email=user.email, password=password)


from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = "users/password_reset.html"
    email_template_name = "users/password_reset_email.html"
    subject_template_name = "users/password_reset_subject.txt"
    success_message = (
        "We've emailed you instructions for setting your password, "
        "if an account exists with the email you entered. You should receive them shortly."
        " If you don't receive an email, "
        "please make sure you've entered the address you registered with, and check your spam folder."
    )
    success_url = reverse_lazy("login-redirect")
