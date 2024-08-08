from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from checkout.models import Payment
from accounts.models import Profile

# Register your models here.


@admin.action(description="Mark selected users as mentors")
def make_mentors(modeladmin, request, queryset):
    for user in queryset:
        try:
            profile = Profile.objects.get(user=user)
            profile.is_expert = True
            profile.save()
            messages.success(
                request, f"User {user.username} marked as mentor.")
        except Profile.DoesNotExist:
            messages.error(
                request, f"Profile for user {user.username} does not exist.")


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False


class CustomUserAdmin(BaseUserAdmin):
    actions = [make_mentors]
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class LogEntryAdmin(admin.ModelAdmin):
    list_display = (
        "user", "action_time", "content_type", "object_repr", "action_flag")
    list_filter = ("action_time", "content_type", "user")
    search_fields = ("object_repr", "change_message")


admin.site.register(LogEntry, LogEntryAdmin)
admin.site.register(Payment)
