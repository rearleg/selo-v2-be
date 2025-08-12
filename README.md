# 🎙️ Selo v2 - Backend API

**Selo v2**는 AI 기반 음성 분석을 통한 스피치 학습 플랫폼의 백엔드 API 서버입니다.  
사용자의 음성을 분석하여 발화 품질을 평가하고, 개선 피드백을 제공하는 "셀로잉(Seloing)" 서비스를 제공합니다.

## 🚀 주요 기능

### 👤 사용자 관리 (Users)
- **회원가입/로그인/로그아웃**: Token 기반 인증
- **프로필 관리**: 사용자 정보 조회/수정/탈퇴
- **온보딩 지원**: 사용자 유형별 맞춤 설정
- **셀로잉 이력**: 완료된 학습 세션 기록 관리

### 🎯 셀로잉 학습 (Seloing)
- **주제 생성**: AI 기반 맞춤형 주제 생성
- **학습 세션**: 음성 녹음 및 AI 분석 요청
- **실시간 진행상황**: 분석 상태 추적
- **결과 분석**: 종합적인 발화 품질 평가
  - 반복 표현 분석
  - 주제 연관성 평가  
  - 발화 안정성 측정
  - 불필요한 추임새 검출

### 📊 통계 및 랭킹 (Stats)
- **개인 통계**: 학습 진도, 점수 추이, 성과 분석
- **글로벌 랭킹**: 전체 사용자 대비 순위 (3회 이상 학습자만)
- **자동 업데이트**: 학습 완료 시 실시간 통계 반영
- **조건부 집계**: 초보자 점수는 전체 평균에서 제외

### 💡 지식 및 팁 (Tips)
- **학습 가이드**: 효과적인 스피치 학습 방법
- **실용 팁**: 상황별 커뮤니케이션 노하우

### 📱 미디어 관리 (Medias)
- **프로필 이미지**: 사용자 프로필 사진 관리

## 🏗️ 기술 스택

### Backend Framework
- **Django 5.2+**: 웹 프레임워크
- **Django REST Framework 3.16+**: API 개발
- **SQLite**: 개발용 데이터베이스

### 주요 라이브러리
- **django-cors-headers**: CORS 처리
- **requests**: 외부 API 통신 (AI 서버)
- **python-dotenv**: 환경변수 관리

### 인증 및 권한
- **Token Authentication**: DRF 기본 토큰 인증
- **Permission Classes**: 세밀한 권한 제어

## 📁 프로젝트 구조

```
SELO-V2-BE/
├── config/                 # 프로젝트 설정
│   ├── settings.py         # Django 설정
│   ├── urls.py            # 메인 URL 라우팅
│   └── wsgi.py            # WSGI 설정
├── users/                  # 사용자 관리
│   ├── models.py          # User, UserType, UserSelloingInfo
│   ├── views.py           # 인증, 프로필 관리 API
│   ├── serializers.py     # 사용자 데이터 직렬화
│   └── admin.py           # 관리자 페이지 설정
├── seloing/               # 셀로잉 학습 시스템
│   ├── models.py          # Seloing, SeloingResult, SeloingAnalysis
│   ├── views.py           # 학습 세션, AI 콜백 API
│   ├── utils.py           # 통계 업데이트 유틸리티
│   └── management/        # 관리 명령어
│       └── commands/
│           └── update_existing_stats.py
├── stats/                 # 통계 및 랭킹
│   ├── models.py          # UserStats, GlobalStats
│   ├── views.py           # 랭킹 조회 API
│   └── serializers.py     # 통계 데이터 직렬화
├── tips/                  # 학습 팁
├── medias/               # 미디어 파일 관리
├── common/               # 공통 모델 및 유틸리티
└── manage.py            # Django 관리 스크립트
```

## 🔧 설치 및 실행

### 1. 개발 환경 설정

```bash
# 저장소 클론
git clone <repository-url>
cd SELO-V2-BE

# Poetry를 사용한 의존성 설치
poetry install
poetry shell

# 또는 pip 사용
pip install -r requirements.txt
```

### 2. 환경변수 설정

```bash
# .env 파일 생성
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 3. 데이터베이스 설정

```bash
# 마이그레이션 생성 및 적용
python manage.py makemigrations
python manage.py migrate

# 관리자 계정 생성
python manage.py createsuperuser

# 기존 데이터 통계 업데이트 (선택사항)
python manage.py update_existing_stats --reset
```

### 4. 서버 실행

```bash
# 개발 서버 시작
python manage.py runserver

# 서버 확인
curl http://localhost:8000/admin/
```

## 🌐 API 엔드포인트

### 인증 (Authentication)
```
POST /api/v1/signup/        # 회원가입
POST /api/v1/login/         # 로그인  
POST /api/v1/logout/        # 로그아웃
```

### 사용자 관리 (Users)
```
GET    /api/v1/users/                           # 사용자 목록 (관리자)
GET    /api/v1/users/{user_id}/                # 사용자 정보 조회
PATCH  /api/v1/users/{user_id}/                # 사용자 정보 수정
DELETE /api/v1/users/{user_id}/                # 회원 탈퇴
GET    /api/v1/users/{user_id}/seloing/        # 셀로잉 이력
GET    /api/v1/users/{user_id}/seloing/{seloing_id}/ # 셀로잉 상세
```

### 셀로잉 학습 (Seloing)  
```
POST /api/v1/seloing/topics/                   # 주제 생성
POST /api/v1/seloing/                         # 셀로잉 시작
POST /api/v1/seloing/{seloing_id}/recording/  # 녹음 업로드
GET  /api/v1/seloing/{seloing_id}/progress/   # 분석 진행상황
GET  /api/v1/seloing/{seloing_id}/           # 분석 결과 조회
POST /api/v1/seloing/{seloing_id}/stat/      # 보상 지급
POST /api/v1/seloing/{seloing_id}/callback/  # AI 콜백 (내부)
```

### 랭킹 및 통계 (Ranking)
```
GET /api/v1/ranking/                          # 전체 랭킹 조회
GET /api/v1/ranking/{user_id}/               # 개별 사용자 랭킹
```

### 학습 자료 (Content)
```
GET /api/v1/knowledge/                        # 지식 조회
GET /api/v1/tips/                            # 팁 조회
```

## 🤖 AI 서버 연동

Selo 백엔드는 외부 AI 서버와 연동하여 음성 분석을 수행합니다:

### AI 분석 플로우
1. **녹음 업로드**: 클라이언트 → BE 서버
2. **AI 요청**: BE 서버 → AI 서버 (`/ai/v1/selowhisper`)  
3. **비동기 분석**: AI 서버에서 음성 처리
4. **결과 콜백**: AI 서버 → BE 서버 (`/api/v1/seloing/{id}/callback/`)
5. **자동 통계 업데이트**: 완료 시 사용자/글로벌 통계 반영

### 분석 결과 데이터
- **음성 전사**: 원본 및 분석된 텍스트
- **점수 평가**: 반복/주제/추임새/안정성 점수  
- **개선 피드백**: 각 영역별 상세 분석
- **통계 반영**: 3회 이상 학습자만 글로벌 랭킹 포함

## 🔐 권한 관리

### 권한 레벨
- **AllowAny**: 회원가입, 지식/팁 조회
- **IsAuthenticated**: 대부분의 학습 기능
- **IsAdminUser**: 전체 사용자 관리
- **본인만**: 개인정보, 학습기록 접근

### 데이터 보안
- **개인정보 보호**: 본인 외 접근 차단
- **토큰 기반 인증**: 안전한 세션 관리
- **관리자 전용**: 민감한 통계 데이터

## 📈 통계 시스템

### 자동 업데이트
- **사용자 생성**: UserStats, UserSelloingInfo 자동 생성
- **학습 완료**: Django Signal로 통계 즉시 반영
- **조건부 집계**: 3회 미만 학습자는 글로벌 평균에서 제외

### 관리 명령어
```bash
# 기존 데이터 통계 일괄 업데이트
python manage.py update_existing_stats

# 전체 통계 초기화 후 재계산
python manage.py update_existing_stats --reset
```

## 🧪 테스트

### 개발 테스트
```bash
# Django 테스트 실행
python manage.py test

# 특정 앱 테스트
python manage.py test users
python manage.py test seloing
```

### API 테스트
```bash
# URL 연결 테스트
python manage.py shell -c "from django.urls import reverse; print('✓ URLs configured')"

# 관리자 페이지 접근
http://localhost:8000/admin/
```

## 🚀 배포

### 운영 환경 설정
1. **환경변수**: `DEBUG=False`, 운영 DB 설정
2. **정적파일**: `python manage.py collectstatic`  
3. **보안설정**: `ALLOWED_HOSTS`, CORS 설정
4. **데이터베이스**: PostgreSQL 등 운영 DB 마이그레이션

### 도커 배포 (예정)
```dockerfile
# Dockerfile
FROM python:3.13-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["gunicorn", "config.wsgi:application"]
```

## 🤝 개발 가이드

### 코드 컨벤션
- **PEP 8**: 파이썬 코딩 스타일 준수
- **API 설계**: RESTful 원칙 따르기
- **에러 처리**: 일관된 응답 형식
- **문서화**: 코드 주석 및 API 문서

### 기여 방법
1. 이슈 등록 또는 기능 제안
2. 브랜치 생성 (`feature/new-feature`)
3. 코드 작성 및 테스트  
4. Pull Request 제출

## 🔧 최신 업데이트

### v0.1.0 (2024)
- ✅ Django 5.2 + DRF 3.16 기반 구축
- ✅ Token 인증 시스템 구현  
- ✅ 셀로잉 학습 플로우 완성
- ✅ AI 서버 연동 및 콜백 처리
- ✅ 실시간 통계 업데이트 시스템
- ✅ 조건부 글로벌 랭킹 (3회 이상)
- ✅ 관리자 패널 통합
- ✅ 기존 데이터 마이그레이션 도구

**Ready for Production** 🚀