import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

# Попытка загрузить .env файл (если есть)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv не установлен, продолжаем без него

# --- ПУТИ ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- БЕЗОПАСНОСТЬ ---
SECRET_KEY = os.environ.get('SECRET_KEY', get_random_secret_key())
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Разрешенные хосты для публичного доступа
# Автоматическое определение хостов для облачных платформ
ALLOWED_HOSTS_ENV = os.environ.get('ALLOWED_HOSTS', '')
if ALLOWED_HOSTS_ENV:
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(',')]
else:
    ALLOWED_HOSTS = ['*']  # Для публичного доступа разрешаем все хосты

# Автоматическое добавление хостов облачных платформ
if 'RAILWAY_STATIC_URL' in os.environ:
    ALLOWED_HOSTS.append(os.environ.get('RAILWAY_PUBLIC_DOMAIN', ''))
if 'RENDER' in os.environ or 'RENDER_EXTERNAL_HOSTNAME' in os.environ:
    render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
    if render_host:
        ALLOWED_HOSTS.append(render_host)
    ALLOWED_HOSTS.append('*.onrender.com')  # Все Render поддомены
if 'FLY_APP_NAME' in os.environ:
    ALLOWED_HOSTS.append(f"{os.environ.get('FLY_APP_NAME')}.fly.dev")

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
    # сюда добавляем наше приложение
    'main',  # если ты назвала приложение main
]


# --- МИДЛВАР ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Для статики в production
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

# --- БАЗА ДАННЫХ (PostgreSQL) ---
# Поддержка Render и других облачных платформ
try:
    import dj_database_url
    DATABASE_URL_AVAILABLE = True
except ImportError:
    DATABASE_URL_AVAILABLE = False

# Базовая конфигурация базы данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'uniquestus'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'Ssssuro4ka.'),
        'HOST': os.environ.get('DB_HOST', os.environ.get('PGHOST', 'localhost')),
        'PORT': os.environ.get('DB_PORT', os.environ.get('PGPORT', '5432')),
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c timezone=Asia/Almaty'
        },
        'CONN_MAX_AGE': 600,  # Поддержание соединения
    }
}

# Автоматическое использование DATABASE_URL (Render, Heroku и др.)
if DATABASE_URL_AVAILABLE and 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
        default=os.environ.get('DATABASE_URL')
    )

# Резервная SQLite база (если PostgreSQL недоступна)
# Раскомментируйте, если нужна резервная база
# DATABASES['default'] = {
#     'ENGINE': 'django.db.backends.sqlite3',
#     'NAME': BASE_DIR / 'db.sqlite3',
# }




# --- ПАРОЛИ ---
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

# --- ЛОКАЛЬНЫЕ НАСТРОЙКИ ---
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# --- СТАТИКА ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Для production

# WhiteNoise для статики
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Медиа файлы (загрузки пользователей)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
