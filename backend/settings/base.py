import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-key")
DEBUG = bool(int(os.getenv("DJANGO_DEBUG", "1")))
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

DJANGO_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
	'rest_framework',
	'corsheaders',
	'drf_yasg',
	'django_filters',
	'rest_framework_simplejwt.token_blacklist',
]

LOCAL_APPS = [
	'backend.apps.users',
	'backend.apps.catalog',
	'backend.apps.orders',
	'backend.apps.reviews',
	'backend.apps.analytics',
	'backend.apps.core',
	'backend.apps.web',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
	'corsheaders.middleware.CorsMiddleware',
	'django.middleware.security.SecurityMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	'backend.apps.core.middleware.audit_middleware',
]

ROOT_URLCONF = 'backend.urls'
WSGI_APPLICATION = 'backend.wsgi.application'
ASGI_APPLICATION = 'backend.asgi.application'

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
			],
		},
	},
]

DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': os.getenv('POSTGRES_DB', 'bookstore'),
		'USER': os.getenv('POSTGRES_USER', 'bookstore'),
		'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'bookstore'),
		'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
		'PORT': os.getenv('POSTGRES_PORT', '5432'),
	}
}

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en-us')
TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
	'DEFAULT_AUTHENTICATION_CLASSES': (
		'rest_framework_simplejwt.authentication.JWTAuthentication',
	),
	'DEFAULT_PERMISSION_CLASSES': (
		'rest_framework.permissions.AllowAny',
	),
	'DEFAULT_FILTER_BACKENDS': (
		'django_filters.rest_framework.DjangoFilterBackend',
		'rest_framework.filters.SearchFilter',
		'rest_framework.filters.OrderingFilter',
	),
}

CORS_ALLOWED_ORIGINS = os.getenv('DJANGO_CORS_ORIGINS', '').split(',') if os.getenv('DJANGO_CORS_ORIGINS') else []

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Celery
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Channels
CHANNEL_LAYERS = {
	'default': {
		'BACKEND': 'channels_redis.core.RedisChannelLayer',
		'CONFIG': {
			'hosts': [REDIS_URL],
		},
	}
}

# Swagger
SWAGGER_SETTINGS = {
	'USE_SESSION_AUTH': False,
}
