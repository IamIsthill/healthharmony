from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_username
from .models import User

class MySocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):
        user = sociallogin.user
        user_email(user, data.get('email') or '')
        user_username(user, data.get('username') or '')
        user.first_name = data.get('given_name', '')
        user.last_name = data.get('family_name', '')
        return user

    def save_user(self, request, sociallogin, form=None):
        user = super(MySocialAccountAdapter, self).save_user(request, sociallogin, form=form)
        email = sociallogin.account.extra_data.get('email', '')
        user.email = email
        user.email = sociallogin.account.extra_data['email']
        user.first_name = sociallogin.account.extra_data.get('given_name', '')
        user.last_name = sociallogin.account.extra_data.get('family_name', '')
        user.save()
        return user
