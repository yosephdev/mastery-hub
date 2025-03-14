from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from django.contrib import messages
from django.urls import reverse
import logging

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


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social accounts that automatically verifies
    email addresses from trusted providers like Google.
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a social provider,
        but before the login is actually processed.
        """
        # Get the email from the social account
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return
        
        # Check if this email already exists in the system
        try:
            existing_email = EmailAddress.objects.get(email=email)
            
            # If the email exists but belongs to a different user, we'll let allauth handle it
            if existing_email.user != sociallogin.user:
                return
                
        except EmailAddress.DoesNotExist:
            # Email doesn't exist yet, we'll create it as verified
            pass
        
        # Mark the email as verified for this social login
        if not sociallogin.email_addresses:
            return
            
        for email_address in sociallogin.email_addresses:
            email_address.verified = True
            
        # Add a success message
        user = sociallogin.user
        messages.success(
            request, 
            f"Welcome, {user.username or user.email}! You've successfully signed in with Google."
        )
        
        logger.info(f"Social login successful for user: {user.username or user.email}")
    
    def get_connect_redirect_url(self, request, socialaccount):
        """
        Returns the default URL to redirect to after successfully
        connecting a social account.
        """
        return reverse('home:index') 