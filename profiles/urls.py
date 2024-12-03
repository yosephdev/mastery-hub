from django.urls import path
from .views import view_profile, view_profiles, view_mentor_profile, edit_profile, delete_profile
from masteryhub.views import list_mentors

app_name = 'profiles'

urlpatterns = [
    path("profiles/", view_profiles, name="view_profiles"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path("profile/<str:username>/", view_profile, name="view_profile"),
    path("profile/delete/<int:user_id>/",
         delete_profile, name="delete_profile"),
    path("mentor/<str:username>/", view_mentor_profile,
         name="view_mentor_profile"),
    path('masteryhub/mentors/', list_mentors, name='list_mentors'),
]
