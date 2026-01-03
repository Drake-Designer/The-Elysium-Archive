"""WSGI config for the elysium_archive project."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "elysium_archive.settings")

application = get_wsgi_application()
