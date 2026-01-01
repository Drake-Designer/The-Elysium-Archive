"""
Django settings for elysium_archive project
"""

import os
from pathlib import Path

import dj_database_url

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment variables
if (BASE_DIR / "env.py").exists():
    import env  # noqa: F401


def _env_bool(value, default=False):
    """Parse a boolean environment variable"""
    if value is None:
        return default
    return str(value).strip().lower() in ["true", "1", "yes", "y", "on"]


# Security settings
SECRET_KEY = os.environ.get("SECRET_KEY", "unsafe-dev-secret-key")
DEBUG = _env_bool(os.environ.get("DEBUG"), default=True)

# Allowed hosts
_allowed_hosts_raw = os.environ.get("ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_raw.split(",") if h.strip()]

if DEBUG:
    if "localhost" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append("localhost")
    if "127.0.0.1" not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append("127.0.0.1")


# Application definition
INSTALLED_APPS = [
    # Admin theme
    "jazzmin",
    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Project apps
    "home",
    "accounts",
    "products",
    "cart",
    "checkout",
    "orders",
    "reviews",
]

# Jazzmin configuration
JAZZMIN_SETTINGS = {
    "site_title": "The Elysium Archive Admin",
    "site_header": "The Elysium Archive",
    "site_brand": "The Elysium Archive",
    "site_logo": None,
    "welcome_sign": "Welcome to the Elysium Archive admin panel.",
    "copyright": "The Elysium Archive",
    "search_model": [
        "auth.User",
        "auth.Group",
    ],
    "topmenu_links": [
        {"name": "View site", "url": "/", "new_window": False},
        {"model": "auth.User"},
        {"model": "auth.Group"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.group": "fas fa-users",
    },
}

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# URL configuration
ROOT_URLCONF = "elysium_archive.urls"

# Templates configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI application
WSGI_APPLICATION = "elysium_archive.wsgi.application"


# Database configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if "DATABASE_URL" in os.environ:
    db_config = dj_database_url.config(conn_max_age=600, ssl_require=True)
    DATABASES["default"] = dict(db_config)


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Dublin"
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Default primary key field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
