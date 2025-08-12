"""
Production settings for Selo v2 project.
"""

from .base import *
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# 운영 환경에서는 특정 호스트만 허용
ALLOWED_HOSTS = [
    os.getenv('DOMAIN_NAME', 'selo.example.com'),  # 실제 도메인으로 변경
    'localhost',
    '127.0.0.1',
]

# 보안 설정
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS 설정 (Cloudflare 사용 시)
USE_TLS = os.getenv('USE_TLS', 'True').lower() == 'true'
if USE_TLS:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Database - PostgreSQL 또는 환경변수 기반
DATABASES = {
    'default': dj_database_url.parse(
        os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/db.sqlite3')
    )
}

# Static files 설정
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files 설정  
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'

# CORS 설정 (운영용)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    os.getenv('FRONTEND_URL', 'https://selo.example.com'),
    # React Native 앱의 경우 필요시 추가
]

# 신뢰할 수 있는 origins (CSRF)
CSRF_TRUSTED_ORIGINS = [
    f"https://{os.getenv('DOMAIN_NAME', 'selo.example.com')}",
]

# 로깅 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'users': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'seloing': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# 이메일 설정 (선택사항)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@selo.example.com')

# 캐시 설정 (Redis 사용 시)
if os.getenv('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.getenv('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }

# 세션 설정
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7일
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_NAME = 'selo_sessionid'

# JWT 토큰 설정 검증
if not APP_JWT_SECRET or APP_JWT_SECRET == "CHANGE-ME":
    raise ValueError("APP_JWT_SECRET must be set in production environment")