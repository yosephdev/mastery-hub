from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from profiles.models import Profile
from masteryhub.models import Session

# Register your models here.


@staff_member_required
def admin_dashboard(request):
    try:
        last_30_days = timezone.now() - timedelta(days=30)

        context = {
            "title": "MasteryHub Admin Dashboard",
            "subtitle": "Welcome to the Admin Dashboard",
            "latest_users": User.objects.filter(
                is_staff=False,
                is_active=True
            ).order_by("-date_joined")[:5],
            "total_users": User.objects.filter(is_active=True).count(),
            "total_mentors": Profile.objects.filter(is_expert=True, user__is_active=True).count(),
            "total_sessions": Session.objects.count(),
            "active_sessions": Session.objects.filter(
                created_at__gte=last_30_days
            ).count(),
            "new_users_month": User.objects.filter(
                date_joined__gte=last_30_days,
                is_active=True
            ).count(),
        }
        return render(request, "admin/dashboard.html", context)
    except Exception as e:
        print(f"Error in admin_dashboard: {str(e)}")
        context = {
            "title": "MasteryHub Admin Dashboard",
            "subtitle": "Error loading dashboard data",
            "error": "Unable to load dashboard data. Please try again later."
        }
        return render(request, "admin/dashboard.html", context)
