"""
Django settings for gestion_incidencias project.
"""

from pathlib import Path
import os
import environ

os.environ['GIO_USE_VFS'] = 'local'

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-fallback-key')

DEBUG = env('DEBUG', default=True)

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'tickets',
    'django_extensions',
]

AUTH_USER_MODEL = 'tickets.CustomUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'tickets.middleware.OnlinePresenceMiddleware',
    'tickets.middleware.ForzarCambioPasswordMiddleware',
]

ROOT_URLCONF = 'gestion_incidencias.urls'

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
                'tickets.context_processors.unread_notifications_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestion_incidencias.wsgi.application'
ASGI_APPLICATION = 'gestion_incidencias.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='incidencias_db'),
        'USER': env('DB_USER', default='incidencias_user'),
        'PASSWORD': env('DB_PASSWORD', default='incidencias_pass'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
# Asegúrate de que STATIC_ROOT esté definido aunque no uses collectstatic aún
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

DOT_BINARY_PATH = r'C:\Program Files\Graphviz\bin\dot.exe'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# En tu archivo settings.py
ALLOWED_HOSTS = ['192.168.1.8', 'localhost', '127.0.0.1']