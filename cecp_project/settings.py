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
ALLOWED_HOSTS = ['scared-sitting-germicide.ngrok-free.dev', 'localhost', '127.0.0.1']  # Lock this down in production
CSRF_TRUSTED_ORIGINS = ['https://scared-sitting-germicide.ngrok-free.dev']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http'  # Use 'https' only when testing via ngrok

# --- Application Definition ----------------------------------------------------
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
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
# Always connects to the live Supabase PostgreSQL database via DATABASE_URL.
# Every team member MUST have DATABASE_URL set in their .env file.
# Copy .env.example → .env and fill in the shared Supabase credentials.

import dj_database_url as _dj_db_url

_database_url = os.environ.get('DATABASE_URL')

if not _database_url:
    raise RuntimeError(
        "\n\n❌  DATABASE_URL is not set!\n"
        "    Please add it to your .env file.\n"
        "    Copy .env.example → .env and fill in the Supabase connection string.\n"
    )

DATABASES = {
    'default': _dj_db_url.config(
        default=_database_url,
        conn_max_age=0,      # Release connection after each request (fixes Supabase pool exhaustion)
        ssl_require=False,
    )
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

# --- Media Files (Cloudinary Integration) ---------------------------------------
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
}

STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# --- Authentication Redirects --------------------------------------------------
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
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
SOCIALACCOUNT_AUTO_SIGNUP = True
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_UNIQUE_EMAIL = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_ADAPTER = 'landing.adapters.CECPSocialAccountAdapter'

# --- allauth 65.x: Do NOT put APP credentials here.
# Allauth 65 auto-imports these settings into the DB (SocialApp table) on startup.
# Having APP in settings AND a SocialApp DB row causes MultipleObjectsReturned.
# Manage credentials via Django Admin → Social Applications instead.
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    },
    'github': {
        'SCOPE': ['user:email', 'read:user'],
    },
    'microsoft': {
        'SCOPE': ['User.Read'],
    },
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

# --- Email / SMTP Settings -----------------------------------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
