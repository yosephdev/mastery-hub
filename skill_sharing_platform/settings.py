import os
import sys
import warnings
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

# ── Core ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

_SECRET_KEY_DEFAULT = "django-insecure-dev-fallback-key-change-me-in-production"
SECRET_KEY = os.getenv("SECRET_KEY", _SECRET_KEY_DEFAULT)
if SECRET_KEY == _SECRET_KEY_DEFAULT:
    warnings.warn(
        "SECRET_KEY is using the insecure development default. "
        "Set the SECRET_KEY environment variable before deploying.",
        stacklevel=1,
    )

DEBUG = os.getenv("DEBUG", "False").strip().lower() in ("true", "1", "yes")

ROOT_URLCONF = "skill_sharing_platform.urls"
WSGI_APPLICATION = "skill_sharing_platform.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ── Hosts & CSRF ─────────────────────────────────────────────────────────────
ALLOWED_HOSTS = [
    h.strip()
    for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if h.strip()
]

_csrf_env = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_env.split(",") if o.strip()]

# ── Applications ─────────────────────────────────────────────────────────────
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

# ── Middleware ────────────────────────────────────────────────────────────────
# WhiteNoiseMiddleware must be immediately after SecurityMiddleware.
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
]

# ── Database ──────────────────────────────────────────────────────────────────
# Uses DATABASE_URL env var (Coolify injects this automatically when a
# PostgreSQL service is linked). Falls back to SQLite for local development.
#
# DB_SSLMODE defaults to "require" for production (Coolify/managed Postgres).
# Set DB_SSLMODE=disable in docker-compose.yml for local dev where the
# Postgres container does not have SSL configured.
_database_url = os.getenv("DATABASE_URL")
_db_sslmode = os.getenv("DB_SSLMODE", "require")

if _database_url:
    _db = urlparse(_database_url)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _db.path[1:],
            "USER": _db.username,
            "PASSWORD": _db.password,
            "HOST": _db.hostname,
            "PORT": _db.port or 5432,
            "OPTIONS": {"sslmode": _db_sslmode},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

if "test" in sys.argv:
    _test_db_url = os.getenv("TEST_DATABASE_URL", _database_url)
    if _test_db_url:
        _tdb = urlparse(_test_db_url)
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": _tdb.path[1:],
                "USER": _tdb.username,
                "PASSWORD": _tdb.password,
                "HOST": _tdb.hostname,
                "PORT": _tdb.port or 5432,
                "OPTIONS": {"sslmode": _db_sslmode},
            }
        }
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# ── Authentication ────────────────────────────────────────────────────────────
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "accounts.backends.EmailOrUsernameModelBackend",
]

LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "home:index"
LOGOUT_REDIRECT_URL = "home:index"
LOGOUT_URL = "accounts:logout"

ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ.get("SOCIALACCOUNT_GOOGLE_CLIENT_ID"),
            "secret": os.environ.get("SOCIALACCOUNT_GOOGLE_SECRET"),
            "key": "",
        },
        "SCOPE": ["profile", "email", "openid"],
        "AUTH_PARAMS": {
            "access_type": "online",
            "prompt": "consent",
            "include_granted_scopes": "true",
        },
        "OAUTH_PKCE_ENABLED": True,
        "STATE": os.environ.get("SOCIALACCOUNT_STATE", "randomstring"),
    }
}

SITE_ID = 1

# ── Email ─────────────────────────────────────────────────────────────────────
if DEBUG or "DEVELOPMENT" in os.environ:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = "smtp.postmarkapp.com"
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.getenv("POSTMARK_ACCESS_KEY")
    EMAIL_HOST_PASSWORD = os.getenv("POSTMARK_SECRET_KEY")
    DEFAULT_FROM_EMAIL = "contact@yoseph.dev"
    SERVER_EMAIL = DEFAULT_FROM_EMAIL

EMAIL_SUBJECT_PREFIX = "[MasteryHub] "

# ── Stripe ────────────────────────────────────────────────────────────────────
STRIPE_CURRENCY = "usd"
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_WH_SECRET = os.environ.get("STRIPE_WH_SECRET")

# ── Static & Media files ──────────────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# AWS S3 — activated by setting USE_AWS=True in env
if os.getenv("USE_AWS", "False").strip().lower() in ("true", "1", "yes"):
    AWS_S3_OBJECT_PARAMETERS = {
        "Expires": "Thu, 31 Dec 2099 20:00:00 GMT",
        "CacheControl": "max-age=94608000",
    }
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "skill-sharing")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "eu-west-1")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

    STATICFILES_STORAGE = "custom_storages.StaticStorage"
    STATICFILES_LOCATION = "static"
    DEFAULT_FILE_STORAGE = "custom_storages.MediaStorage"
    MEDIAFILES_LOCATION = "media"

    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{STATICFILES_LOCATION}/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{MEDIAFILES_LOCATION}/"

# ── Security ──────────────────────────────────────────────────────────────────
# The app runs behind Coolify's Traefik reverse proxy which terminates TLS.
# Traefik handles the HTTPS redirect — do NOT set SECURE_SSL_REDIRECT=True
# or requests will loop. Traefik sets X-Forwarded-Proto so Django knows the
# original scheme was HTTPS.
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

if not DEBUG:
    SECURE_SSL_REDIRECT = False          # Traefik handles HTTPS redirect
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    SECURE_HSTS_SECONDS = 31536000       # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ── Logging ───────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["console", "mail_admins"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django.security": {
            "handlers": ["console", "mail_admins"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

# ── Internationalisation ──────────────────────────────────────────────────────
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ── Site meta ─────────────────────────────────────────────────────────────────
SITE_NAME = "MasteryHub"
SITE_DOMAIN = os.getenv("SITE_DOMAIN", "localhost:8000" if DEBUG else "yourdomain.com")

# ── Templates ─────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "templates", "allauth"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "checkout.context_processors.cart_contents",
                "checkout.context_processors.message_processor",
                "checkout.context_processors.project_context",
            ],
        },
    },
]

# ── Crispy Forms ──────────────────────────────────────────────────────────────
CRISPY_TEMPLATE_PACK = "bootstrap5"
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

# ── Sessions ──────────────────────────────────────────────────────────────────
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 86400
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_SAVE_EVERY_REQUEST = True

# ── CSRF ──────────────────────────────────────────────────────────────────────
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
