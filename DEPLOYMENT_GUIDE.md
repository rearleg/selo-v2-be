# 🚀 Selo v2 Backend 배포 가이드

## 📋 배포 준비 상태 체크리스트

### ✅ 완료된 배포 준비사항
- [x] 설정 파일 분리 (development/production)
- [x] Docker 및 Docker Compose 설정
- [x] Nginx 리버스 프록시 설정
- [x] 보안 설정 (HTTPS, CSRF, CORS)
- [x] 데이터베이스 마이그레이션 준비
- [x] 정적 파일 처리 설정
- [x] 로깅 및 모니터링 설정
- [x] JWT 기반 인증 시스템
- [x] Rate limiting 설정

### 🔧 추가 확인 필요사항
- [ ] 환경변수 설정 (.env.production)
- [ ] 도메인 및 DNS 설정
- [ ] SSL 인증서 설정
- [ ] 데이터베이스 백업 전략
- [ ] 모니터링 도구 연결 (선택사항)

## 🌐 Cloudflare 도메인 연결 방법

### 1. Cloudflare 설정

#### 1.1 도메인 등록
```bash
# Cloudflare에 도메인 추가
1. Cloudflare 대시보드 로그인
2. "사이트 추가" 클릭
3. 도메인 이름 입력 (예: selo-api.com)
4. 플랜 선택 (Free 플랜도 충분)
```

#### 1.2 DNS 레코드 설정
```
Type: A
Name: @
Content: YOUR_SERVER_IP
TTL: Auto
Proxy: Enabled (오렌지 구름 아이콘)

Type: A  
Name: api
Content: YOUR_SERVER_IP
TTL: Auto
Proxy: Enabled

Type: CNAME
Name: www
Content: selo-api.com
TTL: Auto
Proxy: Enabled
```

#### 1.3 Cloudflare SSL 설정
```
SSL/TLS 탭에서:
- 암호화 모드: "Full (strict)" 선택
- Edge Certificates: "Always Use HTTPS" 활성화
- Minimum TLS Version: 1.2
- Opportunistic Encryption: 활성화
```

### 2. 서버 준비 (Ubuntu 예시)

#### 2.1 기본 도구 설치
```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 재로그인 후 확인
docker --version
docker-compose --version
```

#### 2.2 프로젝트 배포
```bash
# 프로젝트 클론
git clone https://github.com/your-repo/SELO-V2-BE.git
cd SELO-V2-BE

# 환경변수 파일 생성
cp .env.production.example .env.production
nano .env.production  # 실제 값으로 수정

# SSL 디렉토리 생성 (Cloudflare Origin Certificate용)
mkdir -p ssl
```

#### 2.3 Cloudflare Origin Certificate 생성
```bash
# Cloudflare 대시보드 > SSL/TLS > Origin Server
# "Create Certificate" 클릭
# 생성된 인증서와 키를 다운로드

# 서버에 인증서 저장
nano ssl/cloudflare.pem    # 인증서 내용 붙여넣기
nano ssl/cloudflare.key    # 개인키 내용 붙여넣기
chmod 600 ssl/cloudflare.key
```

### 3. 배포 실행

#### 3.1 Docker 컨테이너 시작
```bash
# 백그라운드에서 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f web

# 상태 확인
docker-compose ps
```

#### 3.2 Django 초기 설정
```bash
# 데이터베이스 마이그레이션
docker-compose exec web python manage.py migrate

# 정적 파일 수집
docker-compose exec web python manage.py collectstatic --noinput

# 슈퍼유저 생성
docker-compose exec web python manage.py createsuperuser

# 기존 데이터 통계 업데이트 (필요시)
docker-compose exec web python manage.py update_existing_stats --reset
```

### 4. 도메인 연결 확인

#### 4.1 DNS 전파 확인
```bash
# DNS 레코드 확인
nslookup selo-api.com
dig selo-api.com

# SSL 인증서 확인
curl -I https://selo-api.com/api/v1/
```

#### 4.2 API 엔드포인트 테스트
```bash
# Health check
curl https://selo-api.com/health/

# API 테스트
curl https://selo-api.com/api/v1/signup/

# Admin 페이지 접근
curl https://selo-api.com/admin/
```

## 🔐 환경변수 설정 가이드

### 필수 환경변수
```bash
# .env.production 파일에 다음 값들을 설정하세요:

# Django 기본 설정
SECRET_KEY=생성된_50자_이상의_강력한_키
DOMAIN_NAME=your-domain.com
DEBUG=False

# 데이터베이스
DATABASE_URL=postgres://user:password@db:5432/dbname

# JWT 설정 
APP_JWT_SECRET=32자_이상의_JWT_시크릿_키

# 카카오 OAuth
KAKAO_CLIENT_ID=카카오_앱_키
KAKAO_REDIRECT_URI=https://your-domain.com/auth/kakao/callback
```

### 환경변수 생성 도구
```python
# Django SECRET_KEY 생성
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())

# JWT Secret 생성
import secrets
print(secrets.token_urlsafe(32))
```

## 🛡️ 보안 설정

### Cloudflare 보안 설정
```
1. Security > WAF > Managed Rules 활성화
2. Security > Rate Limiting 설정:
   - API endpoints: 1000 requests/minute
   - Login endpoints: 10 requests/minute
3. Security > Bot Fight Mode 활성화
4. Firewall Rules 추가 (국가별 차단 등)
```

### 서버 보안 설정
```bash
# UFW 방화벽 설정
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# fail2ban 설치 (선택사항)
sudo apt install fail2ban
```

## 📊 모니터링 및 로깅

### 로그 확인
```bash
# Django 애플리케이션 로그
docker-compose logs -f web

# Nginx 로그
docker-compose logs -f nginx

# PostgreSQL 로그
docker-compose logs -f db

# 실시간 로그 모니터링
tail -f logs/django.log
```

### 성능 모니터링
```bash
# 컨테이너 리소스 사용량
docker stats

# 디스크 사용량
df -h

# 메모리 사용량
free -h
```

## 🔄 배포 자동화 (선택사항)

### GitHub Actions 워크플로우
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.0
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd ~/SELO-V2-BE
          git pull origin main
          docker-compose down
          docker-compose up -d --build
          docker-compose exec -T web python manage.py migrate
          docker-compose exec -T web python manage.py collectstatic --noinput
```

## 🚨 트러블슈팅

### 일반적인 문제들

#### SSL 인증서 문제
```bash
# Cloudflare Origin Certificate 재생성
# 인증서 파일 권한 확인
ls -la ssl/
chmod 600 ssl/cloudflare.key
```

#### 데이터베이스 연결 문제
```bash
# PostgreSQL 상태 확인
docker-compose exec db pg_isready

# 연결 테스트
docker-compose exec web python manage.py dbshell
```

#### 정적 파일 404 오류
```bash
# 정적 파일 재수집
docker-compose exec web python manage.py collectstatic --clear --noinput

# Nginx 설정 확인
docker-compose exec nginx nginx -t
```

#### CORS 오류
```bash
# settings/production.py의 CORS 설정 확인
# 프론트엔드 도메인이 CORS_ALLOWED_ORIGINS에 포함되었는지 확인
```

## ✅ 배포 완료 체크리스트

- [ ] 도메인이 정상적으로 연결됨
- [ ] HTTPS 인증서가 유효함
- [ ] API 엔드포인트가 모두 작동함
- [ ] 관리자 페이지 접근 가능
- [ ] 데이터베이스 마이그레이션 완료
- [ ] 정적 파일 서빙 정상
- [ ] 카카오 로그인 테스트 완료
- [ ] JWT 토큰 발급/검증 정상
- [ ] 로그 수집 정상 작동
- [ ] 백업 시스템 구축 (권장)

## 📞 배포 후 지원

배포 완료 후 다음 사항들을 확인하고 관리하세요:

1. **모니터링**: 정기적인 서버 상태 확인
2. **백업**: 데이터베이스 정기 백업 스케줄링
3. **업데이트**: 보안 업데이트 적용
4. **로그 분석**: 오류 로그 정기 검토
5. **성능 최적화**: 필요시 서버 리소스 확장

---

## 🎯 성공적인 배포!

이 가이드를 따라하면 Selo v2 Backend API가 Cloudflare와 연결된 도메인으로 안전하게 배포됩니다. 

**배포된 API 주소**: `https://your-domain.com/api/v1/`  
**관리자 페이지**: `https://your-domain.com/admin/`

문제가 발생하면 로그를 확인하고 이 가이드의 트러블슈팅 섹션을 참조하세요! 🚀