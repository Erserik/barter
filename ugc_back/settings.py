import os
from pathlib import Path
import environ
from datetime import timedelta
from corsheaders.defaults import default_headers, default_methods

# ─── БАЗОВЫЕ ПУТИ ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent

# ─── ИНИЦИАЛИЗАЦИЯ django-environ ─────────────────────────────────────────────
env = environ.Env(
    DEBUG=(bool, False),
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# ─── СЕКРЕТЫ И РЕЖИМ ОТЛАДКИ ───────────────────────────────────────────────────
SECRET_KEY = env('SECRET_KEY')
DEBUG      = env('DEBUG')

ALLOWED_HOSTS = ['*']  # в продакшене лучше конкретизировать

# ─── ПОДКЛЮЧЁННЫЕ ПРИЛОЖЕНИЯ ────────────────────────────────────────────────────
INSTALLED_APPS = [
    'corsheaders',                   # <- CORS

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'drf_yasg',
    'channels',

    'accounts',

]

AUTH_USER_MODEL = 'accounts.CustomUser'

# ─── MIDDLEWARE ────────────────────────────────────────────────────────────────
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',         # <- CORS должен быть выше CommonMiddleware
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ugc_back.urls'
WSGI_APPLICATION = 'ugc_back.wsgi.application'

# ─── TEMPLATES ────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',   # обязательно для Admin
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ─── БАЗА ДАННЫХ ───────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE':   env('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME':     env('DB_NAME'),
        'USER':     env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST':     env('DB_HOST', default='localhost'),
        'PORT':     env('DB_PORT', default='5432'),
    }
}

# ─── ВАЛИДАЦИЯ ПАРОЛЕЙ ─────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── ЛОКАЛИЗАЦИЯ ───────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'en-us'
TIME_ZONE     = env('TIME_ZONE', default='UTC')
USE_I18N      = True
USE_TZ        = True

# ─── СТАТИКА И МЕДИА ───────────────────────────────────────────────────────────
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL   = '/media/'
MEDIA_ROOT  = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── DRF + JWT ─────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}

# ─── CORS ───────────────────────────────────────────────────────────────────────
# Разрешаем абсолютно всем запросы
CORS_ALLOW_ALL_ORIGINS = True

# Отключаем отправку куков/credentials
CORS_ALLOW_CREDENTIALS = False


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",         # ← твой фронтенд
    "https://tusapp.kz",             # ← если есть прод-фронт
    "https://dev.tusapp.kz",  # ← если есть прод-фронт
    "https://api.tusapp.kz"

]

CORS_ALLOW_HEADERS = list(default_headers) + [
    'authorization',
    'content-type',
]

CSRF_TRUSTED_ORIGINS = [
    "https://tusapp.kz",
    "https://dev.tusapp.kz",
    "https://api.tusapp.kz",
]

CORS_ALLOW_METHODS = list(default_methods)

# ─── ПРЕДЕЛЫ ЗАГРУЗКИ ───────────────────────────────────────────────────────────
# чтобы не получать 413 от Django
DATA_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 50 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 500 * 1024 * 1024  # 50 MB



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')  # укажи в .env
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')  # укажи в .env
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

ASGI_APPLICATION = 'ugc_back.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}