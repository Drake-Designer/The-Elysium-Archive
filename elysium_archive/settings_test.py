"""
Test settings for the Elysium Archive project.

This file loads the main settings and changes what is needed for testing.
"""

from elysium_archive.settings import *  # noqa: F401, F403

# Avoid errors caused by missing static files during tests.
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Use simple file storage instead of the manifest system.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Keep emails in memory and does not send real ones.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Force HTML emails in tests as well.
ACCOUNT_EMAIL_HTML = True

# Use a faster hasher to speed up tests.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
