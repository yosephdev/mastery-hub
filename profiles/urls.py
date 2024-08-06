from django.urls import path
from .views import view_profile, view_mentor_profile, edit_profile

urlpatterns = [
    path("profile/", view_profile, name="view_own_profile"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path("profile/<str:username>/", view_profile, name="view_profile"),
    path("mentor/<str:username>/", view_mentor_profile, name="view_mentor_profile"),
]
