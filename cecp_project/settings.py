# ==============================================================================
# CECP Club Website — Django Project Settings
# ==============================================================================
# Configured for: Django 4.2+ | Supabase (PostgreSQL) | Tailwind via CDN
# ==============================================================================

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Path Configuration -------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Security ------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-cecp-dev-key-change-in-production'
)
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = ['*']  # Lock this down in production

# --- Application Definition ----------------------------------------------------
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # --- CECP Apps ---
    'landing.apps.LandingConfig',
    
    # --- Allauth ---
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.microsoft',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'landing.middleware.RoleSessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'cecp_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # App-level templates are auto-discovered
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'cecp_project.wsgi.application'

# --- Database ------------------------------------------------------------------
# Uses SQLite by default for local dev. Switch to Supabase PostgreSQL via
# DATABASE_URL env var for staging/production.
# Example: DATABASE_URL=postgresql://user:pass@db.xxx.supabase.co:5432/postgres

_database_url = os.environ.get('DATABASE_URL')

if _database_url:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(
            default=_database_url,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# --- Supabase Client Config (for API-level integration) -----------------------
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', '')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')

# --- Password Validation -------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Internationalization -------------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# --- Static Files ---------------------------------------------------------------
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# --- Default Primary Key Field Type --------------------------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- Media Files ----------------------------------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Authentication Redirects --------------------------------------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# --- Custom Authentication Backends -------------------------------------------
# Dual-panel auth: Admin (username) and Member (email) backends.
AUTHENTICATION_BACKENDS = [
    'landing.backends.AdminLoginBackend',
    'landing.backends.MemberLoginBackend',
    'django.contrib.auth.backends.ModelBackend',  # Fallback for Django admin
    'allauth.account.auth_backends.AuthenticationBackend',  # Allauth backend
]

# --- Allauth Settings ----------------------------------------------------------
SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = "none"
SOCIALACCOUNT_LOGIN_ON_GET = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'APP': {
            'client_id': 'dummy-client-id',
            'secret': 'dummy-secret',
            'key': ''
        }
    },
    'github': {
        'SCOPE': ['user:email', 'read:user'],
        'APP': {
            'client_id': 'dummy-client-id',
            'secret': 'dummy-secret',
            'key': ''
        }
    },
    'microsoft': {
        'SCOPE': ['User.Read'],
        'APP': {
            'client_id': 'dummy-client-id',
            'secret': 'dummy-secret',
            'key': ''
        }
    }
}

# --- Jazzmin Admin Theme Configuration -----------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "CECP Admin",
    "site_header": "CECP",
    "site_brand": "CECP Master Dashboard",
    "site_logo": "images/cecp-logo.jpg",
    "login_logo": "images/cecp-logo.jpg",
    "welcome_sign": "Welcome to the CECP Master Dashboard",
    "copyright": "CECP Club RIT Roorkee",
    "search_model": ["auth.User", "landing.ClubMember"],
    "show_ui_builder": False,
    "custom_css": "css/jazzmin-custom.css",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "default",
    "dark_mode_theme": "darkly",
}
