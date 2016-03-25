#coding: utf-8
from .models import FtpUser

class CustomBackEnd:
    def authenticate(self,email=None,password=None):
        try:
            user = FtpUser.objects.get(Email=email)
        except FtpUser.DoesNotExist:
            pass
        else:
            if user.check_password(password):
                return user
        return None

    def get_user(self,email):
        try:
            return FtpUser.objects.get(Email=email)
        except FtpUser.DoesNotExist:
            return None
