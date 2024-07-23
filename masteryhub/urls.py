from django.urls import path
from . import views
from .views import (
    CustomLoginView, CustomLogoutView, expert_dashboard,
    mentee_dashboard, mentor_matching_view, view_profile, view_mentor_profile, 
    edit_profile, forum_list, create_forum_post, view_forum_post, reply_forum_post, 
    book_session, edit_session, home, signup_view, report_concern, list_mentors, search_mentors, become_mentor,
    mentor_help, mentor_rules, request_mentorship, manage_mentorship_requests, 
    accept_mentorship, reject_mentorship, my_mentorships, session_list, view_session,
    create_session, delete_session, create_feedback, forum_posts, pricing
)
from .admin_views import admin_dashboard

urlpatterns = [
    path('', home, name='home'),
    # Authentication
    path('signup/', signup_view, name='account_signup'),
    path('login/', CustomLoginView.as_view(), name='account_login'),
    path('logout/', CustomLogoutView.as_view(), name='account_logout'),
    path('report-concern/', report_concern, name='report_concern'),

    # Admin Dashboard
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),

    # Profile
    path('profile/', view_profile, name='view_own_profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/<str:username>/', view_profile, name='view_profile'),

    # Mentors
    path('mentors/', list_mentors, name='list_mentors'),
    path('mentor/<str:username>/', view_mentor_profile, name='view_mentor_profile'),
    path('search-mentors/', search_mentors, name='search_mentors'),
    path('become-mentor/', become_mentor, name='become_mentor'),
    path('mentor-help/', mentor_help, name='mentor_help'),
    path('mentor-rules/', mentor_rules, name='mentor_rules'),

    # Mentorship
    path('expert-dashboard/', expert_dashboard, name='expert_dashboard'),
    path('mentee-dashboard/', mentee_dashboard, name='mentee_dashboard'),
    path('mentor-matching/', mentor_matching_view, name='mentor_matching'),
    path('request-mentorship/<int:mentor_id>/', request_mentorship, name='request_mentorship'),
    path('manage-mentorship-requests/', manage_mentorship_requests, name='manage_mentorship_requests'),
    path('accept-mentorship/<int:mentorship_id>/', accept_mentorship, name='accept_mentorship'),
    path('reject-mentorship/<int:mentorship_id>/', reject_mentorship, name='reject_mentorship'),
    path('my-mentorships/', my_mentorships, name='my_mentorships'),

    # Sessions
    path('sessions/', session_list, name='session_list'),
    path('sessions/<int:session_id>/', view_session, name='view_session'),
    path('sessions/create/', create_session, name='create_session'),
    path('sessions/<int:session_id>/edit/', edit_session, name='edit_session'),
    path('sessions/<int:session_id>/register/', session_list, name='session_list'),
    path('pricing/', pricing, name='pricing'),
    path('session/<int:session_id>/book/', book_session, name='book_session'),  
    

    # Forums
    path('forums/', forum_list, name='forum_list'),
    path('forums/new/', create_forum_post, name='create_forum_post'),
    path('forums/<int:post_id>/', view_forum_post, name='view_forum_post'),
    path('forums/<int:post_id>/reply/', reply_forum_post, name='reply_forum_post'),
]
