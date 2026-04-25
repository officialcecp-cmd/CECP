# ==============================================================================
# Landing App — Supabase Client Integration
# ==============================================================================
# This module provides a centralized Supabase client instance and helper
# functions for fetching data from Supabase tables. It gracefully falls back
# to None if Supabase credentials are not configured, allowing the Django
# views to use hardcoded fallback data during local development.
# ==============================================================================
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# --- Supabase Client Singleton ------------------------------------------------
_supabase_client = None


def get_supabase_client():
    """
    Returns a singleton Supabase client instance.
    Returns None if credentials are not configured.
    """
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    url = getattr(settings, 'SUPABASE_URL', '')
    key = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', '') or \
          getattr(settings, 'SUPABASE_ANON_KEY', '')

    if not url or not key:
        logger.warning(
            "Supabase credentials not configured. "
            "Set SUPABASE_URL and SUPABASE_ANON_KEY in your .env file. "
            "Falling back to static data."
        )
        return None

    try:
        from supabase import create_client
        _supabase_client = create_client(url, key)
        logger.info("Supabase client initialized successfully.")
        return _supabase_client
    except ImportError:
        logger.error("supabase package not installed. Run: pip install supabase")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None


# --- Data Fetching Helpers ----------------------------------------------------

def fetch_initiatives():
    """
    Fetch active initiatives from the 'initiatives' Supabase table.
    Returns a list of dicts or None if unavailable.
    """
    client = get_supabase_client()
    if not client:
        return None

    try:
        response = client.table('initiatives') \
            .select('*') \
            .eq('is_active', True) \
            .order('display_order') \
            .execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching initiatives from Supabase: {e}")
        return None


def fetch_featured_projects():
    """
    Fetch featured projects from the 'projects' Supabase table.
    Returns a list of dicts or None if unavailable.
    """
    client = get_supabase_client()
    if not client:
        return None

    try:
        response = client.table('projects') \
            .select('*') \
            .eq('is_featured', True) \
            .neq('status', 'archived') \
            .order('display_order') \
            .execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching projects from Supabase: {e}")
        return None


def fetch_team_members():
    """
    Fetch active team members from the 'team_members' Supabase table.
    Returns a list of dicts or None if unavailable.
    """
    client = get_supabase_client()
    if not client:
        return None

    try:
        response = client.table('team_members') \
            .select('*') \
            .eq('is_active', True) \
            .order('display_order') \
            .execute()
        return response.data
    except Exception as e:
        logger.error(f"Error fetching team members from Supabase: {e}")
        return None
