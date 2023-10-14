from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="insecure-secret-key")

DEBUG = config('DEBUG', default=False, cast=bool)
LOCAL_DEVELOPMENT = config("LOCAL_DEVELOPMENT", default=False, cast=bool)

if LOCAL_DEVELOPMENT:
    ALLOWED_HOSTS = ['*']
else:
    ALLOWED_HOSTS = [".christcs.in"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.apps.web.apps.WebConfig',
    'core.apps.dashboard.apps.DashboardConfig',
    'django_hosts'
]

MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_hosts.middleware.HostsResponseMiddleware',
]

ROOT_URLCONF = 'core.urls'
DEFAULT_HOST = "www"
ROOT_HOSTCONF = "core.hosts"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


DATABASE_URL = config("DATABASE_URL")
DATABASES = {
    'default': dj_database_url.config(default=DATABASE_URL)
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'assets'
STATICFILES_DIRS = [BASE_DIR / 'static', ]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


DASHBOARD_URL = config('DASHBOARD_URL')
ENCRYPTION_SALT = config("ENCRYPTION_SALT")
ENCRYPTION_ITERATION = config("ENCRYPTION_ITERATION")

# PAYTM PAYMENTS CONFIG
PAYTM_MERCHANT_ID = config("PAYTM_MERCHANT_ID")
PAYTM_MERCHANT_KEY = config("PAYTM_MERCHANT_KEY")
PAYTM_CALLBACK_URL = DASHBOARD_URL + "/payments/handlers/"
PAYTM_PROCESS_TRANSACTION_URL = config("PAYTM_PROCESS_TRANSACTION_URL")

# GOOGLE OAUTH2 CONFIG
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
OAUTH_REDIRECTION_URL = DASHBOARD_URL + "/login/oauth2/google/"
GOOGLE_CLIENT_SECRET = {
    "web":
    {

        "client_id": GOOGLE_CLIENT_ID,
        "project_id": "erudite-spot-335720 ",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": config("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": [
            OAUTH_REDIRECTION_URL
        ]
     }
}
