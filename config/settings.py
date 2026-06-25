"""
Django settings for Nexus project.

Sensitive values are loaded from .env (see .env.example for template).
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv(BASE_DIR / '.env')

# SECURITY — all from .env
SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
DEBUG = os.environ.get('DJANGO_DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_htmx',
    'nexus_core',
    'blog',
    'links',
    'research',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
                'nexus_core.context_processors.pin_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
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
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
WHITENOISE_USE_FINDERS = True

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Nexus PIN (6位数字)
NEXUS_PIN = os.environ.get('NEXUS_PIN', '123456')

# Nexus API Key (用于程序化管理内容)
NEXUS_API_KEY = os.environ.get('NEXUS_API_KEY', '')

# 监控 Agent 配置
MONITOR_SERVERS = [
    {"name": "solar", "url": "http://localhost:9100/metrics", "role": "远程开发服务器"},
    {"name": "ivory", "url": "http://100.67.174.27:9100/metrics", "role": "Docker 容器服务器"},
]

# RSS 订阅源
RSS_FEEDS = [
    {"name": "爱范儿", "url": "https://www.ifanr.com/feed", "icon": "📱", "color": "#f97316"},
    {"name": "GitHub Blog", "url": "https://github.blog/feed/", "icon": "🐙", "color": "#8b5cf6"},
    {"name": "少数派", "url": "https://sspai.com/feed", "icon": "🎯", "color": "#ef4444"},
    {"name": "36氪", "url": "https://36kr.com/feed", "icon": "📰", "color": "#06b6d4"},
    {"name": "InfoQ", "url": "https://www.infoq.cn/feed", "icon": "💡", "color": "#10b981"},
]

# RSS 代理服务器（海外，解决国内抓取超时问题）
RSS_PROXY_URL = os.getenv("RSS_PROXY_URL", "")
