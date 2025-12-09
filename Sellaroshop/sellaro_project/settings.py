"""
Django settings for sellaro_project.
"""

from pathlib import Path
import os
# Import environ and getenv for secure settings if using another library, 
# but os.environ.get is reliable for Render environment variables.

# Correct BASE_DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# 1. CRITICAL SECURITY FIX: Read SECRET_KEY from Environment Variable
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# 2. CRITICAL SECURITY FIX: Read DEBUG from Environment Variable
# When DEBUG=False is set in the environment, this evaluates to False.
DEBUG = os.environ.get('DEBUG') == 'True'

# 3. CRITICAL DEPLOYMENT FIX: Set ALLOWED_HOSTS for Render
# Use the URL sellaro.onrender.com
ALLOWED_HOSTS = ['sellaro.onrender.com', '127.0.0.1', 'localhost']


# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'shop_app',  # Make sure this is here
    'products',
    'store',
    # Ensure any installed package from requirements.txt that needs to be an app is here
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'sellaro_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'sellaro_project.wsgi.application'
ASGI_APPLICATION = 'sellaro_project.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'

USE_I18N = True
USE_TZ = True

# Static files settings
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles' # Crucial for collectstatic on Render

# Media files settings
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
