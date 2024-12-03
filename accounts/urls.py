from django.urls import path
from allauth.account.views import SignupView
from . import admin_views
from .views import (
    CustomLoginView,
    CustomLogoutView,
    CustomConfirmEmailView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
)

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path(
        "confirm-email/<str:key>/",
        CustomConfirmEmailView.as_view(),
        name="confirm_email",
    ),

    # Password Reset
    path("password/reset/",
         CustomPasswordResetView.as_view(),
         name="reset_password"),
    path("password/reset/done/",
         CustomPasswordResetDoneView.as_view(),
         name="reset_password_done"),
    path("password/reset/key/<uidb64>/<token>/",
         CustomPasswordResetConfirmView.as_view(),
         name="reset_password_confirm"),
    path("password/reset/complete/",
         CustomPasswordResetCompleteView.as_view(),
         name="reset_password_complete"),

    # Admin Dashboard
    path("admin/dashboard/",
         admin_views.admin_dashboard,
         name="admin_dashboard"),
]
