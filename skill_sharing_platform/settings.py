import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# Core Django Settings
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = True
ROOT_URLCONF = "skill_sharing_platform.urls"
WSGI_APPLICATION = "skill_sharing_platform.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Host Settings
ALLOWED_HOSTS = os.getenv(
    "ALLOWED_HOSTS",
    "localhost,127.0.0.1,127.0.0.1:3000,8000-yosephdev-masteryhub-xw239vmyc5m.ws.codeinstitute-ide.net,.herokuapp.com"
).split(",")

CSRF_TRUSTED_ORIGINS = [
    "https://8000-yosephdev-masteryhub-xw239vmyc5m.ws.codeinstitute-ide.net",
    "https://skill-sharing-446c0336ffb5.herokuapp.com",
]

# Application Definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Third-party
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "django_extensions",
    "rest_framework",
    "corsheaders",
    "stripe",
    "crispy_forms",
    "crispy_bootstrap5",
    "storages",
    "django_countries",
    "sslserver",
    "widget_tweaks",

    # Local
    "profiles",
    "masteryhub",
    "home",
    "checkout",
    "accounts",
]

# Middleware Configuration
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "masteryhub.middleware.BrotliMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

# Database Configuration
tmpPostgres = urlparse(os.getenv("DATABASE_URL"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': tmpPostgres.path[1:],
        'USER': tmpPostgres.username,
        'PASSWORD': tmpPostgres.password,
        'HOST': tmpPostgres.hostname,
        'PORT': tmpPostgres.port or 5432,
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Handle test database settings
if "test" in sys.argv:
    tmpPostgresTest = urlparse(
        os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL")))

    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": tmpPostgresTest.path[1:],
            "USER": tmpPostgresTest.username,
            "PASSWORD": tmpPostgresTest.password,
            "HOST": tmpPostgresTest.hostname,
            "PORT": tmpPostgresTest.port or 5432,
            "OPTIONS": {
                "sslmode": "require",
            },
        }
    }

    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Authentication Settings
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "accounts.backends.EmailOrUsernameModelBackend",
]

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'home:index'
LOGOUT_REDIRECT_URL = 'home:index'
LOGOUT_URL = 'accounts:logout'

# AllAuth Settings
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False

# Google OAuth2 Settings
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ.get('SOCIALACCOUNT_GOOGLE_CLIENT_ID'),
            'secret': os.environ.get('SOCIALACCOUNT_GOOGLE_SECRET'),
            'key': ''
        },
        'SCOPE': [
            'profile',
            'email',
            'openid',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
            'prompt': 'consent',
            'include_granted_scopes': 'true'
        },
        'OAUTH_PKCE_ENABLED': True,  # Ensures better security
        # Prevents CSRF errors
        'STATE': os.environ.get('SOCIALACCOUNT_STATE', 'randomstring'),
    }
}

# Site ID for django.contrib.sites
SITE_ID = 1

# Email Configuration
if DEBUG or 'DEVELOPMENT' in os.environ:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    DEFAULT_FROM_EMAIL = 'masteryhub@example.com'
    SERVER_EMAIL = DEFAULT_FROM_EMAIL
else:
    EMAIL_BACKEND = 'postmark.django.backend.EmailBackend'
    POSTMARK_API_KEY = os.environ.get('POSTMARK_API_KEY')

    DEFAULT_FROM_EMAIL = 'contact@yoseph.dev'
    SERVER_EMAIL = DEFAULT_FROM_EMAIL
  
# Email Subject Prefix
EMAIL_SUBJECT_PREFIX = '[MasteryHub] '

# Stripe Configuration
STRIPE_CURRENCY = 'usd'
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_WH_SECRET = os.environ.get('STRIPE_WH_SECRET')

# Files Storage Settings
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# AWS Configuration
if "USE_AWS" in os.environ:
    AWS_S3_OBJECT_PARAMETERS = {
        "Expires": "Thu, 31 Dec 2099 20:00:00 GMT",
        "CacheControl": "max-age=94608000",
    }
    AWS_STORAGE_BUCKET_NAME = "skill-sharing"
    AWS_S3_REGION_NAME = "eu-west-1"
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

    STATICFILES_STORAGE = "custom_storages.StaticStorage"
    STATICFILES_LOCATION = "static"
    DEFAULT_FILE_STORAGE = "custom_storages.MediaStorage"
    MEDIAFILES_LOCATION = "media"

    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STATICFILES_LOCATION}/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIAFILES_LOCATION}/"

# Security Settings
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Email Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.mail': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# Additional Settings
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
SITE_NAME = 'MasteryHub'
SITE_DOMAIN = 'localhost:8000' if DEBUG else 'skill-sharing-446c0336ffb5.herokuapp.com'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates', 'allauth'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'checkout.context_processors.cart_contents',
                'checkout.context_processors.message_processor',
                'checkout.context_processors.project_context',
            ],
        },
    },
]

# Crispy Forms Settings
CRISPY_TEMPLATE_PACK = 'bootstrap5'
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# Session Settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = True

# Security Settings
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = ['https://skill-sharing-446c0336ffb5.herokuapp.com']
