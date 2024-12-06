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
from django.contrib.auth import views as auth_views

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
         name="password_reset"),
    path("password/reset/done/",
         CustomPasswordResetDoneView.as_view(),
         name="password_reset_done"),
    path("password/reset/<uidb64>/<token>/",
         CustomPasswordResetConfirmView.as_view(),
         name="password_reset_confirm"),
    path("password/reset/complete/",
         CustomPasswordResetCompleteView.as_view(),
         name="password_reset_complete"),

    # Admin Dashboard
    path("admin/dashboard/",
         admin_views.admin_dashboard,
         name="admin_dashboard"),

    # Password Change
    path('password/change/', 
         auth_views.PasswordChangeView.as_view(template_name='account/password_change.html'),
         name='password_change'),
    path('password/change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='account/password_change_done.html'),
         name='password_change_done'),
]
