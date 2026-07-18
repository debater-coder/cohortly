from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.forms import ValidationError
from django.http import HttpRequest


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request: HttpRequest, sociallogin: SocialLogin) -> None:
        if request.user.is_authenticated:
            connected_accounts = request.user.socialaccount_set.all()
            if connected_accounts.exists():
                raise ValidationError("You can only link one social account.")
