from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import (
    Session,
    Profile,
    Category,
    Mentorship,
    Review,
    Forum,
    Mentor,
    Booking,
    ConcernReport,
    Feedback,
    LearningGoal,
    Skill,
)
from checkout.models import Payment

# Register your models here.


@admin.action(description="Mark selected users as mentors")
def make_mentors(modeladmin, request, queryset):
    for user in queryset:
        try:
            profile = Profile.objects.get(user=user)
            profile.is_expert = True
            profile.save()
        except Profile.DoesNotExist:
            messages.error(
                request, f"Profile for user {user.username} does not exist.")
            continue
    messages.success(request, "Selected users have been marked as mentors.")


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

    fieldsets = (
        ('Basic Information', {
            'fields': ('bio', 'skills', 'goals', 'profile_picture')
        }),
        ('Experience & Achievements', {
            'fields': ('experience', 'achievements')
        }),
        ('Social Profiles', {
            'fields': ('linkedin_profile', 'github_profile')
        }),
        ('Mentorship Details', {
            'fields': (
                'is_expert',
                'mentor_since',
                'mentorship_areas',
                'availability',
                'preferred_mentoring_method',
                'is_available'
            )
        }),
    )


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'is_staff', 'get_is_expert')
    list_filter = UserAdmin.list_filter + ('profile__is_expert',)
    actions = [make_mentors]

    def get_is_expert(self, obj):
        return obj.profile.is_expert if hasattr(obj, 'profile') else False
    get_is_expert.short_description = 'Expert Status'
    get_is_expert.boolean = True

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Session)
admin.site.register(Category)
admin.site.register(Mentorship)
admin.site.register(Review)
admin.site.register(Forum)
admin.site.register(Booking)
admin.site.register(ConcernReport)
admin.site.register(Feedback)
admin.site.register(LearningGoal)
admin.site.register(Skill)


@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'is_available')
    search_fields = ('user__username', 'user__email', 'bio')
    list_filter = ('is_available',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
