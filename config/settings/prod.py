"""
Django production settings for Acervo Liturgico Digital project.
Otimizado para deploy no Railway.
"""

import dj_database_url

from .base import *  # noqa: F401, F403

# ==============================================================================
# GENERAL
# ==============================================================================

DEBUG = False

# ==============================================================================
# DATABASE — Railway fornece DATABASE_URL automaticamente
# ==============================================================================

DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.parse(
        DATABASE_URL, conn_max_age=600, conn_health_checks=True
    )

# ==============================================================================
# STATIC FILES — Whitenoise serve arquivos estáticos sem Nginx
# ==============================================================================

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STORAGES = {
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# ==============================================================================
# SECURITY
# ==============================================================================

SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = 'DENY'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Railway gera domínios *.up.railway.app
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='',
    cast=lambda v: [s.strip() for s in v.split(',') if s.strip()] if v else [],
)

# ==============================================================================
# LOGGING
# ==============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# ==============================================================================
# EMAIL
# ==============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
