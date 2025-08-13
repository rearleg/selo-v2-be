#!/bin/sh
set -eu
umask 002

echo "[entrypoint] starting container..."

if [ -z "${DJANGO_PROJECT:-}" ]; then
  echo "DJANGO_PROJECT is required" >&2
  exit 1
fi

SQLITE_PATH="${SQLITE_PATH:-/data/db/db.sqlite3}"
DB_DIR="$(dirname "$SQLITE_PATH")"
mkdir -p "$DB_DIR"
chown -R "$(id -u)":"$(id -g)" "$DB_DIR" || true
chmod 775 "$DB_DIR" || true
# 선택: 최초 DB 파일 생성
[ -f "$SQLITE_PATH" ] || : > "$SQLITE_PATH" || true
chmod 664 "$SQLITE_PATH" || true

echo "[entrypoint] creating log directory..."
mkdir -p /app/logs
touch /app/logs/django.log
chmod 666 /app/logs/django.log

# static/media도 미리 준비
mkdir -p "${STATIC_ROOT:-/app/staticfiles}" "${MEDIA_ROOT:-/app/media}"
chown -R "$(id -u)":"$(id -g)" "${STATIC_ROOT:-/app/staticfiles}" "${MEDIA_ROOT:-/app/media}" /app/logs "$DB_DIR" || true
chmod 775 "${STATIC_ROOT:-/app/staticfiles}" "${MEDIA_ROOT:-/app/media}" || true

python -VV || true
python manage.py check --deploy || true

echo "[entrypoint] migrate..."
python manage.py migrate --noinput

echo "[entrypoint] collectstatic..."
python manage.py collectstatic --noinput

echo "[entrypoint] launching gunicorn..."
exec gunicorn "${DJANGO_PROJECT}.wsgi:application" \
  --bind 0.0.0.0:8000 \
  --workers "${GUNICORN_WORKERS:-3}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-60}"