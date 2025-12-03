import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

# Загружаем .env
load_dotenv()

# --- ПУТИ ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- БЕЗОПАСНОСТЬ ---
SECRET_KEY = os.environ.get('SECRET_KEY', get_random_secret_key())
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# --- ALLOWED_HOSTS ---
ALLOWED_HOSTS_ENV = os.environ.get('ALLOWED_HOSTS', '')
if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(',')]
else:
    ALLOWED_HOSTS = ['*']

# Автоматическое добавление хостов Render
render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if render_host:
    if render_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(render_host)
    if '*.onrender.com' not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append('*.onrender.com')

# Безопасность для production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# --- УСТАНОВЛЕННЫЕ ПРИЛОЖЕНИЯ ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
]

# --- МИДЛВАР ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'uniquest.urls'

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

WSGI_APPLICATION = 'uniquest.wsgi.application'

# --- БАЗА ДАННЫХ ---
# Приоритет: DATABASE_URL (от Render) > отдельные переменные > значения по умолчанию
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'uniquestus'),
        'USER': os.environ.get('DB_USER', 'uniquest_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
        'CONN_MAX_AGE': 600,
    }
}

# Использование DATABASE_URL от Render (приоритет)
if 'DATABASE_URL' in os.environ:
    try:
        import dj_database_url
        DATABASES['default'] = dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    except ImportError:
        # Если dj-database-url не установлен, парсим вручную
        import urllib.parse
        db_url = os.environ.get('DATABASE_URL')
        if db_url:
            parsed = urllib.parse.urlparse(db_url)
            DATABASES['default'] = {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': parsed.path[1:] if parsed.path.startswith('/') else parsed.path,
                'USER': parsed.username,
                'PASSWORD': parsed.password,
                'HOST': parsed.hostname,
                'PORT': parsed.port or '5432',
                'OPTIONS': {
                    'connect_timeout': 10,
                },
                'CONN_MAX_AGE': 600,
            }
else:
    # Если DATABASE_URL не установлен, используем отдельные переменные
    # Проверяем, что есть хотя бы HOST (не localhost) или PASSWORD (значит настроено)
    db_host = os.environ.get('DB_HOST', '')
    db_password = os.environ.get('DB_PASSWORD', '')
    
    if db_host and db_host != 'localhost' and 'localhost' not in db_host:
        # Используем отдельные переменные если HOST указан и не localhost
        DATABASES['default'].update({
            'NAME': os.environ.get('DB_NAME', DATABASES['default']['NAME']),
            'USER': os.environ.get('DB_USER', DATABASES['default']['USER']),
            'PASSWORD': db_password or DATABASES['default']['PASSWORD'],
            'HOST': db_host,
            'PORT': os.environ.get('DB_PORT', DATABASES['default']['PORT']),
        })
    elif db_password and db_password != DATABASES['default']['PASSWORD']:
        # Если есть пароль от Render, используем его с другими переменными
        DATABASES['default'].update({
            'NAME': os.environ.get('DB_NAME', DATABASES['default']['NAME']),
            'USER': os.environ.get('DB_USER', DATABASES['default']['USER']),
            'PASSWORD': db_password,
            'HOST': db_host or DATABASES['default']['HOST'],
            'PORT': os.environ.get('DB_PORT', DATABASES['default']['PORT']),
        })

# --- ПАРОЛИ ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- ЛОКАЛЬНЫЕ НАСТРОЙКИ ---
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# --- СТАТИКА ---
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# --- МЕДИА ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
