from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from .models import Profile

class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            profile = Profile.objects.get(phone_number=username)
            user = profile.user
            if user.check_password(password):
                return user
        except Profile.DoesNotExist:
            return None
        return None