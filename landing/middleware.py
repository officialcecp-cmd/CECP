# ==============================================================================
# Landing App — Custom Middleware
# ==============================================================================
# Provides session-level role tracking for the dual-panel auth system.
# ==============================================================================
import logging

logger = logging.getLogger(__name__)


class RoleSessionMiddleware:
    """
    Injects role-related context into the request object for easy
    access throughout views and templates.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Inject role info into request
            request.login_type = request.session.get('login_type', 'member')
            request.is_club_member = False
            request.is_admin_user = False
            request.member_role = None

            try:
                profile = request.user.club_profile
                request.member_role = profile.role
                request.is_club_member = profile.is_active and profile.role == 'member'
                request.is_admin_user = profile.is_active and profile.role in ('hod', 'faculty', 'club_head')
            except Exception:
                pass
        else:
            request.login_type = None
            request.is_club_member = False
            request.is_admin_user = False
            request.member_role = None

        response = self.get_response(request)
        return response
