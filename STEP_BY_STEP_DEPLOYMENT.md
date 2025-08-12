# 🚀 Selo v2 Backend 초보자용 배포 가이드

> 🎯 **이 가이드의 목표**: 프로그래밍 초보자도 따라할 수 있도록 Selo v2 Backend를 실제 서버에 배포하고 도메인과 연결하기

## 📋 준비물 체크리스트

배포를 시작하기 전에 다음 항목들을 준비해주세요:

- [ ] **서버** (AWS EC2, Vultr, DigitalOcean 등)
- [ ] **도메인** (예: selo-api.com)
- [ ] **Cloudflare 계정** (무료)
- [ ] **카카오 개발자 계정** 
- [ ] **컴퓨터에 Git 설치**
- [ ] **약간의 인내심** ☕

---

# 🌟 PART 1: 도메인 및 Cloudflare 설정

## Step 1: 도메인 구입하기 (10분)

### 1.1 도메인 구입처 추천
- **가비아** (한국): https://domain.gabia.com
- **Namecheap** (해외): https://namecheap.com
- **Google Domains**: https://domains.google

### 1.2 도메인 선택 팁
```
좋은 예시:
- selo-api.com
- myapp-backend.net  
- api.myservice.co.kr

피해야 할 예시:
- 너무 긴 도메인
- 특수문자가 들어간 도메인
- 기존 유명 서비스와 비슷한 이름
```

### 1.3 도메인 구입 과정
1. 원하는 도메인 검색
2. 장바구니에 추가 (1년 구입 권장)
3. 결제 완료
4. 구입 완료 이메일 확인

---

## Step 2: Cloudflare 설정하기 (15분)

### 2.1 Cloudflare 계정 생성
1. https://cloudflare.com 접속
2. "Sign Up" 클릭
3. 이메일, 비밀번호 입력
4. 이메일 인증 완료

### 2.2 사이트 추가하기
1. Cloudflare 대시보드에서 **"사이트 추가"** 클릭
2. 구입한 도메인 입력 (예: `selo-api.com`)
3. **"Free"** 플랜 선택
4. **"계속"** 클릭

### 2.3 DNS 레코드 설정
**중요**: 아직 서버 IP가 없으므로 임시로 `1.1.1.1`을 사용합니다.

DNS 관리 화면에서 다음과 같이 설정:

```
타입: A
이름: @  
내용: 1.1.1.1
TTL: 자동
프록시 상태: 🟠 (프록시됨)

타입: A
이름: api
내용: 1.1.1.1  
TTL: 자동
프록시 상태: 🟠 (프록시됨)

타입: CNAME
이름: www
내용: selo-api.com
TTL: 자동
프록시 상태: 🟠 (프록시됨)
```

### 2.4 네임서버 변경
1. Cloudflare에서 제공하는 네임서버 2개를 복사
   ```
   예시:
   ava.ns.cloudflare.com
   king.ns.cloudflare.com
   ```
2. 도메인 구입처(가비아 등) 관리 페이지로 이동
3. **"네임서버 변경"** 또는 **"DNS 설정"** 메뉴 찾기
4. Cloudflare 네임서버로 변경
5. **저장** 클릭

**⏰ 대기 시간**: 네임서버 변경은 최대 24시간이 걸릴 수 있습니다.

### 2.5 SSL 설정
1. Cloudflare 대시보드 > **SSL/TLS** 탭
2. **암호화 모드**: "전체(엄격)" 선택
3. **Edge Certificates** 하위 메뉴:
   - **"항상 HTTPS 사용"** 활성화
   - **"HSTS 활성화"** 체크
   - **"최소 TLS 버전"**: 1.2 선택

---

# 🖥️ PART 2: 서버 설정

## Step 3: 서버 선택 및 구입하기 (10분)

### 3.1 추천 서버 제공업체
| 업체 | 장점 | 최소 사양 | 가격 |
|------|------|-----------|------|
| **AWS EC2** | 안정적, 다양한 기능 | t3.small | $20/월 |
| **Vultr** | 저렴, 단순함 | Regular 1GB | $6/월 |
| **DigitalOcean** | 초보자 친화적 | Basic 1GB | $6/월 |

### 3.2 서버 사양 권장사항
```
최소 사양:
- CPU: 1 core
- RAM: 1GB
- Storage: 25GB SSD
- OS: Ubuntu 22.04 LTS

권장 사양:
- CPU: 2 cores
- RAM: 2GB
- Storage: 50GB SSD
- OS: Ubuntu 22.04 LTS
```

### 3.3 서버 생성 과정 (Vultr 예시)
1. https://vultr.com 회원가입
2. **"Deploy Instance"** 클릭
3. **서버 위치**: Seoul (한국 사용자용)
4. **Server Type**: Regular Cloud Compute
5. **Server Size**: $6/month (1GB RAM)
6. **Operating System**: Ubuntu 22.04 x64
7. **SSH Keys**: 나중에 설정 (패스워드 사용)
8. **Server Label**: `selo-backend-server`
9. **"Deploy Now"** 클릭

### 3.4 서버 정보 확인
서버 생성 완료 후 다음 정보를 메모장에 저장:
```
서버 IP: 123.456.789.012 (예시)
사용자명: root
비밀번호: 생성된 임시 비밀번호
```

---

## Step 4: 서버에 접속하기 (10분)

### 4.1 SSH 클라이언트 준비
**Windows 사용자**:
- **PuTTY** 다운로드: https://putty.org
- 또는 **Windows Terminal** 사용

**Mac 사용자**:
- 터미널 앱 사용 (기본 설치됨)

### 4.2 서버 접속 방법

**Windows (PuTTY) 사용자**:
1. PuTTY 실행
2. **Host Name**: 서버 IP 입력
3. **Port**: 22
4. **Connection type**: SSH
5. **"Open"** 클릭
6. 사용자명 `root` 입력
7. 비밀번호 입력 (화면에 보이지 않음)

**Mac/Linux 사용자**:
```bash
ssh root@123.456.789.012
# 비밀번호 입력
```

### 4.3 첫 접속 시 설정
```bash
# 시스템 업데이트
apt update && apt upgrade -y

# 필수 도구 설치
apt install -y curl wget git nano

# 방화벽 설정
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable

echo "✅ 서버 기본 설정 완료!"
```

---

# 🐳 PART 3: Docker 설치 및 프로젝트 배포

## Step 5: Docker 설치하기 (15분)

### 5.1 Docker 설치 스크립트 실행
```bash
# Docker 설치 스크립트 다운로드 및 실행
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker 서비스 시작
systemctl start docker
systemctl enable docker

# Docker 버전 확인
docker --version
```

### 5.2 Docker Compose 설치
```bash
# Docker Compose 다운로드
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 실행 권한 부여
chmod +x /usr/local/bin/docker-compose

# 버전 확인
docker-compose --version
```

**예상 출력**:
```
Docker version 24.0.x
Docker Compose version v2.21.x
```

---

## Step 6: 프로젝트 코드 다운로드 (10분)

### 6.1 프로젝트 클론
```bash
# 홈 디렉토리로 이동
cd ~

# Git 프로젝트 클론 (실제 저장소 URL로 변경하세요)
git clone https://github.com/your-username/SELO-V2-BE.git

# 프로젝트 디렉토리로 이동
cd SELO-V2-BE

# 파일 확인
ls -la
```

**예상 출력**:
```
Dockerfile
docker-compose.yml
requirements.txt
.env.production.example
manage.py
...
```

### 6.2 프로젝트 구조 확인
```bash
# 중요한 파일들이 있는지 확인
echo "=== 배포 파일 체크 ==="
for file in Dockerfile docker-compose.yml requirements.txt .env.production.example; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file 없음"
    fi
done
```

---

# 🔧 PART 4: 환경 설정

## Step 7: 환경변수 설정하기 (20분)

### 7.1 환경변수 파일 생성
```bash
# 환경변수 예시 파일을 실제 파일로 복사
cp .env.production.example .env.production

# 환경변수 파일 편집
nano .env.production
```

### 7.2 환경변수 값 설정
nano 에디터에서 다음과 같이 수정하세요:

```bash
# Django 기본 설정
SECRET_KEY=여기에_50자_이상의_긴_랜덤_문자열_입력
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
DOMAIN_NAME=your-domain.com  # 실제 도메인으로 변경
USE_TLS=True

# 데이터베이스 (기본값 유지)
DATABASE_URL=postgres://selo_user:selo_strong_password_2024@db:5432/selo_db
DB_NAME=selo_db
DB_USER=selo_user
DB_PASSWORD=selo_strong_password_2024

# JWT 설정
APP_JWT_SECRET=여기에_32자_이상의_JWT_시크릿_키_입력
APP_JWT_ALG=HS256
APP_JWT_EXP_MINUTES=10080

# 카카오 OAuth (나중에 설정)
KAKAO_CLIENT_ID=카카오_앱_키_입력_예정
KAKAO_REDIRECT_URI=https://your-domain.com/auth/kakao/callback

# URL 설정
FRONTEND_URL=https://your-frontend-domain.com
BACKEND_URL=https://your-domain.com

# 캐시
REDIS_URL=redis://redis:6379/0
```

### 7.3 강력한 비밀번호 생성하는 방법

**SECRET_KEY 생성**:
```bash
# 터미널에서 다음 명령어 실행
python3 -c "
import secrets
import string
chars = string.ascii_letters + string.digits + '!@#$%^&*'
print(''.join(secrets.choice(chars) for _ in range(50)))
"
```

**JWT 시크릿 생성**:
```bash
python3 -c "
import secrets
print(secrets.token_urlsafe(32))
"
```

### 7.4 nano 에디터 사용법
- **저장**: `Ctrl + O` 누른 후 `Enter`
- **종료**: `Ctrl + X`
- **이동**: 화살표 키 사용

---

## Step 8: 카카오 개발자 설정 (15분)

### 8.1 카카오 개발자 계정 생성
1. https://developers.kakao.com 접속
2. 카카오 계정으로 로그인
3. **"개발자 등록"** 클릭
4. 약관 동의 및 개발자 정보 입력

### 8.2 카카오 앱 생성
1. **"내 애플리케이션"** 클릭
2. **"애플리케이션 추가하기"** 클릭
3. 앱 정보 입력:
   ```
   앱 이름: Selo Backend
   사업자명: (본인 이름)
   카테고리: 기타
   ```
4. **"저장"** 클릭

### 8.3 카카오 앱 설정
1. 생성된 앱 클릭
2. **"앱 키"** 탭에서 **"REST API 키"** 복사
3. **"플랫폼"** 탭 > **"Web 플랫폼 등록"**
   ```
   사이트 도메인: https://your-domain.com
   ```
4. **"카카오 로그인"** 탭:
   - 카카오 로그인 활성화
   - Redirect URI 등록: `https://your-domain.com/auth/kakao/callback`

### 8.4 환경변수에 카카오 키 추가
```bash
# .env.production 파일 다시 편집
nano .env.production

# KAKAO_CLIENT_ID 부분을 실제 키로 변경
KAKAO_CLIENT_ID=복사한_REST_API_키_붙여넣기
```

---

# 🚀 PART 5: 배포 실행

## Step 9: Cloudflare DNS 업데이트 (5분)

### 9.1 서버 IP를 Cloudflare에 등록
1. Cloudflare 대시보드 접속
2. **DNS** 탭 클릭
3. 기존 A 레코드들의 IP를 실제 서버 IP로 변경:
   ```
   @ → 실제_서버_IP (예: 123.456.789.012)
   api → 실제_서버_IP
   ```
4. **"저장"** 클릭

### 9.2 DNS 전파 확인
```bash
# 서버에서 DNS 확인
nslookup your-domain.com
```

---

## Step 10: SSL 인증서 설정 (10분)

### 10.1 Cloudflare Origin Certificate 생성
1. Cloudflare > **SSL/TLS** > **Origin Server**
2. **"Create Certificate"** 클릭
3. **호스트명**: `*.your-domain.com, your-domain.com`
4. **Key type**: RSA(2048)
5. **"Create"** 클릭

### 10.2 인증서 파일 저장
```bash
# SSL 디렉토리 생성
mkdir -p ssl

# 인증서 파일 생성 (Cloudflare에서 복사한 내용 붙여넣기)
nano ssl/cloudflare.pem
# Origin Certificate 내용 붙여넣기

# 개인키 파일 생성
nano ssl/cloudflare.key  
# Private Key 내용 붙여넣기

# 파일 권한 설정
chmod 600 ssl/cloudflare.key
```

---

## Step 11: Docker 컨테이너 실행 (15분)

### 11.1 nginx 설정 파일 수정
```bash
# nginx 설정에서 도메인 변경
nano nginx/nginx.conf

# 다음 부분들을 실제 도메인으로 변경:
# your-domain.com → 실제_도메인
# your-frontend-domain.com → 실제_프론트엔드_도메인
```

### 11.2 Docker 컨테이너 빌드 및 실행
```bash
# 컨테이너 빌드 및 백그라운드 실행
docker-compose up -d --build

# 실행 상태 확인
docker-compose ps
```

**예상 출력**:
```
Name                 Command               State           Ports
----------------------------------------------------------------
be_web_1            gunicorn config.wsgi:app...   Up      0.0.0.0:8000->8000/tcp
be_db_1             docker-entrypoint.sh ...      Up      0.0.0.0:5432->5432/tcp
be_redis_1          redis-server --append...      Up      0.0.0.0:6379->6379/tcp
be_nginx_1          nginx -g daemon off;          Up      0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

### 11.3 로그 확인
```bash
# 전체 로그 확인
docker-compose logs

# 특정 서비스 로그 확인
docker-compose logs web
docker-compose logs nginx
```

---

## Step 12: Django 초기 설정 (10분)

### 12.1 데이터베이스 마이그레이션
```bash
# 데이터베이스 테이블 생성
docker-compose exec web python manage.py migrate

# 정적 파일 수집
docker-compose exec web python manage.py collectstatic --noinput
```

### 12.2 관리자 계정 생성
```bash
# 슈퍼유저 생성
docker-compose exec web python manage.py createsuperuser

# 입력 예시:
# Username: admin
# Email: admin@yourdomain.com  
# Password: (강력한 비밀번호 입력)
```

### 12.3 기존 데이터 통계 업데이트 (선택사항)
```bash
# 기존 셀로잉 데이터가 있다면 통계 업데이트
docker-compose exec web python manage.py update_existing_stats --reset
```

---

# 🎯 PART 6: 테스트 및 검증

## Step 13: 배포 완료 테스트 (15분)

### 13.1 웹사이트 접속 테스트
브라우저에서 다음 URL들을 차례로 테스트:

```
1. http://your-domain.com
   → https로 자동 리다이렉트 확인

2. https://your-domain.com/admin/
   → Django 관리자 페이지 로딩 확인

3. https://your-domain.com/api/v1/
   → API 엔드포인트 응답 확인
```

### 13.2 API 엔드포인트 테스트
서버에서 직접 테스트:
```bash
# API 엔드포인트 테스트
curl -X POST https://your-domain.com/api/v1/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123","nickname":"테스트"}' \
  | python3 -m json.tool

# 카카오 로그인 엔드포인트 테스트
curl -X POST https://your-domain.com/api/v1/auth/kakao/ \
  -H "Content-Type: application/json" \
  -d '{"code":"test_code"}' \
  | python3 -m json.tool
```

### 13.3 로그 모니터링
```bash
# 실시간 로그 확인
docker-compose logs -f web

# 오류가 있는지 확인
docker-compose logs web | grep ERROR
```

---

## Step 14: 성능 및 보안 확인 (10분)

### 14.1 SSL 인증서 확인
온라인 도구로 SSL 상태 확인:
- https://www.ssllabs.com/ssltest/
- 도메인 입력 후 **"Submit"** 클릭
- **A+ 등급**이 나오면 완벽!

### 14.2 사이트 속도 테스트
- https://pagespeed.web.dev/
- 도메인 입력 후 분석 실행

### 14.3 서버 리소스 확인
```bash
# CPU, 메모리 사용량 확인
docker stats

# 디스크 사용량 확인
df -h

# 실행 중인 컨테이너 확인
docker ps
```

---

# 🎉 배포 완료!

## ✅ 최종 체크리스트

배포가 완료되었다면 다음 항목들을 확인하세요:

- [ ] **도메인 접속**: https://your-domain.com 접속 가능
- [ ] **HTTPS 리다이렉트**: HTTP가 HTTPS로 자동 이동
- [ ] **관리자 페이지**: `/admin/` 접속 및 로그인 가능
- [ ] **API 응답**: `/api/v1/` 엔드포인트 정상 응답
- [ ] **SSL 등급**: A+ 등급 획득
- [ ] **카카오 로그인**: 설정 완료
- [ ] **Docker 상태**: 모든 컨테이너 정상 실행
- [ ] **로그 확인**: 오류 메시지 없음

## 🚀 성공적인 배포!

축하합니다! Selo v2 Backend가 성공적으로 배포되었습니다.

**배포된 서비스 정보**:
- 🌐 **API 주소**: https://your-domain.com/api/v1/
- 🔧 **관리자 페이지**: https://your-domain.com/admin/
- 📱 **카카오 로그인**: https://your-domain.com/api/v1/auth/kakao/
- 📊 **헬스체크**: https://your-domain.com/health/ (선택)

---

# 🔧 유지보수 가이드

## 일상적인 관리 작업

### 로그 확인
```bash
# 최근 로그 확인
docker-compose logs --tail=100 web

# 에러 로그만 확인  
docker-compose logs web | grep -i error
```

### 서비스 재시작
```bash
# 특정 서비스 재시작
docker-compose restart web

# 전체 서비스 재시작
docker-compose restart
```

### 데이터베이스 백업
```bash
# PostgreSQL 데이터베이스 백업
docker-compose exec db pg_dump -U selo_user selo_db > backup_$(date +%Y%m%d).sql
```

### 코드 업데이트
```bash
# 최신 코드 받기
git pull origin main

# 컨테이너 재빌드
docker-compose up -d --build

# 데이터베이스 마이그레이션
docker-compose exec web python manage.py migrate
```

## 문제 해결

### 자주 발생하는 문제들

1. **503 Service Unavailable**
   ```bash
   # Django 컨테이너 상태 확인
   docker-compose logs web
   
   # 컨테이너 재시작
   docker-compose restart web
   ```

2. **SSL 인증서 오류**
   ```bash
   # 인증서 파일 권한 확인
   ls -la ssl/
   chmod 600 ssl/cloudflare.key
   ```

3. **데이터베이스 연결 오류**
   ```bash
   # PostgreSQL 상태 확인
   docker-compose logs db
   
   # 데이터베이스 재시작
   docker-compose restart db
   ```

4. **카카오 로그인 오류**
   - Redirect URI가 정확한지 확인
   - 카카오 앱 키가 올바른지 확인
   - 도메인 설정이 맞는지 확인

---

# 📞 도움이 필요하다면

이 가이드를 따라했는데 문제가 발생한다면:

1. **로그 확인**: `docker-compose logs` 명령어로 오류 메시지 확인
2. **구글 검색**: 오류 메시지를 구글에 검색
3. **GitHub Issues**: 프로젝트 저장소에 이슈 등록
4. **커뮤니티**: 개발 커뮤니티에 질문

**중요한 팁**: 오류 메시지를 정확히 복사해서 질문하면 더 빠른 도움을 받을 수 있습니다!

---

**🎊 배포를 완료하신 것을 축하드립니다! 이제 여러분의 Selo v2 Backend가 전 세계에서 접속 가능합니다!**