from typing import override

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.forms import ValidationError
from django.http import HttpRequest


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Django Allauth adapter that prevents more than one connected SBHS account."""

    def pre_social_login(self, request: HttpRequest, sociallogin: SocialLogin) -> None:
        if request.user.is_authenticated:
            connected_accounts = request.user.socialaccount_set.all()
            if connected_accounts.exists():
                raise ValidationError("You can only link one social account.")

    def is_open_for_signup(self, request: HttpRequest, sociallogin: SocialLogin):
        return True


class NoNewLocalUserAdapter(DefaultAccountAdapter):
    """Django Allauth adapter that prevents creation of new local users."""

    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return False
