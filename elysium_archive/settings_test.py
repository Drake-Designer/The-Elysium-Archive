"""
Test settings for the Elysium Archive project.

This file loads the main settings and changes only what is needed for testing.
"""

# pylint: disable=wildcard-import,unused-wildcard-import
from elysium_archive.settings import *  # noqa: F401, F403

# Keep storage simple and local for tests.
# This avoids any external dependency (Cloudinary) and any manifest pipeline issues.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Keep emails in memory and do not send real ones.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Force HTML emails in tests as well.
ACCOUNT_EMAIL_HTML = True

# Use a faster hasher to speed up tests.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Keep Stripe webhook validation enabled in tests without requiring env vars.
STRIPE_WH_SECRET = "whsec_test_dummy"  # nosec B105
