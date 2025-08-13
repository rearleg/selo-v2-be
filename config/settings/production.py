from .base import *
import os
from pathlib import Path

DEBUG = False

# --- ALLOWED_HOSTS ---
_raw_hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "")
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(",") if h.strip()]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["api.selo-ai.my", ".selo-ai.my", "localhost", "127.0.0.1"]

# --- CSRF_TRUSTED_ORIGINS ---
_raw_csrf = os.getenv("CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = [u.strip() for u in _raw_csrf.split(",") if u.strip()]
if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = ["https://api.selo-ai.my"]

# --- 보안 ---
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True  # Django5에선 기본적으로 헤더 설정됨
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))  # 1년
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# --- DB: 기본 SQLite, ENV가 주어지면 Postgres/DATABASE_URL 사용 ---
SQLITE_PATH = os.getenv("SQLITE_PATH", str(BASE_DIR / "db.sqlite3"))
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "").strip()

if DATABASE_URL:
    import dj_database_url

    DATABASES = {"default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
elif POSTGRES_HOST:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "postgres"),
            "USER": os.getenv("POSTGRES_USER", "postgres"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", ""),
            "HOST": POSTGRES_HOST,
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": 600,
        }
    }
else:
    # ← 현재 상태: SQLite 사용
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": SQLITE_PATH,
        }
    }

# --- STATIC / MEDIA ---
STATIC_URL = "/static/"
STATIC_ROOT = os.getenv("STATIC_ROOT", str(BASE_DIR / "staticfiles"))

MEDIA_URL = "/media/"
MEDIA_ROOT = os.getenv("MEDIA_ROOT", str(BASE_DIR / "media"))

# --- 로깅: 콘솔 기본 ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
