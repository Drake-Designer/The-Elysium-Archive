"""
Django settings for elysium_archive project.
"""

import os
from pathlib import Path

import dj_database_url

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment variables (dev only)
if (BASE_DIR / "env.py").exists():
    import env  # noqa: F401


def _env_bool(value, default=False):
    """Parse a boolean environment variable."""
    if value is None:
        return default
    return str(value).strip().lower() in ("true", "1", "yes", "y", "on")


def _env_list(name, default=None):
    """Parse a comma-separated environment variable into a list."""
    raw = os.environ.get(name)
    if raw is None:
        return default or []
    return [item.strip() for item in raw.split(",") if item.strip()]


# Security
SECRET_KEY = os.environ.get("SECRET_KEY", "unsafe-dev-secret-key")
DEBUG = _env_bool(os.environ.get("DEBUG"), default=True)

# Hosts / CSRF
ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS", default=[])

if DEBUG:
    for host in ("localhost", "127.0.0.1"):
        if host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)

CSRF_TRUSTED_ORIGINS = _env_list("CSRF_TRUSTED_ORIGINS", default=[])

# Heroku / reverse proxy HTTPS header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True


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
    # Third-party (media only via Cloudinary)
    # Keep staticfiles before cloudinary apps when you use Cloudinary for media only. :contentReference[oaicite:0]{index=0}
    "cloudinary_storage",
    "cloudinary",
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

ROOT_URLCONF = "elysium_archive.urls"

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

WSGI_APPLICATION = "elysium_archive.wsgi.application"


# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if os.environ.get("DATABASE_URL"):
    db_config = dj_database_url.config(
        conn_max_age=600,
        ssl_require=True,
    )
    DATABASES["default"] = dict(db_config) if db_config is not None else {}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Dublin"
USE_I18N = True
USE_TZ = True


# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files (Cloudinary)
MEDIA_URL = "/media/"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
