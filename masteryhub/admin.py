from django.contrib import admin
from .models import Session, Profile, Category, Mentorship, Review, Payment, Forum
from django.contrib.admin.models import LogEntry

# Register your models here.


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
