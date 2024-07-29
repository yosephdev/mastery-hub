from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required


# Register your models here.


@staff_member_required
def admin_dashboard(request):
    context = {
        "title": "MasteryHub Admin Dashboard",
        "subtitle": "Welcome to the Admin Dashboard",
        "latest_users": User.objects.filter(is_staff=False).order_by("-date_joined")[
            :5
        ],
        "total_users": User.objects.count(),
    }
    return render(request, "admin/dashboard.html", context)
