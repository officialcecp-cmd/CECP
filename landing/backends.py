# ==============================================================================
# Landing App — Custom Authentication Backends
# ==============================================================================
# Implements: Email-based member auth, Username-based admin auth.
# Role-gating ensures only the correct user types can login via each panel.
# ==============================================================================
import logging
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class AdminLoginBackend(ModelBackend):
    """
    Authenticates admins (Faculty Coordinator, Club Head, HOD) using
    username + password. Only allows users with admin-level roles.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Only activate for admin panel logins
        if kwargs.get('login_type') != 'admin':
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if not user.check_password(password):
            return None

        if not user.is_active:
            return None

        # Verify the user has an admin-level ClubMember profile
        try:
            profile = user.club_profile
            if profile.role not in ('hod', 'faculty', 'club_head'):
                logger.warning(
                    f"Non-admin user '{username}' attempted admin login."
                )
                return None
            if not profile.is_active:
                return None
        except Exception:
            # No club_profile → not an admin
            return None

        return user


class MemberLoginBackend(ModelBackend):
    """
    Authenticates members using their registered email + password.
    Works for both club members and external users.
    Automatically identifies whether the user is a registered club member
    or a general user based on their ClubMember profile.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # Only activate for member panel logins
        if kwargs.get('login_type') != 'member':
            return None

        email = kwargs.get('email') or username

        if not email:
            return None

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            logger.info(f"No user found with email: {email}")
            return None
        except User.MultipleObjectsReturned:
            # Edge case: multiple users with same email
            user = User.objects.filter(email__iexact=email).first()

        if not user.check_password(password):
            return None

        if not user.is_active:
            return None

        return user
