from django.urls import path
from . import views
from .views import CustomLoginView, CustomLogoutView

urlpatterns = [
    path("", views.home, name="masteryhub"),
    path("signup/", views.signup_view, name="account_signup"),
    path("login/", views.CustomLoginView.as_view(), name="account_login"),
    path("logout/", views.CustomLogoutView.as_view(), name="account_logout"),
    path("profile/", views.view_profile, name="view_profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.view_profile, name="view_user_profile"),
    path(
        "mentor/<str:username>/", views.view_mentor_profile, name="view_mentor_profile"
    ),
]
