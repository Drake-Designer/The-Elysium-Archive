"""Django settings for elysium_archive project."""

import os
from pathlib import Path
from typing import Any, cast

import dj_database_url
from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured
from django.core.management.utils import get_random_secret_key

# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment file if exists (gitignored, for dev only)
if (BASE_DIR / "env.py").exists():
    import env  # noqa: F401


# Helper: Parse boolean from environment variable
def _env_bool(value, default=False):
    """Convert string like 'true', '1', 'yes' to boolean."""
    if value is None:
        return default
    return str(value).strip().lower() in ("true", "1", "yes", "y", "on")


# Helper: Parse comma-separated list from environment variable
def _env_list(name, default=None):
    """Convert comma-separated string to list.

    Example: 'value1,value2,value3' -> ['value1', 'value2', 'value3']
    """
    raw = os.environ.get(name)
    if raw is None:
        return default or []
    return [item.strip() for item in raw.split(",") if item.strip()]


# Secret key for Django cryptographic signing (sessions, tokens, etc.)
SECRET_KEY_ENV = (
    os.environ.get("SECRET_KEY")
    or os.environ.get("DJANGO_SECRET_KEY")
)
SECRET_KEY = SECRET_KEY_ENV or get_random_secret_key()

# Debug mode (detailed error pages, auto static serving)
DEBUG = _env_bool(os.environ.get("DEBUG"), default=True)

# Prevent production deployment without explicit secret key
if not DEBUG and not SECRET_KEY_ENV:
    raise ImproperlyConfigured(
        "SECRET_KEY must be set to a secure value when DEBUG=False."
    )

# Check if running on Heroku
IS_HEROKU = os.environ.get("DYNO") is not None

# Domains allowed to serve this site (prevents HTTP Host header attacks)
ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS", default=[])

# Auto-allow Heroku domains in production
if not ALLOWED_HOSTS and IS_HEROKU:
    ALLOWED_HOSTS = [".herokuapp.com"]

# Always allow localhost in development
if DEBUG:
    for host in ("localhost", "127.0.0.1"):
        if host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)

# Trusted origins for CSRF protection (needed for HTTPS POST requests)
CSRF_TRUSTED_ORIGINS = _env_list("CSRF_TRUSTED_ORIGINS", default=[])

# Auto-configure CSRF trusted origins for Heroku
if not CSRF_TRUSTED_ORIGINS and IS_HEROKU:
    CSRF_TRUSTED_ORIGINS = ["https://*.herokuapp.com"]

# Allow localhost CSRF in development
if DEBUG and not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = ["http://127.0.0.1", "http://localhost"]

# Trust proxy headers for HTTPS detection (required for Heroku)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Production security settings (HTTPS enforcement, secure cookies)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Additional security headers
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# Django apps loaded for this project
INSTALLED_APPS = [
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "django_ckeditor_5",
    "cloudinary",
    "cloudinary_storage",
    "accounts.apps.AccountsConfig",
    "home",
    "products",
    "cart.apps.CartConfig",
    "checkout",
    "orders",
    "reviews",
]

# Required for django.contrib.sites
SITE_ID = int(os.environ.get("SITE_ID", "1"))

# Jazzmin admin interface customization
JAZZMIN_SETTINGS = {
    "site_title": "The Elysium Archive Admin",
    "site_header": "The Elysium Archive",
    "site_brand": "The Elysium Archive",
    "welcome_sign": "Welcome to the Elysium Archive admin panel.",
    "search_model": ["auth.User", "auth.Group"],
    "topmenu_links": [
        {"name": "View site", "url": "/", "new_window": False},
        {"name": "Test Errors", "url": "/_test/errors/", "new_window": False},
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

# Middleware processing order (request/response pipeline)
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Map Django message levels to Bootstrap CSS classes
MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

# Main URL configuration module
ROOT_URLCONF = "elysium_archive.urls"

# Template engine configuration
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
                "elysium_archive.context_processors.cart_context",
                "elysium_archive.context_processors.deals_context",
            ],
        },
    }
]

# WSGI application entry point
WSGI_APPLICATION = "elysium_archive.wsgi.application"

# Database configuration (SQLite for dev, PostgreSQL for production)
DATABASES: dict[str, Any] = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Override with PostgreSQL if DATABASE_URL is set (Heroku)
if os.environ.get("DATABASE_URL"):
    db_config = dj_database_url.config(conn_max_age=600, ssl_require=True)
    DATABASES["default"] = cast(dict[str, Any], db_config)

# Password validation rules for user accounts
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        )
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        )
    },
]

# Localization settings
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Dublin"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JS, images) configuration
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# User-uploaded media files configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Storage backends (Cloudinary for production, local filesystem for dev)
if os.environ.get("CLOUDINARY_URL"):
    # Production: Use Cloudinary for media, WhiteNoise for static
    STORAGES = {
        "default": {
            "BACKEND": (
                "cloudinary_storage.storage.MediaCloudinaryStorage"
            ),
        },
        "staticfiles": {
            "BACKEND": (
                "whitenoise.storage."
                "CompressedManifestStaticFilesStorage"
            ),
        },
    }
    CKEDITOR_5_FILE_STORAGE = (
        "cloudinary_storage.storage.MediaCloudinaryStorage"
    )

    import cloudinary

    cloudinary.config(secure=True)
else:
    # Development: Use local filesystem for both media and static
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": (
                "whitenoise.storage."
                "CompressedManifestStaticFilesStorage"
            ),
        },
    }
    CKEDITOR_5_FILE_STORAGE = (
        "django.core.files.storage.FileSystemStorage"
    )

# Default primary key field type for models
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication URL redirects
LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# Authentication backends (Django default + custom case-sensitive backend)
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "accounts.backends.CaseSensitiveAuthenticationBackend",
]

# Django-allauth configuration (user registration and authentication)
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = [
    "email*", "username*", "password1*", "password2*"
]
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = os.environ.get(
    "ACCOUNT_EMAIL_VERIFICATION", "mandatory"
)
ACCOUNT_EMAIL_REQUIRED = True

# Custom allauth forms
ACCOUNT_FORMS = {
    "signup": "accounts.forms.ElysiumSignupForm",
    "login": "accounts.forms.ElysiumLoginForm",
}

# Use HTTPS for email links in production
if DEBUG:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = os.environ.get(
        "ACCOUNT_DEFAULT_HTTP_PROTOCOL",
        "http",
    )
else:
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

# Email backend (console for dev, SMTP for production)
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# SMTP configuration (using Resend SMTP by default)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.resend.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = _env_bool(os.environ.get("EMAIL_USE_TLS"), default=True)
EMAIL_USE_SSL = _env_bool(os.environ.get("EMAIL_USE_SSL"), default=False)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "resend")

# Resend uses the API key as the SMTP password
EMAIL_HOST_PASSWORD = os.environ.get("RESEND_API_KEY") or os.environ.get(
    "EMAIL_HOST_PASSWORD", ""
)

# Normalize TLS/SSL based on standard SMTP ports if mismatched
if EMAIL_PORT == 465:
    if EMAIL_USE_TLS or not EMAIL_USE_SSL:
        EMAIL_USE_TLS = False
        EMAIL_USE_SSL = True
elif EMAIL_PORT == 587:
    if EMAIL_USE_SSL or not EMAIL_USE_TLS:
        EMAIL_USE_SSL = False
        EMAIL_USE_TLS = True

# Email sender addresses
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "The Elysium Archive <noreply@drakedrumstudio.ie>",
)
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", DEFAULT_FROM_EMAIL)

# Contact form recipient
CONTACT_RECIPIENT_EMAIL = os.environ.get(
    "CONTACT_RECIPIENT_EMAIL", DEFAULT_FROM_EMAIL
)

# Email subject prefix for allauth emails
ACCOUNT_EMAIL_SUBJECT_PREFIX = os.environ.get(
    "ACCOUNT_EMAIL_SUBJECT_PREFIX", "[The Elysium Archive] "
)

# Prevent production deployment without email credentials
if not DEBUG and not EMAIL_HOST_PASSWORD:
    raise ImproperlyConfigured(
        "RESEND_API_KEY (or EMAIL_HOST_PASSWORD) must be set when DEBUG=False."
    )

# Stripe payment gateway configuration
STRIPE_PUBLIC_KEY = os.environ.get(
    "STRIPE_PUBLIC_KEY", "pk_test_dummy_key_for_local_dev"
)
STRIPE_SECRET_KEY = os.environ.get(
    "STRIPE_SECRET_KEY", "sk_test_dummy_key_for_local_dev"
)
STRIPE_WH_SECRET = os.environ.get("STRIPE_WH_SECRET", "")

# CKEditor 5 rich text editor configuration
CKEDITOR_5_UPLOAD_PATH = "ckeditor5/"

CKEDITOR_5_CONFIGS = {
    # Configuration for product content (full featured)
    "product_content": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "link",
            "|",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "outdent",
            "indent",
            "alignment",
            "|",
            "blockQuote",
            "codeBlock",
            "horizontalLine",
            "pageBreak",
            "insertTable",
            "imageUpload",
            "mediaEmbed",
            "|",
            "undo",
            "redo",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "toggleImageCaption",
                "imageStyle:inline",
                "imageStyle:block",
                "imageStyle:side",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
        },
        "height": "500px",
    },
    # Configuration for general writing (simplified toolbar)
    "writer": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "link",
            "|",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "blockQuote",
            "codeBlock",
            "insertTable",
            "imageUpload",
            "horizontalLine",
            "|",
            "undo",
            "redo",
        ],
        "heading": {
            "options": [
                {
                    "model": "paragraph",
                    "title": "Paragraph",
                    "class": "ck-heading_paragraph",
                },
                {
                    "model": "heading2",
                    "view": "h2",
                    "title": "Heading 2",
                    "class": "ck-heading_heading2",
                },
                {
                    "model": "heading3",
                    "view": "h3",
                    "title": "Heading 3",
                    "class": "ck-heading_heading3",
                },
            ]
        },
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "toggleImageCaption",
                "imageStyle:inline",
                "imageStyle:block",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn", "tableRow", "mergeTableCells"
            ]
        },
        "height": "600px",
    },
    # Default configuration (full featured)
    "default": {
        "toolbar": [
            "heading",
            "|",
            "bold",
            "italic",
            "underline",
            "strikethrough",
            "link",
            "|",
            "bulletedList",
            "numberedList",
            "todoList",
            "|",
            "outdent",
            "indent",
            "alignment",
            "|",
            "blockQuote",
            "codeBlock",
            "horizontalLine",
            "pageBreak",
            "insertTable",
            "imageUpload",
            "mediaEmbed",
            "|",
            "undo",
            "redo",
        ],
        "image": {
            "toolbar": [
                "imageTextAlternative",
                "toggleImageCaption",
                "imageStyle:inline",
                "imageStyle:block",
                "imageStyle:side",
            ],
        },
        "table": {
            "contentToolbar": [
                "tableColumn",
                "tableRow",
                "mergeTableCells",
                "tableProperties",
                "tableCellProperties",
            ],
        },
        "height": "500px",
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "ERROR",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}
