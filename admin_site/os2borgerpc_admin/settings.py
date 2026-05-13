# Django settings for OS2borgerPC admin project.

import logging
import os
from datetime import datetime
from pathlib import Path

if os.environ.get("GS_BUCKET_NAME"):
    # Importing it here so it's not a hard requirement
    from google.oauth2 import service_account

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

# Our customized user profile.
AUTH_PROFILE_MODULE = "account.UserProfile"


DEBUG = os.environ.get("DEBUG") == "True"

ADMINS = (
    [
        (os.environ.get("ADMIN_NAME"), os.environ.get("ADMIN_EMAIL")),
    ]
    if os.environ.get("ADMIN_EMAIL")
    else None
)

MANAGERS = ADMINS

# By default Django uses "cached.Loader"
# which caches templates quite aggressively.
# Unfortunately it doesn't include proper detection
# for html file changes, which causes
# the served templates to poorly update when doing frontend work
#
# We used to work around this by changing
# the gunicorn settings to --max-requests 1 and --workers 1,
# which forced a reset through gunicorn.
# That also made the web page *really* slow
# in development since gunicorn spent most of the time
# recreating workers, which was not ideal
#
# Caching is of course desired in production,
# so we just change between cached and
# not cached loader depending on debug environment
#
# Related docs: https://docs.djangoproject.com/en/6.0/ref/templates/api/#django.template.loaders.cached.Loader
base_loaders = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

production_loaders = [("django.template.loaders.cached.Loader", base_loaders)]

# Template settings
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates/",
        ],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": [
                "system.templatetags.custom_tags",
            ],
            "loaders": base_loaders if DEBUG else production_loaders,
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME"),
        "USER": os.environ.get("DB_USER"),
        "PASSWORD": os.environ.get("DB_PASSWORD"),
        "HOST": os.environ.get("DB_HOST"),
        "PORT": os.environ.get("DB_PORT", ""),
        "OPTIONS": {
            "connect_timeout": 30,  # Minimum is 2
        },
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts
if os.environ.get("ALLOWED_HOSTS"):
    ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(",")
else:
    ALLOWED_HOSTS = []

# Django > 4.0 introduced changes related to CSRF. Note that the protocol has to be specified too.
# https://docs.djangoproject.com/en/4.2/releases/4.0/#csrf
# https://docs.djangoproject.com/en/4.2/ref/settings/#csrf-trusted-origins
if os.environ.get("CSRF_TRUSTED_ORIGINS"):
    CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS").split(",")
else:
    CSRF_TRUSTED_ORIGINS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
# Timezone/Language
TIME_ZONE = os.environ.get("TIME_ZONE")

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE")

LOCALE_PATHS = [BASE_DIR / "locale"]

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = "/media"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = "/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = "/static"

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = "/static/"

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_DIR / "static",
    "/frontend",
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)


# Storage setup
if os.environ.get("GS_BUCKET_NAME"):
    # The Google Cloud Storage bucket name. For `django-storages[google]`
    # https://django-storages.readthedocs.io/en/latest/backends/gcloud.html
    # If it is set, we save all files to Google Cloud.
    DEFAULT_FILE_STORAGE = "storages.backends.gcloud.GoogleCloudStorage"
    GS_BUCKET_NAME = os.environ.get("GS_BUCKET_NAME")
    GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
        os.environ.get("GS_CREDENTIALS_FILE")
    )
    GS_QUERYSTRING_AUTH = False
    GS_FILE_OVERWRITE = False
    GS_CUSTOM_ENDPOINT = os.environ.get("GS_CUSTOM_ENDPOINT")

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.environ.get("SECRET_KEY")

MIDDLEWARE = (
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "os2borgerpc_admin.middlewares.user_locale_middleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "mozilla_django_oidc.middleware.SessionRefresh",
)

# Email settings

# FROM field for regular e-mails sent by django. Ought to match the SMTP user.
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
# FROM field for server-error emails (see mail_admins). Ought to match the SMTP user
SERVER_EMAIL = os.environ.get("SERVER_EMAIL")
# The recipient for server error e-mails
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
# SMTP host/username/password
EMAIL_HOST = os.environ.get("EMAIL_HOST")
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD")
# Django's default email backend
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

ROOT_URLCONF = "os2borgerpc_admin.urls"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "os2borgerc_admin.wsgi.application"


LOCAL_APPS = (
    "account",
    "changelog",
    "docs",
    "system",
)

THIRD_PARTY_APPS = (
    "crispy_forms",
    "crispy_bootstrap5",
    "markdownx",
    "django_otp",
    "django_otp.plugins.otp_static",
    "django_otp.plugins.otp_totp",
    "two_factor",
    "mozilla_django_oidc",
)

DJANGO_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
)

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Django's logging is basically Python's logging with only a few additions.
# The below config sends an email to the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "bpc": {
            # https://docs.python.org/3/library/logging.html#levels
            "format": "{levelname} {asctime} {message}",
            "style": "{",
        }
    },
    "filters": {
        # This is a default filter - filtering away all logs when Debug=TRUE
        "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}
    },
    "handlers": {
        # mail_admins is default
        # Uses the default formatter, which is only the message
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        # Changes the formatter from the default "console" handler
        "custom_console": {
            "class": "logging.StreamHandler",
            "formatter": "bpc",
        },
    },
    "loggers": {
        # This is not default
        "django.db.backends": {
            "level": os.environ.get("DB_LOG_LEVEL", "CRITICAL"),
            "handlers": ["custom_console"],
            "propagate": False,
        },
    },
    # This is not default
    "root": {
        "handlers": ["custom_console", "mail_admins"],
        "level": os.environ.get("LOG_LEVEL", "ERROR"),
    },
}

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Handler for citizen login.
CITIZEN_LOGIN_API_VALIDATOR = os.environ.get(
    "CITIZEN_LOGIN_API_VALIDATOR", "system.utils.cicero_validate"
)

# Cicero specific stuff.
CICERO_URL = os.environ.get("CICERO_URL")

# All Python Markdown's officially supported extensions can be added here without
# any extra setup.
# Third-party extensions can also be imported and used, asuming they (and their
# dependencies) are installed.
MARKDOWNX_MARKDOWN_EXTENSIONS = [
    "extra",
]

MARKDOWNX_IMAGE_MAX_SIZE = {"size": (800, 800), "quality": 90}

# This specifies where uploaded media (images) are stored
MARKDOWNX_MEDIA_PATH = datetime.now().strftime("changelog-images/%Y/%m/%d")

FORM_RENDERER = "django.forms.renderers.DjangoDivFormRenderer"

LOGIN_REDIRECT_URL = "/"
# Only called when SSO logins fail
LOGIN_REDIRECT_URL_FAILURE = "/accounts/sso-login-error/"

# SSO
OIDC_RP_CLIENT_ID = os.environ.get("OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = os.environ.get("OIDC_RP_CLIENT_SECRET")
OIDC_OP_AUTHORIZATION_ENDPOINT = os.environ.get("OIDC_OP_AUTHORIZATION_ENDPOINT")
OIDC_OP_TOKEN_ENDPOINT = os.environ.get("OIDC_OP_TOKEN_ENDPOINT")
OIDC_OP_USER_ENDPOINT = os.environ.get("OIDC_OP_USER_ENDPOINT")
OIDC_RP_SIGN_ALGO = os.environ.get("OIDC_RP_SIGN_ALGO")
OIDC_OP_JWKS_ENDPOINT = os.environ.get("OIDC_OP_JWKS_ENDPOINT")
AUTHENTICATION_BACKENDS = [
    "account.auth.MyOIDCAB",
    "django.contrib.auth.backends.ModelBackend",
]
OIDC_USE_PKCE = os.environ.get("OIDC_USE_PKCE")
OIDC_CUSTOMER = os.environ.get("OIDC_CUSTOMER")

if os.environ.get("SECURE_PROXY_SSL_HEADER"):
    SECURE_PROXY_SSL_HEADER = os.environ.get("SECURE_PROXY_SSL_HEADER").split(",")
else:
    SECURE_PROXY_SSL_HEADER = None
