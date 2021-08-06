"""
Django settings for sizzy_lk project.

Generated by 'django-admin startproject' using Django 3.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from decouple import config

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '$#@!4_9^kzr-9+0-@ob-5=cx(!bv7lu*hzi0w(ayq+*2ltay)n'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['sizze.io', 'www.sizze.io', 'lk.sizze.io', 'www.lk.sizze.io', '127.0.0.1', '89.223.122.154']

LOGIN_URL = '/user/login/'
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'auth_users.apps.AuthConfig',
    'content.apps.ContentConfig',
    'api_redactor_app',
    'compressor',
    'tinymce',
    'nested_admin',
    'corsheaders',

    'reversion',
    'django_crontab',
    'rest_framework',
    'rest_framework.authtoken',
    'simple_sso.sso_server'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'api_redactor_app.middleware.cors_middleware.check_token_middleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
X_FRAME_OPTIONS = 'SAMEORIGIN'

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:8000",
#     "https://dashboard.sizze.io",
#     "https://romantic-thompson-d5f37d.netlify.app",
#     "https://sizze.io",
#     "https://lk.sizze.io",
#     "http://0.0.0.0:3000"
# ]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'sizzy_lk.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'sizzy_lk.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lk_sizze',
        'USER': 'sergey',
        'PASSWORD': 'sergey',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

AUTHENTICATION_BACKENDS = (
    'auth_users.auth_helpers.helpers.EmailBackend',
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

COMPRESS_ROOT = './content/static/'

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

STATIC_URL = '/static/'
STATIC_DIR = os.path.join(BASE_DIR, './static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "assets"),
]

STATIC_ROOT = 'static'

MEDIA_ROOT = './media/'
MEDIA_URL = '/media/'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# ПОКА ТЕСТ
EMAIL_HOST = 'mail.sizze.io'
EMAIL_PORT = '465'
EMAIL_HOST_USER = "support@sizze.io"
EMAIL_HOST_PASSWORD = config("smtp_password")
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = "mail.sizze.io"

TINYMCE_JS_URL = os.path.join(STATIC_URL, "tiny_mce/tiny_mce.js")
TINYMCE_JS_ROOT = os.path.join(STATIC_ROOT, "tiny_mce")
TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace,style, visualblocks, fullscreen",
    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    'extended_valid_elements': "svg[*],defs[*],pattern[*],desc[*],metadata[*],g[*],mask[*],path[*],line[*],marker[*],rect[*],circle[*],ellipse[*],polygon[*],polyline[*],linearGradient[*],radialGradient[*],stop[*],image[*],view[*],text[*],textPath[*],title[*],tspan[*],glyph[*],symbol[*],switch[*],use[*]"
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'auth_users.auth_helpers.helpers.TokenAuthSupportCookie',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'api_redactor_app.helpers.is_auth.IsAuthenticated',
    )
}

APPEND_SLASH = False
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

GOOGLE_PHOTO_API = {"web": {"client_id": "334729455720-v3rk8a7n810m2u52d7ekn5gr2q2rkqua.apps.googleusercontent.com",
                            "project_id": "sizze-photo", "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "client_secret": "6QHX7jQht8kLwY1PlXntC1pL", "redirect_uris": ["https://sizze.io/"]}}

GOOGLE_CLIENT_SECRET = 'dKKeVeH8zZWy9aBcfgKnO5a5'
GOOGLE_CLIENT_ID = '334729455720-d4pno273r6kaoe49cjautkg9isov59ke.apps.googleusercontent.com'

SILENCED_SYSTEM_CHECKS = ["auth.W004"]

CRONJOBS = [
    ('0 0 * * *', 'content.cron.delete_past_project', '>> /var/www/html/lk_sizze/cron.log'),
    ('0 0 * * *', 'content.cron.delete_past_tokens', '>> /var/www/html/lk_sizze/cron.log'),
    ('0 0 * * 2,4,6', 'content.cron.create_backup', '>> /var/www/html/lk_sizze/cron.log')
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console'
        },
        'auth': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'console',
            'filename': '/var/www/html/lk_sizze/logs/access.log'
        },
        'figma': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'console',
            'filename': '/var/www/html/lk_sizze/logs/figma.log'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'auth': {
            'handlers': ['auth'],
            'level': 'INFO'
        },
        'figma': {
            'handlers': ['figma'],
            'level': 'INFO'
        }
    },
}

FIGMA_SECRET = "mIiNtkfnRQxLTTUn4fPHjmG6iP0BEu"
FIGMA_CLIENT = "hZWPD96SWEmc4QnMGxpRcw"
FIGMA_REDIRECT_URI = "https://dashboard.sizze.io/0auth/callback"