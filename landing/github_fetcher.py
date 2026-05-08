# ==============================================================================
# GitHub Data Fetcher — Pulls repos & languages from public GitHub profiles
# ==============================================================================
import logging
import requests
from datetime import timedelta
from django.utils import timezone
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"
CACHE_DURATION = timedelta(hours=6)  # Refresh every 6 hours


def extract_github_username(github_url):
    """
    Extract the GitHub username from a profile URL.
    Handles: https://github.com/username, https://www.github.com/username/, etc.
    """
    if not github_url:
        return None
    try:
        parsed = urlparse(github_url.strip().rstrip('/'))
        parts = parsed.path.strip('/').split('/')
        if parts and parts[0]:
            return parts[0]
    except Exception:
        pass
    return None


def fetch_github_repos(username, max_repos=20):
    """
    Fetch public repositories for a GitHub user.
    Returns a list of dicts with repo info, sorted by stars then updated_at.
    """
    if not username:
        return []
    try:
        url = f"{GITHUB_API_BASE}/users/{username}/repos"
        params = {
            'type': 'owner',
            'sort': 'updated',
            'direction': 'desc',
            'per_page': min(max_repos, 100),
        }
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CECP-Nexus-Portal/1.0',
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            repos_data = response.json()
            repos = []
            for repo in repos_data:
                if repo.get('fork', False):
                    continue  # Skip forks
                repos.append({
                    'name': repo.get('name', ''),
                    'description': repo.get('description', '') or '',
                    'html_url': repo.get('html_url', ''),
                    'language': repo.get('language', '') or '',
                    'stars': repo.get('stargazers_count', 0),
                    'forks': repo.get('forks_count', 0),
                    'updated_at': repo.get('updated_at', ''),
                    'topics': repo.get('topics', []),
                })
            # Sort: starred repos first, then by update date
            repos.sort(key=lambda r: (-r['stars'], r['updated_at']), reverse=False)
            return repos[:max_repos]
        else:
            logger.warning(f"GitHub API returned {response.status_code} for user {username}")
            return []
    except requests.RequestException as e:
        logger.error(f"GitHub API request failed for {username}: {e}")
        return []


def fetch_github_languages(username, max_repos=30):
    """
    Aggregate language statistics across all public repos of a GitHub user.
    Returns a dict of {language: byte_count}, sorted by usage.
    """
    if not username:
        return {}
    try:
        # First get repos
        url = f"{GITHUB_API_BASE}/users/{username}/repos"
        params = {
            'type': 'owner',
            'sort': 'updated',
            'per_page': min(max_repos, 100),
        }
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CECP-Nexus-Portal/1.0',
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return {}

        repos = response.json()
        language_totals = {}

        for repo in repos:
            if repo.get('fork', False):
                continue
            lang = repo.get('language')
            if lang:
                language_totals[lang] = language_totals.get(lang, 0) + 1

        # Sort by frequency
        sorted_langs = dict(sorted(language_totals.items(), key=lambda x: -x[1]))
        return sorted_langs

    except requests.RequestException as e:
        logger.error(f"GitHub languages fetch failed for {username}: {e}")
        return {}


def sync_github_data(profile, force=False):
    """
    Sync GitHub repos and languages for a UserProfile.
    Uses caching to avoid hitting the API too often.
    Returns (repos, languages) tuple.
    """
    now = timezone.now()

    # Check if cache is still valid
    if (not force
            and profile.last_github_sync
            and (now - profile.last_github_sync) < CACHE_DURATION
            and profile.github_repos_cache is not None):
        return profile.github_repos_cache, profile.github_languages_cache or {}

    username = extract_github_username(profile.github_profile)
    if not username:
        return [], {}

    repos = fetch_github_repos(username)
    languages = fetch_github_languages(username)

    # Save to cache
    profile.github_repos_cache = repos
    profile.github_languages_cache = languages
    profile.last_github_sync = now
    profile.save(update_fields=['github_repos_cache', 'github_languages_cache', 'last_github_sync'])

    return repos, languages
