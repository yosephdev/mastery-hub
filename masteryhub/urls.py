from django.urls import path

from . import views
from .views import CustomLoginView, CustomLogoutView
from .admin_views import admin_dashboard


urlpatterns = [
    # Home and Authentication
    path("", views.home, name="home"),
    path("signup/", views.signup_view, name="account_signup"),
    path("login/", CustomLoginView.as_view(), name="account_login"),
    path("logout/", CustomLogoutView.as_view(), name="account_logout"),
    # Admin Dashboard
    path("admin/dashboard/", admin_dashboard, name="admin_dashboard"),
    # Profile URLs
    path("profile/", views.view_profile, name="view_own_profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("profile/<str:username>/", views.view_profile, name="view_profile"),
    # Mentor URLs
    path("mentors/", views.list_mentors, name="list_mentors"),
    path(
        "mentor/<str:username>/", views.view_mentor_profile, name="view_mentor_profile"
    ),
    path("search-mentors/", views.search_mentors, name="search_mentors"),
    # Mentorship URLs
    path(
        "request-mentorship/<int:mentor_id>/",
        views.request_mentorship,
        name="request_mentorship",
    ),
    path(
        "manage-mentorship-requests/",
        views.manage_mentorship_requests,
        name="manage_mentorship_requests",
    ),
    path(
        "accept-mentorship/<int:mentorship_id>/",
        views.accept_mentorship,
        name="accept_mentorship",
    ),
    path(
        "reject-mentorship/<int:mentorship_id>/",
        views.reject_mentorship,
        name="reject_mentorship",
    ),
    path("my-mentorships/", views.my_mentorships, name="my_mentorships"),
    # Session URLs
    path("sessions/", views.list_sessions, name="list_sessions"),
    path("session/<int:session_id>/", views.view_session, name="view_session"),
    path("session/create/", views.create_session, name="create_session"),
    path("session/<int:session_id>/edit/", views.edit_session, name="edit_session"),
    # Forum URLs
    path("forum/", views.forum_list, name="forum_list"),
    path("forum/create/", views.create_forum_post, name="create_forum_post"),
    path("forum/<int:post_id>/", views.view_forum_post, name="view_forum_post"),
    path("forum/<int:post_id>/reply/", views.reply_forum_post, name="reply_forum_post"),
]
