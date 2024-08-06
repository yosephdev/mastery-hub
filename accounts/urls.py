from django.urls import path
from allauth.account.views import SignupView
from . import views
from . import admin_views
from .views import (
    CustomLoginView,
    CustomLogoutView,
    signup_view,
    CustomConfirmEmailView,
)

urlpatterns = [
    # Authentication
    path("accounts/signup/", SignupView.as_view(), name="account_signup"),
    path("login/", CustomLoginView.as_view(), name="account_login"),
    path("logout/", CustomLogoutView.as_view(), name="account_logout"),
    path(
        "confirm-email/<str:key>/",
        CustomConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
    # Admin Dashboard
    path("admin/dashboard/", admin_views.admin_dashboard, name="admin_dashboard"),
]
