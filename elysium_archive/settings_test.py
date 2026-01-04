"""Django test settings for elysium_archive project.

Imports base settings and overrides for test environment.
Disables manifest-based staticfiles storage and enables in-memory email backend.
"""

from elysium_archive.settings import *  # noqa: F401, F403

# Use non-manifest staticfiles storage for tests to avoid missing favicon errors.
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# Override STORAGES for test environment to use simple storage without manifest.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Use in-memory email backend to prevent actual email sending during tests.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Use fast password hasher for tests to speed up user creation.
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
