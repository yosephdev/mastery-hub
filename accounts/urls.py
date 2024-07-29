from django.urls import path
from . import views
from .views import (
    CustomLoginView,
    CustomLogoutView,   
    signup_view,
    report_concern,   
)
from .admin_views import admin_dashboard

urlpatterns = [    
   # Authentication
    path("signup/", signup_view, name="account_signup"),
    path("login/", CustomLoginView.as_view(), name="account_login"),
    path("logout/", CustomLogoutView.as_view(), name="account_logout"),   
    # Admin Dashboard
    path("admin/dashboard/", admin_dashboard, name="admin_dashboard"),    
]
