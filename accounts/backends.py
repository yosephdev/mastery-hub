from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(
                Q(username=username) | Q(email=email)
            )

            if user.check_password(password):
                return user

        except UserModel.DoesNotExist:
            return None

        return None
