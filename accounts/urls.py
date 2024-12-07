from django.urls import path
from . import views
from . import admin_views
from django.contrib.auth import views as auth_views
from .views import (
    CustomConfirmEmailView,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView
)

app_name = 'accounts'

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("admin/dashboard/", admin_views.admin_dashboard, name="admin_dashboard"),
    path('password/change/',
         auth_views.PasswordChangeView.as_view(
             template_name='account/password_change.html'),
         name='password_change'),
    path('password/change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='account/password_change_done.html'),
         name='password_change_done'),
    path('password/reset/',
         CustomPasswordResetView.as_view(),
         name='password_reset'),
    path('password/reset/done/',
         CustomPasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/',
         CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password/reset/complete/',
         CustomPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('confirm-email/<str:key>/',
         CustomConfirmEmailView.as_view(),
         name='account_confirm_email'),
]
