"""
Django development settings for Acervo Liturgico Digital project.
"""

from .base import *  # noqa: F401, F403

# ==============================================================================
# GENERAL
# ==============================================================================

DEBUG = True

# ==============================================================================
# DJANGO DEBUG TOOLBAR
# ==============================================================================

try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ['debug_toolbar']  # noqa: F405
    MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')  # noqa: F405
    INTERNAL_IPS = ['127.0.0.1']
except ImportError:
    pass

# ==============================================================================
# EMAIL (console backend for development)
# ==============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
