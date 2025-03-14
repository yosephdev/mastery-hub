from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.models import EmailAddress
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from allauth.account.utils import perform_login
from allauth.exceptions import ImmediateHttpResponse
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
    Custom adapter for social accounts that automatically verifies
    email addresses from trusted providers like Google.
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a social provider,
        but before the login is actually processed.
        """
        # Store the provider in the session
        if hasattr(request, 'session'):
            request.session['sociallogin_provider'] = sociallogin.account.provider
        
        # Get the email from the social account
        email = sociallogin.account.extra_data.get('email')
        if not email:
            return
        
        # Check if this email already exists in the system
        try:
            existing_email = EmailAddress.objects.get(email=email)
            
            # If the email exists but belongs to a different user, connect the accounts
            if existing_email.user != sociallogin.user:
                # Log the user in directly with the existing account
                user = existing_email.user
                sociallogin.connect(request, user)
                
                # Add a success message
                messages.success(
                    request, 
                    f"Welcome back, {user.username or user.email}! You've successfully signed in with Google."
                )
                
                # Perform login and redirect
                perform_login(request, user, email_verification="none")
                
                # Redirect to home page
                raise ImmediateHttpResponse(redirect(reverse('home:index')))
                
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
        
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Always allow auto signup for social accounts.
        """
        return True
        
    def populate_user(self, request, sociallogin, data):
        """
        Hook that can be used to further populate the user instance.
        """
        user = super().populate_user(request, sociallogin, data)
        
        # Set email as verified
        user.emailaddress_set.create(email=user.email, verified=True, primary=True)
        
        return user 