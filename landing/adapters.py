# ==============================================================================
# Landing App — Custom Allauth Adapter
# ==============================================================================
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CECPSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter that auto-generates a username from the user's email
    so social login never shows the 'pick a username' signup page.
    """

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        # If username is empty, generate one from email
        if not user.username:
            email = data.get('email', '')
            base = email.split('@')[0] if email else 'user'
            user.username = base
        return user

    def save_user(self, request, sociallogin, form=None):
        """
        Ensure unique username before saving.
        """
        user = sociallogin.user
        if not user.username:
            email = user.email or ''
            user.username = email.split('@')[0] if email else 'user'

        # Make username unique
        from django.contrib.auth.models import User
        base = user.username
        counter = 1
        while User.objects.filter(username=user.username).exists():
            user.username = f"{base}{counter}"
            counter += 1

        return super().save_user(request, sociallogin, form)

    def pre_social_login(self, request, sociallogin):
        """
        Auto-link social accounts to existing local users with matching email addresses.
        This prevents the signup form from appearing when an email already exists in the database.
        """
        if sociallogin.is_existing:
            return

        if not sociallogin.email_addresses:
            return

        email = sociallogin.email_addresses[0].email
        
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(email=email)
            # Link the social account to the existing user
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass
