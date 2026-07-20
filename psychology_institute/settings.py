# Import necessary modules
import os
from pathlib import Path
from datetime import timedelta
from decouple import Csv, Config, RepositoryEnv


#some necessary variables
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_DIR = BASE_DIR / 'dependencies'


# ENV_FILE_PATH
if os.getenv('DJANGO_USE_DEV_ENV') == 'true':
    ENV_FILE = 'dev.env'  # Development mode
else:
    ENV_FILE = '.env'  # Production mode


# CONFIG
ENV_FILE_PATH = ENV_DIR / ENV_FILE
repository = RepositoryEnv(str(ENV_FILE_PATH))
config = Config(repository)


# SECRET_KEY and DEBUG
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)


# ALLOWED_HOSTS
ALLOWED_HOSTS = [
    'sarmadclinic.ir',
    'www.sarmadclinic.ir',
    'localhost',
    '127.0.0.1',
    '185.8.175.241',
]


# APPLICATIONS
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap5',
    'widget_tweaks',
    'jalali_date',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'django_extensions',
    'django_celery_beat',
    
    # Local apps
    'app.blog',
    'app.courses',
    'app.dashboard',
    'app.payment',
    'app.reports',
    'app.sales',
    'app.admin_panel',
    'app.workshops',
    'app.packages',
    'app.appointments',
    'app.chat',
    'app.mmpi',
    'psychology_institute.apps.PsychologyInstituteConfig',

]


# MIDDLEWARE
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ROOT_URLCONF
ROOT_URLCONF = 'psychology_institute.urls'


# TEMPLATES
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'dependencies/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]


# WSGI
WSGI_APPLICATION = 'psychology_institute.wsgi.application'


# DATABASE
DATABASES = {
    'default': {
        'ENGINE': config('DATABASE_ENGINE', default='django.db.backends.postgresql'),
        'NAME': config('DB_NAME', default='psychology_institute'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'app.dashboard.validators.PersianUserAttributeSimilarityValidator',
    },
    {
        'NAME': 'app.dashboard.validators.PersianMinimumLengthValidator',
    },
    {
        'NAME': 'app.dashboard.validators.PersianCommonPasswordValidator',
    },
    {
        'NAME': 'app.dashboard.validators.PersianNumericPasswordValidator',
    },
]


# INTERNATIONALIZATION
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGE_BIDI = True
LANGUAGES = [
    ('fa', 'فارسی'),
    ('en', 'English'),
]


# LOCALE
LOCALE_PATHS = [
    BASE_DIR / 'dependencies/locale',
]


# STATIC
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'dependencies/static',
]


# MEDIA
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'dependencies/media'


# AUTO_FIELD
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# AUTH_USER_MODEL
AUTH_USER_MODEL = 'dashboard.User'


# AUTHENTICATION_BACKENDS
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]


# SITE_ID
SITE_ID = 1


# ACCOUNT_EMAIL_VERIFICATION
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'


# ACCOUNT_UNIQUE_EMAIL
ACCOUNT_UNIQUE_EMAIL = True


# ACCOUNT_USER_MODEL_USERNAME_FIELD
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'


# ACCOUNT_LOGIN_METHODS
ACCOUNT_LOGIN_METHODS = {'email'}


# ACCOUNT_SIGNUP_FIELDS
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']


# Login URLs
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


# CRISPY
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# REST_FRAMEWORK
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',

    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "http://localhost:3010",
    "http://127.0.0.1:3010",
    "http://185.8.175.241:3000",
    "http://sarmadclinic.ir",
    "https://sarmadclinic.ir",
    "http://www.sarmadclinic.ir",
    "https://www.sarmadclinic.ir",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = DEBUG  


# CSRF
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:3001',
    'http://127.0.0.1:3001',
    'http://localhost:3010',  
    'http://127.0.0.1:3010',
    'http://185.8.175.241',
    'http://185.8.175.241:3000',
    'http://185.8.175.241:8000',
    'http://sarmadclinic.ir',
    'https://sarmadclinic.ir',
    'http://www.sarmadclinic.ir',
    'https://www.sarmadclinic.ir',
]
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_NAME = 'csrftoken'
SESSION_COOKIE_SAMESITE = 'Lax'


# X_FORWARDED
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # For HTTPS behind reverse proxy
FORCE_SCRIPT_NAME = ''  # Empty string means use relative URLs

DEVELOPMENT_MODE = config('DEVELOPMENT_MODE', default=DEBUG, cast=bool)


# SECURITY
if not DEBUG and not DEVELOPMENT_MODE:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
else:
    # Disable SSL redirect in development
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0

SESSION_COOKIE_SECURE = not DEVELOPMENT_MODE  # F in dev, T in pro
CSRF_COOKIE_SECURE = not DEVELOPMENT_MODE  # F in dev, T in pro


# CELERY
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE


# EMAIL
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@sarmadclinic.ir')


# SMS
SMS_PROVIDER_WSDL = config('SMS_PROVIDER_WSDL', default='http://www.sepahansms.com/smsSendWebServiceforphp.asmx?wsdl')
SMS_USERNAME = config('SMS_USERNAME', default='')
SMS_PASSWORD = config('SMS_PASSWORD', default='')
SMS_DOMAIN = config('SMS_DOMAIN', default='sepahansms')
SMS_SENDER_NUMBER = config('SMS_SENDER_NUMBER', default='')
SEPAHANGOSTAR_API_BASE = config('SEPAHANGOSTAR_API_BASE', default='https://api.sepahansms.com')
SEPAHANGOSTAR_API_TOKEN = config('SEPAHANGOSTAR_API_TOKEN', default='')
SEPAHANGOSTAR_SENDER_NUMBER = config('SEPAHANGOSTAR_SENDER_NUMBER', default='')


# OTP
OTP_EXPIRE_SECONDS = int(config('OTP_EXPIRE_SECONDS', default='180'))
OTP_RESEND_COOLDOWN_SECONDS = int(config('OTP_RESEND_COOLDOWN_SECONDS', default='60'))
OTP_MAX_ATTEMPTS = int(config('OTP_MAX_ATTEMPTS', default='5'))


# SECURE
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'


# CACHES
try:
    import redis
    redis.Redis(host='localhost', port=6379, db=1).ping()
    # Redis is available, use it
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    SESSION_CACHE_ALIAS = 'default'
except (ImportError, redis.ConnectionError, redis.RedisError):
    # Redis is not available, use local memory cache
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
    SESSION_ENGINE = 'django.contrib.sessions.backends.db'

SESSION_COOKIE_AGE = 86400  #(24 hours)


# CROOM
CROOM_API_KEY = config('CROOM_API_KEY', default='')
CROOM_API_URL = config('CROOM_API_URL', default='')


# JALALI_DATE
JALALI_DATE_DEFAULT_GEOGRAPHIC_ZONE = 'Asia/Tehran'
JALALI_DATE_DEFAULT_FORMAT = '%Y/%m/%d'
JALALI_DATE_DEFAULT_DATETIME_FORMAT = '%Y/%m/%d %H:%M:%S'
JALALI_DATE_DEFAULT_DATE_FORMAT = '%Y/%m/%d'
JALALI_DATE_DEFAULT_TIME_FORMAT = '%H:%M:%S'


# ZARINPAL
ZARINPAL_MERCHANT_ID = config('ZARINPAL_MERCHANT_ID')
ZARINPAL_SANDBOX = config('ZARINPAL_SANDBOX', cast=bool)


# SITE and FRONTEND
SITE_URL = config('SITE_URL', default='https://sarmadclinic.ir')
FRONTEND_URL = config('FRONTEND_URL', default='https://sarmadclinic.ir')
ZARINPAL_CALLBACK_URL = config(
    'ZARINPAL_CALLBACK_URL', 
    default=f'{SITE_URL}/api/payment/verify/'
)