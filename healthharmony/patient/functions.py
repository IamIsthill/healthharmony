from allauth.socialaccount.models import SocialAccount
from healthharmony.users.models import User
from django.utils import timezone
from django.contrib import messages


def get_social_picture(user):
    """get picture from the email metadata"""
    try:
        social = SocialAccount.objects.get(user=user, provider="google")
        return social.extra_data.get("picture")
    except SocialAccount.DoesNotExist:
        return None


def calculate_age(DOB):
    """Calculate the age from the date of birth"""
    now = timezone.now()
    if DOB:
        return now.year - DOB.year
    return None


def get_latest_blood_pressure(user):
    """Retrieve the latest blood pressure for the user."""
    latest_bp = user.blood_pressures.first()
    if latest_bp and latest_bp.blood_pressure:
        return latest_bp.blood_pressure
    return None


def update_patient_view_context(request, context):
    """Update the context with the required information"""
    try:
        user = User.objects.prefetch_related("blood_pressures").get(
            email=request.user.email
        )
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return

    context["user"] = user
    context["age"] = calculate_age(user.DOB)
    context["blood_pressure"] = get_latest_blood_pressure(user)

    picture = get_social_picture(user)
    if picture:
        context["picture"] = picture
