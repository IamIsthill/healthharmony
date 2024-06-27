from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_dhvsu_email(value):
    if not value.endswith('@dhvsu.edu.ph'):
        raise ValidationError(
            _('Email address must end with @dhvsu.edu.ph'),
            params={'value': value},
        )
