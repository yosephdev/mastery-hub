from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.template.response import TemplateResponse
from django.urls import path
from checkout.models import Payment
from profiles.models import Profile
from masteryhub.models import (
    Session, Category, Mentorship, Review, Forum,
    Feedback, ConcernReport, Skill, Booking, LearningGoal
)

# Register your models here.


class MyAdminSite(admin.AdminSite):
    site_header = 'MasteryHub Administration'
    site_title = 'MasteryHub Admin'
    index_title = 'Dashboard'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.admin_dashboard_view),
                 name='admin_dashboard'),
            path('analytics/', self.admin_view(self.analytics_view), name='analytics'),
        ]
        return custom_urls + urls

    def admin_dashboard_view(self, request):
        context = {
            **self.each_context(request),
            'title': 'Admin Dashboard',
        }
        return TemplateResponse(request, "admin/dashboard.html", context)

    def analytics_view(self, request):
        context = {
            **self.each_context(request),
            'title': 'Analytics Dashboard',
        }
        return TemplateResponse(request, "admin/analytics.html", context)


admin_site = MyAdminSite(name='myadmin')


@admin.action(description="Mark selected users as mentors")
def make_mentors(modeladmin, request, queryset):
    """Action to mark selected users as mentors."""
    success_count = 0
    error_count = 0

    for user in queryset:
        try:
            profile = Profile.objects.get(user=user)
            profile.is_expert = True
            profile.save()
            success_count += 1
        except Profile.DoesNotExist:
            error_count += 1
            messages.error(
                request,
                f"Profile for user {user.username} does not exist."
            )

    if success_count:
        messages.success(
            request,
            f"Successfully marked {success_count} user{'s' if success_count != 1 else ''} as mentor{'s' if success_count != 1 else ''}."
        )


class ProfileInline(admin.StackedInline):
    """Inline admin for Profile model."""
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

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }


@admin.register(User, site=admin_site)
class CustomUserAdmin(BaseUserAdmin):
    """Custom User admin with enhanced features."""
    actions = [make_mentors]
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name',
                    'last_name', 'is_staff', 'is_expert')
    list_filter = ('is_staff', 'is_superuser',
                   'is_active', 'profile__is_expert')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

    def is_expert(self, obj):
        """Custom admin field to show mentor status."""
        try:
            return obj.profile.is_expert
        except Profile.DoesNotExist:
            return False
    is_expert.boolean = True
    is_expert.short_description = 'Mentor Status'

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }


@admin.register(LogEntry, site=admin_site)
class LogEntryAdmin(admin.ModelAdmin):
    """Enhanced Log Entry admin."""
    list_display = (
        'action_time',
        'user',
        'content_type',
        'object_repr',
        'action_flag',
        'change_message'
    )
    list_filter = ('action_time', 'content_type', 'action_flag', 'user')
    search_fields = ('object_repr', 'change_message', 'user__username')
    date_hierarchy = 'action_time'
    readonly_fields = (
        'action_time',
        'user',
        'content_type',
        'object_id',
        'object_repr',
        'action_flag',
        'change_message'
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }


@admin.register(Payment, site=admin_site)
class PaymentAdmin(admin.ModelAdmin):
    """Payment model admin."""
    list_display = ('user', 'amount', 'date', 'session')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'session__title')
    date_hierarchy = 'date'
    readonly_fields = ('date',)

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }


@admin.register(Session, site=admin_site)
class SessionAdmin(admin.ModelAdmin):
    """Session model admin."""
    list_display = ('title', 'get_host', 'status', 'date', 'price')
    list_filter = ('status', 'category', 'date')
    search_fields = ('title', 'host__user__username', 'description')

    def get_host(self, obj):
        return obj.host.user.username
    get_host.short_description = 'Host'


@admin.register(Mentorship, site=admin_site)
class MentorshipAdmin(admin.ModelAdmin):
    """Mentorship model admin."""
    list_display = ('get_mentor', 'get_mentee',
                    'status', 'start_date', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('mentor__user__username', 'mentee__user__username')

    def get_mentor(self, obj):
        return obj.mentor.user.username
    get_mentor.short_description = 'Mentor'

    def get_mentee(self, obj):
        return obj.mentee.user.username
    get_mentee.short_description = 'Mentee'


@admin.register(Review, site=admin_site)
class ReviewAdmin(admin.ModelAdmin):
    """Review model admin."""
    list_display = ('session', 'get_reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer__user__username', 'comment')

    def get_reviewer(self, obj):
        return obj.reviewer.user.username
    get_reviewer.short_description = 'Reviewer'


@admin.register(Forum, site=admin_site)
class ForumAdmin(admin.ModelAdmin):
    """Forum model admin."""
    list_display = ('title', 'get_author', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'content', 'author__user__username')

    def get_author(self, obj):
        return obj.author.user.username
    get_author.short_description = 'Author'


@admin.register(Feedback, site=admin_site)
class FeedbackAdmin(admin.ModelAdmin):
    """Feedback model admin."""
    list_display = ('session', 'get_mentee', 'get_mentor', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('mentee__user__username',
                     'mentor__user__username', 'comment')

    def get_mentee(self, obj):
        return obj.mentee.user.username
    get_mentee.short_description = 'Mentee'

    def get_mentor(self, obj):
        return obj.mentor.user.username
    get_mentor.short_description = 'Mentor'


@admin.register(ConcernReport, site=admin_site)
class ConcernReportAdmin(admin.ModelAdmin):
    """ConcernReport model admin."""
    list_display = ('category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('description',)


@admin.register(Skill, site=admin_site)
class SkillAdmin(admin.ModelAdmin):
    """Skill model admin."""
    list_display = ('name', 'title', 'category', 'price', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'title', 'description')


@admin.register(Booking, site=admin_site)
class BookingAdmin(admin.ModelAdmin):
    """Booking model admin."""
    list_display = ('get_user', 'skill', 'booking_date', 'status')
    list_filter = ('status', 'booking_date')
    search_fields = ('user__username', 'skill__title')

    def get_user(self, obj):
        return obj.user.username
    get_user.short_description = 'User'


@admin.register(LearningGoal, site=admin_site)
class LearningGoalAdmin(admin.ModelAdmin):
    """LearningGoal model admin."""
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'description')


@admin.register(Category, site=admin_site)
class CategoryAdmin(admin.ModelAdmin):
    """Category model admin."""
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


admin.site = admin_site
admin.site.site_header = 'MasteryHub Administration'
admin.site.site_title = 'MasteryHub Admin'
admin.site.index_title = 'Dashboard'
