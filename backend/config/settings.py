"""
Django settings for TenderBee backend.
Supports Neon Serverless PostgreSQL with pooling, Celery, DRF, SimpleJWT, and multi-tenant isolation.
"""
import os
import sys
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BASE_DIR.parent

# Ensure both backend/ and repo root are in python path
for p in (str(BASE_DIR), str(REPO_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Load environment variables
load_dotenv(REPO_ROOT / ".env")
load_dotenv()

# Security & Debug
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-tenderbee-core-deterministic-eval-platform-key-2026",
)
DEBUG = os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes")
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("ALLOWED_HOSTS", "*").split(",") if h.strip()]

# Application definition
INSTALLED_APPS = [
    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",

    # TenderBee domain apps
    "apps.accounts.apps.AccountsConfig",
    "apps.tenders.apps.TendersConfig",
    "apps.rules.apps.RulesConfig",
    "apps.documents.apps.DocumentsConfig",
    "apps.verify.apps.VerifyConfig",
    "apps.evidence.apps.EvidenceConfig",
    "apps.audit.apps.AuditConfig",
    "apps.find.apps.FindConfig",
    "apps.prepare.apps.PrepareConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.accounts.middleware.TenantContextMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# Database Configuration: Neon Serverless PostgreSQL with dual connections
# 1. DIRECT_URL: used for running migrations (session connection)
# 2. DATABASE_URL: used for application runtime (pooled connection)
is_migrating = any(arg in sys.argv for arg in ("migrate", "makemigrations"))
is_testing = any("test" in arg or "pytest" in arg for arg in sys.argv) or "pytest" in sys.modules
target_db_url = os.environ.get("DIRECT_URL") if is_migrating and os.environ.get("DIRECT_URL") else os.environ.get("DATABASE_URL")

# Short conn_max_age for serverless autoscaling / pooler suspension
conn_max_age = int(os.environ.get("CONN_MAX_AGE", 0))

if not is_testing and target_db_url and target_db_url.startswith("postgres") and "ep-sample" not in target_db_url:
    DATABASES = {
        "default": dj_database_url.config(
            default=target_db_url,
            conn_max_age=conn_max_age,
            ssl_require=True,
        )
    }
else:
    # Graceful fallback to SQLite for local development and testing
    data_dir = REPO_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    sqlite_path = data_dir / "tenderbee_dev.sqlite3"
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": str(sqlite_path),
        }
    }

# Custom User Model for Tenant Isolation & Organization Scoping
AUTH_USER_MODEL = "accounts.User"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = REPO_ROOT / "data" / "static"

# Media & Storage
MEDIA_URL = "/media/"
MEDIA_ROOT = REPO_ROOT / "data" / "media"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = os.environ.get("CORS_ALLOW_ALL", "True").lower() in ("true", "1")
CORS_ALLOW_CREDENTIALS = True

# REST Framework Configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# SimpleJWT Configuration with custom tenant claims
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.environ.get("JWT_ACCESS_MINUTES", 60))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.environ.get("JWT_REFRESH_DAYS", 7))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_USER_CLASS": "accounts.User",
}

# Celery Configuration
CELERY_BROKER_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
