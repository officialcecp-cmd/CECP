# ==============================================================================
# Landing App — Access Control Decorators
# ==============================================================================
# Role-based decorators for the unified authentication system.
# ==============================================================================
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def admin_required(view_func):
    """
    Restricts access to admin-level users only (Club Head, Faculty, HOD).
    Redirects non-admin users to the unified login page.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Authentication required. Please login.')
            return redirect('landing:login')

        try:
            profile = request.user.club_profile
            if profile.role not in ('hod', 'faculty', 'club_head'):
                messages.error(request, 'ACCESS DENIED — Insufficient clearance level.')
                return redirect('landing:index')
            if not profile.is_active:
                messages.error(request, 'Your admin account has been deactivated.')
                return redirect('landing:login')
        except Exception:
            messages.error(request, 'No admin profile linked to this account.')
            return redirect('landing:login')

        return view_func(request, *args, **kwargs)
    return _wrapped


def club_member_required(view_func):
    """
    Restricts access to registered club members only.
    Non-club-member users get redirected to the login page.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Authentication required.')
            return redirect('landing:login')

        try:
            profile = request.user.club_profile
            if not profile.is_active:
                messages.error(request, 'Your member profile has been deactivated.')
                return redirect('landing:login')
        except Exception:
            messages.error(request, 'No club member profile found for your account.')
            return redirect('landing:login')

        return view_func(request, *args, **kwargs)
    return _wrapped
