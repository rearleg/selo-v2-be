# ========= builder =========
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 빌드에 필요한 기본 패키지
# cryptography/psycopg2 등 대비해서 헤더/라이브러리 추가
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc python3-dev libffi-dev libssl-dev cargo curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 로그 디렉터리 생성 (권한은 일단 root로 둬도 됨)
RUN mkdir -p /app/logs

# wheel 출력 디렉터리 생성
RUN mkdir -p /wheels

# 의존성 먼저 복사 (캐시 최적화)
COPY requirements.txt /app/requirements.txt

# 휠 미리 빌드
# ← 역슬래시 뒤 공백 제거!
RUN pip install --upgrade pip wheel \
 && pip wheel --no-cache-dir -r /app/requirements.txt -w /wheels


# ========= runtime =========
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 비루트 유저
RUN useradd -m appuser

WORKDIR /app

# 미리 빌드한 휠로 설치 (root에서 설치 후 권한 낮춤)
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

# 앱 코드 복사
COPY . /app

# 엔트리포인트 스크립트
COPY entrypoint.sh /entrypoint.sh


RUN chmod +x /entrypoint.sh \
 && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]