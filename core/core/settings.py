"""
Django settings for core project.
Fixed & optimized for Windows + Tailwind + Hot Reload (Nov 2025)
"""

from pathlib import Path
import os
# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY
SECRET_KEY = 'django-insecure-7iue1t1p937up2%dn_l*=o)z8@e49ntb3-r!%f*+a&m8944091'
DEBUG = True
ALLOWED_HOSTS = ['localhost','lgu.labocamnorte.site','labocamnorte.site','https://lgu.labocamnorte.site','https://labocamnorte.site', '127.0.0.1','192.168.1.22','192.168.1.77','192.168.1.77:8000']
CSRF_TRUSTED_ORIGINS = [
    'https://lgu.labocamnorte.site',
    'https://labocamnorte.site',
    'http://labocamnorte.site',
    'https://www.labocamnorte.site',
    'http://www.labocamnorte.site',
]
# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # YOUR APP (fixed name!)
    'app.main',
    'app.user_auth',                
    'app.event',
    'app.education_assistance',
    'app.monitoring_api',
    # TAILWIND + HOT RELOAD
    'tailwind',
    'theme',                           
    'django_browser_reload',  
    # OTHERS UTILS
    'rest_framework', 
    'corsheaders',        
]

CORS_ALLOW_ALL_ORIGINS = True
NPM_BIN_PATH = r"C:\Program Files\nodejs\npm.cmd"
# Tailwind config
TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = ['127.0.0.1','lgu.labocamnorte.site','labocamnorte.site','https://lgu.labocamnorte.site','https://labocamnorte.site','192.168.1.22','192.168.1.77']  # Required for django-browser-reload

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Hot reload middleware (only added below in DEBUG)
]

# Add hot-reload only in DEBUG mode (and only once!)
if DEBUG:
    MIDDLEWARE += ['django_browser_reload.middleware.BrowserReloadMiddleware']

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],        # ← Fixed: Path object
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Database (MySQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lgu_main_system',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': '3306', 
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

BASE_DIR = Path(__file__).resolve().parent.parent



# Static & Media
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'