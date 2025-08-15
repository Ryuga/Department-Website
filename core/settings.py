from pathlib import Path
from decouple import config
import dj_database_url

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
    'django_hosts',
]

MIDDLEWARE = [
    'django_hosts.middleware.HostsRequestMiddleware',
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
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
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

DASHBOARD_URL = config('DASHBOARD_URL')
ENCRYPTION_SALT = config("ENCRYPTION_SALT")
ENCRYPTION_ITERATION = config("ENCRYPTION_ITERATION")

# PAYTM PAYMENTS CONFIG
PAYTM_MERCHANT_ID = config("PAYTM_MERCHANT_ID")
PAYTM_MERCHANT_KEY = config("PAYTM_MERCHANT_KEY")
PAYTM_CALLBACK_URL = DASHBOARD_URL + "/payments/handlers/"
PAYTM_BASE_URL = "https://securegw-stage.paytm.in" if LOCAL_DEVELOPMENT else "https://securegw.paytm.in"


PAYTM_INITIATE_TRANSACTION_URL = f"{PAYTM_BASE_URL}/theia/api/v1/initiateTransaction?mid={PAYTM_MERCHANT_ID}"
PAYTM_SHOW_PAYMENTS_PAGE_URL = f"{PAYTM_BASE_URL}/theia/api/v1/showPaymentPage?mid={PAYTM_MERCHANT_ID}"

# GOOGLE OAUTH2 CONFIG
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
OAUTH_REDIRECTION_URL = DASHBOARD_URL + "/login/oauth2/google/"
GOOGLE_CLIENT_SECRET = {
    "web":
    {

        "client_id": GOOGLE_CLIENT_ID,
        "project_id": "department-website-401919",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": config("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": [
            OAUTH_REDIRECTION_URL
        ]
     }
}


#Celery Config
CELERY_BROKER_URL = config("REDIS_URL")
CELERY_RESULT_BACKEND = config("REDIS_URL")
CELERY_TIMEZONE = 'Asia/Kolkata'


#Email Config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.zoho.in"
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_CDN_URL = config("DEFAULT_CDN_URL")

CSRF_TRUSTED_ORIGINS = [
    "https://dashboard.christcs.in",
    "https://admin.christcs.in",
    "https://zephyrus.christcs.in",
]
