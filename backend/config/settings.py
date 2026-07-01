"""
Django settings for config project.
Configuration centralisee via django-environ.
"""
import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- django-environ : lecture du fichier .env ---
# On declare les types attendus + valeurs par defaut de secours.
env = environ.Env(
    DJANGO_DEBUG=(bool, False),
)
# Lit backend/.env (a la racine du projet Django, a cote de manage.py)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
# Avant : cle en dur dans le code -> maintenant lue depuis .env
SECRET_KEY = env('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# Avant : DEBUG = True fige -> maintenant pilote par l'environnement
DEBUG = env('DJANGO_DEBUG')

# Avant : liste en dur -> maintenant lue depuis .env, separee par des virgules
ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',

    # Third-party
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_celery_beat',

    # Apps metier Ecotisac
    'apps.auth_user',
    'apps.deposits',
    'apps.recyclers',
    'apps.transactions',
    'apps.wallet',
    'apps.notifications',
    'apps.brands',
    'apps.messaging',
    'apps.admin_panel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # CorsMiddleware doit etre place le plus haut possible,
    # et avant CommonMiddleware si CORS_URLS_REGEX est utilise
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# Avant : os.environ.get(...) partout -> maintenant env(...) de django-environ
# Comportement identique, juste plus propre et coherent avec le reste
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': env('POSTGRES_DB', default='ecotisac'),
        'USER': env('POSTGRES_USER', default='ecotisac_user'),
        'PASSWORD': env('POSTGRES_PASSWORD', default='ecotisac_pass'),
        'HOST': env('POSTGRES_HOST', default='db'),
        'PORT': env('POSTGRES_PORT', default='5432'),
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
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Cache Redis
# Utilise pour le cache Django general et servira aussi pour l'OTP (SMS, 5 min)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{env('REDIS_HOST', default='localhost')}:{env('REDIS_PORT', default='6379')}/1",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
}

# Django REST Framework
REST_FRAMEWORK = {
    # Authentification obligatoire par defaut sur tous les endpoints.
    # Chaque endpoint public (ex: /api/auth/send-otp/) devra explicitement
    # declarer permission_classes = [AllowAny] dans sa vue.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # SimpleJWT comme methode d'authentification principale.
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # Pagination par defaut pour toutes les listes (deposits, offers, etc.)
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS
# Origines autorisees a appeler l'API depuis un navigateur (Next.js web + backoffice).
# Flutter (mobile) n'est pas concerne par CORS, cette protection ne s'applique
# qu'aux requetes emises depuis un navigateur.
CORS_ALLOWED_ORIGINS = env.list(
    'CORS_ALLOWED_ORIGINS',
    default=[
        'http://localhost:3000',   # Next.js frontend (dev)
        'http://localhost:3001',   # Next.js backoffice (dev)
    ],
)
CORS_ALLOW_CREDENTIALS = True

# Securite production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 an
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# Celery
# Avant : os.environ.get(...) -> maintenant env(...), comportement identique
CELERY_BROKER_URL = f"redis://{env('REDIS_HOST', default='localhost')}:{env('REDIS_PORT', default='6379')}/0"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# Logging
# Logs envoyes sur la console (stdout), captures automatiquement par
# `docker logs ecotisac_backend` -- pas besoin de fichiers de log en local.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': env('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}