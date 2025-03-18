from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from allauth.account.utils import perform_login
from allauth.exceptions import ImmediateHttpResponse
import logging
from profiles.models import Profile

logger = logging.getLogger(__name__)

class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter for accounts that handles redirects and messages.
    """
    
    def get_login_redirect_url(self, request):
        """
        Override the default redirect URL after login.
        """
        return reverse('home:index')
    
    def get_signup_redirect_url(self, request):
        """
        Override the default redirect URL after signup.
        """
        return reverse('home:index')
    
    def is_open_for_signup(self, request):
        """
        Whether registration is allowed.
        """
        return True
    
    def is_email_verification_mandatory(self, request):
        """
        Skip email verification for social accounts.
        """
        if hasattr(request, 'session') and request.session.get('sociallogin_provider'):
            return False
        return True
    
    def render_mail(self, template_prefix, email, context):
        """
        Override to ensure proper site name and domain in emails.
        """
        context['current_site'] = {
            'name': 'MasteryHub',
            'domain': context.get('current_site', {}).get('domain', 'skill-sharing-446c0336ffb5.herokuapp.com')
        }
        return super().render_mail(template_prefix, email, context)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social accounts that handles profile creation and redirects.
    """
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user information from social provider info.
        """
        user = super().populate_user(request, sociallogin, data)
        if sociallogin.account.provider == 'google':
            user.email = sociallogin.account.extra_data.get('email', '')
            user.first_name = sociallogin.account.extra_data.get('given_name', '')
            user.last_name = sociallogin.account.extra_data.get('family_name', '')
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save the user and create their profile.
        """
        user = super().save_user(request, sociallogin, form)
        try:
            # Create profile for social account user
            Profile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': f"{user.first_name} {user.last_name}".strip(),
                    'bio': '',
                    'country': '',
                    'is_mentor': False
                }
            )
            logger.info(f"Profile created for social account user: {user.email}")
        except Exception as e:
            logger.error(f"Error creating profile for social account user: {str(e)}")
        return user
    
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Enable auto signup for social accounts.
        """
        return True
    
    def get_connect_redirect_url(self, request, socialaccount):
        """
        Return the URL to redirect to after successfully connecting a social account.
        """
        return reverse('home:index') 