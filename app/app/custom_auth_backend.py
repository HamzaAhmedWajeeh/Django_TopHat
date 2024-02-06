# # custom_auth_backend.py

# from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth.models import User
# from django.contrib.auth import get_user_model

# class CustomAuthBackend(BaseBackend):
#     def authenticate(self, request, email=None, password=None):
#         try:
#             user = get_user_model().objects.get(email=email)
#             print(user)
#             if user.check_password(password):
#                 return user
#         except User.DoesNotExist:
#             return None

#     def get_user(self, user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None
