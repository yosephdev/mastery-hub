from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.models import LogEntry
from .models import Session, Profile, Category, Mentorship, Review, Payment, Forum

# Register your models here.

@admin.action(description='Mark selected users as mentors')
def make_mentors(modeladmin, request, queryset):
    for user in queryset:
        try:
            profile = Profile.objects.get(user=user)
            profile.is_expert = True
            profile.save()
        except Profile.DoesNotExist:
            messages.error(request, f"Profile for user {user.username} does not exist.")
            continue
    messages.success(request, "Selected users have been marked as mentors.")

class CustomUserAdmin(UserAdmin):
    actions = [make_mentors]

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("user", "action_time", "content_type", "object_repr", "action_flag")
    list_filter = ("action_time", "content_type", "user")
    search_fields = ("object_repr", "change_message")

admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(Session)
admin.site.register(Profile)
admin.site.register(Category)
admin.site.register(Mentorship)
admin.site.register(Review)
admin.site.register(Payment)
admin.site.register(Forum)
