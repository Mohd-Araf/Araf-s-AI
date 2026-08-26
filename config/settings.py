"""
Django settings for Araf's Assistant project.

Supports:
- Local development with SQLite
- Production deployment on Render
- PostgreSQL via DATABASE_URL
- WhiteNoise static files
- REST Framework
- CORS / CSRF
- Gemini / OpenAI AI configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# ============================================================
# BASE CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Load local .env file if it exists.
# On Render, Environment Variables are used instead.
load_dotenv(BASE_DIR / ".env")


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-arafs-assistant-development-key"
)

# IMPORTANT:
# Default is False for production safety.
DEBUG = os.getenv("DEBUG", "False").lower() in (
    "true",
    "1",
    "yes",
    "on",
)


# ------------------------------------------------------------
# Allowed Hosts
# ------------------------------------------------------------

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "127.0.0.1,localhost",
    ).split(",")
    if host.strip()
]


# ------------------------------------------------------------
# CSRF Trusted Origins
# ------------------------------------------------------------

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CSRF_TRUSTED_ORIGINS",
        "",
    ).split(",")
    if origin.strip()
]


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",

    # Local apps
    "accounts",
    "chatbot",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [
    # CORS should be near the top
    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise for static files
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL / WSGI / ASGI
# ============================================================

ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates",
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


if DATABASE_URL:
    try:
        import dj_database_url

        DATABASES = {
            "default": dj_database_url.parse(
                DATABASE_URL,
                conn_max_age=600,
                ssl_require=True,
            )
        }

    except ImportError:
        # Fallback if dj-database-url is not installed
        import urllib.parse as urlparse

        url = urlparse.urlparse(DATABASE_URL)

        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": url.path.lstrip("/"),
                "USER": url.username,
                "PASSWORD": url.password,
                "HOST": url.hostname,
                "PORT": url.port or "5432",
            }
        }

else:
    # Local development fallback
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 6,
        },
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME":
            "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"


# WhiteNoise
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },

    "staticfiles": {
        "BACKEND":
            "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],

    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}


# ============================================================
# CORS
# ============================================================

# For development you can allow all origins.
# For production, use CORS_ALLOWED_ORIGINS.

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False

    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "https://araf-s-ai.onrender.com",
        ).split(",")
        if origin.strip()
    ]


CORS_ALLOW_CREDENTIALS = True


# ============================================================
# AI CONFIGURATION
# ============================================================

def get_bool_env(name, default=False):
    """Safely convert an environment variable to boolean."""
    return os.getenv(name, str(default)).lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


def get_int_env(name, default=4):
    """Safely convert an environment variable to integer."""
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


AI_CONFIG = {
    # Gemini
    "GEMINI_API_KEY": os.getenv(
        "GEMINI_API_KEY",
        "",
    ),

    # OpenAI
    "OPENAI_API_KEY": os.getenv(
        "OPENAI_API_KEY",
        "",
    ),

    # Default AI model
    "DEFAULT_MODEL": os.getenv(
        "AI_DEFAULT_MODEL",
        "gemini-3.6-flash",
    ),

    # Web search
    "ENABLE_WEB_SEARCH": get_bool_env(
        "ENABLE_WEB_SEARCH",
        True,
    ),

    # Maximum search results
    "MAX_SEARCH_RESULTS": get_int_env(
        "MAX_SEARCH_RESULTS",
        4,
    ),

    # Assistant name
    "ASSISTANT_NAME": "Araf's Assistant",
}


# ============================================================
# PRODUCTION SECURITY
# ============================================================

if not DEBUG:

    # Render provides HTTPS
    SECURE_SSL_REDIRECT = True

    # Secure cookies
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    # Browser security
    SECURE_BROWSER_XSS_FILTER = True

    # Prevent MIME-type sniffing
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Referrer policy
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

    # HSTS
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# ============================================================
# DEVELOPMENT OVERRIDES
# ============================================================

if DEBUG:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
