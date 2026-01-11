"""Django settings for elysium_archive project."""

import os
from pathlib import Path
from typing import Any, cast

import dj_database_url
from django.contrib.messages import constants as messages
from django.core.exceptions import ImproperlyConfigured

# Base directory and local environment loading
BASE_DIR = Path(__file__).resolve().parent.parent

if (BASE_DIR / "env.py").exists():
    import env  # noqa: F401


# Environment helper functions
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


# Core security and environment flags
SECRET_KEY = os.environ.get("SECRET_KEY", "unsafe-dev-secret-key")
DEBUG = _env_bool(os.environ.get("DEBUG"), default=True)

if not DEBUG and (not SECRET_KEY or SECRET_KEY == "unsafe-dev-secret-key"):
    raise ImproperlyConfigured(
        "SECRET_KEY must be set to a secure value when DEBUG=False."
    )

IS_HEROKU = os.environ.get("DYNO") is not None

# Hosts and CSRF configuration
ALLOWED_HOSTS = _env_list("ALLOWED_HOSTS", default=[])

if not ALLOWED_HOSTS and IS_HEROKU:
    ALLOWED_HOSTS = [".herokuapp.com"]

if DEBUG:
    for host in ("localhost", "127.0.0.1"):
        if host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)

CSRF_TRUSTED_ORIGINS = _env_list("CSRF_TRUSTED_ORIGINS", default=[])

if not CSRF_TRUSTED_ORIGINS and IS_HEROKU:
    CSRF_TRUSTED_ORIGINS = ["https://*.herokuapp.com"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Security headers
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# Installed applications
INSTALLED_APPS = [
    # Admin theme
    "jazzmin",
    # Django core
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    # Third party
    "allauth",
    "allauth.account",
    "django_ckeditor_5",
    "cloudinary",
    "cloudinary_storage",
    # Local apps
    "accounts.apps.AccountsConfig",
    "home",
    "products",
    "cart",
    "checkout",
    "orders",
    "reviews",
]

SITE_ID = int(os.environ.get("SITE_ID", "1"))

# Admin interface configuration
JAZZMIN_SETTINGS = {
    "site_title": "The Elysium Archive Admin",
    "site_header": "The Elysium Archive",
    "site_brand": "The Elysium Archive",
    "welcome_sign": "Welcome to the Elysium Archive admin panel.",
    "search_model": ["auth.User", "auth.Group"],
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

# Middleware configuration
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

# Django message tag mapping
MESSAGE_TAGS = {
    messages.DEBUG: "secondary",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

# URL and template configuration
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
                "elysium_archive.context_processors.cart_context",
                "elysium_archive.context_processors.deals_context",
            ],
        },
    }
]

WSGI_APPLICATION = "elysium_archive.wsgi.application"

# Database configuration
DATABASES: dict[str, Any] = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

if os.environ.get("DATABASE_URL"):
    db_config = dj_database_url.config(conn_max_age=600, ssl_require=True)
    DATABASES["default"] = cast(dict[str, Any], db_config)

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization settings
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Dublin"
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files and storage configuration
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

if os.environ.get("CLOUDINARY_URL"):
    STORAGES = {
        "default": {
            "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    CKEDITOR_5_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

    # Configure Cloudinary to serve secure URLs
    import cloudinary

    cloudinary.config(secure=True)
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    CKEDITOR_5_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Default model field configuration
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Authentication redirects
LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Allauth configuration
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = os.environ.get(
    "ACCOUNT_EMAIL_VERIFICATION",
    "mandatory",
)

# Enable HTML emails for allauth
ACCOUNT_EMAIL_HTML = _env_bool(os.environ.get("ACCOUNT_EMAIL_HTML"), default=True)

ACCOUNT_FORMS = {
    "signup": "accounts.forms.ElysiumSignupForm",
    "login": "accounts.forms.ElysiumLoginForm",
}

# Email configuration
if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL",
    "The Elysium Archive <elysiumarchive@outlook.com>",
)
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", DEFAULT_FROM_EMAIL)

EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.sendgrid.net")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = _env_bool(os.environ.get("EMAIL_USE_TLS"), default=True)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "apikey")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")

# Stripe configuration
STRIPE_PUBLIC_KEY = os.environ.get(
    "STRIPE_PUBLIC_KEY", "pk_test_dummy_key_for_local_dev"
)
STRIPE_SECRET_KEY = os.environ.get(
    "STRIPE_SECRET_KEY", "sk_test_dummy_key_for_local_dev"
)
STRIPE_WH_SECRET = os.environ.get("STRIPE_WH_SECRET", "")

# CKEditor 5 configuration
CKEDITOR_5_UPLOAD_PATH = "ckeditor5/"

CKEDITOR_5_CONFIGS = {
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
            "contentToolbar": ["tableColumn", "tableRow", "mergeTableCells"],
        },
        "height": "600px",
    },
    # Keep a default config to avoid warnings from packages expecting a 'default' key.
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
