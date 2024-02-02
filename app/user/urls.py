"""
URLs Mappings for the User API
"""
from django.urls import path

from user import views

app_name = 'user'

urlpatterns = [
    path(
        'create/',
        views.CreateUserView.as_view(),
        name='create'
        ),
    path(
        'create-admin/',
        views.CreateAdminUserView.as_view(),
        name='create-admin'
    ),
    # path(
    #     'verify/<str:token>/',
    #     views.UserVerificationView.as_view(),
    #     name='verify'
    #     ),
    path(
        'token/',
        views.CreateTokenView.as_view(),
        name='token'
        ),
    path(
        'me/',
        views.ManageUserView.as_view(),
        name='me'
        ),
    # path(
    #     'password-reset/',
    #     views.UserResetPassword.as_view(),
    #     name='password_reset'
    #     ),
    # path(
    #     'password-reset-confirm/',
    #     views.UserResetPasswordConfirm.as_view(),
    #     name='password_reset'
    #     ),
]
