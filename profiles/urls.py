from django.urls import path
from . import views
from masteryhub.views import view_mentor_profile

app_name = 'profiles'

urlpatterns = [
    # List all profiles
    path('profiles/', views.view_profiles, name='view_profiles'),

    # View/edit/delete own profile
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('profile/delete/<int:user_id>/', views.delete_profile, name='delete_profile_with_id'),

    # View specific profiles
    path('profile/<str:username>/', views.view_profile, name='view_profile'),
    path('mentor/<str:username>/', view_mentor_profile,
         name='view_mentor_profile'),
]
