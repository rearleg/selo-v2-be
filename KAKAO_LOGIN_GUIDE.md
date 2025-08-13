# 🔐 Selo v2 카카오 로그인 연동 가이드

이 문서는 Selo v2 백엔드 서버에서 카카오 소셜 로그인을 구현하고 연동하는 방법을 설명합니다.

## 📋 목차
- [시스템 개요](#시스템-개요)
- [카카오 앱 설정](#카카오-앱-설정)
- [백엔드 설정](#백엔드-설정)
- [클라이언트 연동](#클라이언트-연동)
- [API 사용법](#api-사용법)
- [문제 해결](#문제-해결)

---

## 🏗️ 시스템 개요

### 카카오 로그인 흐름
```
1. 클라이언트 앱 → 카카오 OAuth 서버: 인가 코드 요청
2. 카카오 OAuth 서버 → 클라이언트 앱: 인가 코드 반환
3. 클라이언트 앱 → Selo 백엔드 서버: 인가 코드 전송
4. Selo 백엔드 서버 → 카카오 API: 액세스 토큰 요청
5. 카카오 API → Selo 백엔드 서버: 액세스 토큰 반환
6. Selo 백엔드 서버 → 카카오 API: 사용자 정보 요청
7. 카카오 API → Selo 백엔드 서버: 사용자 정보 반환
8. Selo 백엔드 서버 → 클라이언트 앱: JWT 토큰 및 사용자 정보 반환
```

### 지원 기능
- ✅ 카카오 계정으로 회원가입/로그인
- ✅ 신규 사용자 자동 계정 생성
- ✅ JWT 토큰 기반 인증
- ✅ 사용자 프로필 이미지 자동 설정
- ✅ 기존 계정과의 연동

---

## 📱 카카오 앱 설정

### 1. 카카오 개발자 콘솔 설정

#### 1.1 앱 생성 및 기본 설정
1. [카카오 개발자 콘솔](https://developers.kakao.com/)에 접속
2. **내 애플리케이션** > **애플리케이션 추가하기**
3. 앱 이름, 사업자명 입력 후 저장

#### 1.2 앱 키 확인
- **앱 설정** > **일반** > **앱 키**에서 **REST API 키** 복사
- 이 키를 `KAKAO_CLIENT_ID`로 사용

#### 1.3 플랫폼 등록
**앱 설정** > **플랫폼** > **플랫폼 추가**에서:

**Android 앱:**
```
패키지명: com.yourcompany.selo (실제 앱 패키지명)
키 해시: 개발/배포용 키 해시 등록
```

**iOS 앱:**
```
번들 ID: com.yourcompany.selo (실제 번들 ID)
```

**Web:**
```
사이트 도메인: https://api.selo-ai.my (백엔드 도메인)
```

#### 1.4 Redirect URI 설정
**앱 설정** > **카카오 로그인** > **Redirect URI** 등록:

```
개발환경: http://127.0.0.1:3000/social/kakao
운영환경: https://api.selo-ai.my/auth/kakao/callback
```

#### 1.5 동의항목 설정
**앱 설정** > **카카오 로그인** > **동의항목**:

| 항목 | 설정 | 사용 목적 |
|-----|-----|----------|
| 닉네임 | 필수 동의 | 사용자 식별 |
| 프로필 사진 | 선택 동의 | 프로필 이미지 |
| 카카오계정(이메일) | 선택 동의 | 계정 관리 |

### 2. 비즈니스 채널 설정 (선택사항)
**서비스 관리** > **비즈니스 채널**에서 카카오톡 채널 연결 가능

---

## ⚙️ 백엔드 설정

### 1. 환경 변수 설정

#### `/home/ubuntu/dev/selo-v2-be/app.env` 파일 수정:
```bash
# 카카오 로그인 설정
KAKAO_CLIENT_ID=your_kakao_rest_api_key_here
KAKAO_REDIRECT_URI=http://127.0.0.1:3000/social/kakao

# JWT 설정 (이미 설정되어 있음)
APP_JWT_SECRET=your_super_secret_jwt_key_here
APP_JWT_ALG=HS256
APP_JWT_EXP_MINUTES=10080
```

**⚠️ 중요:** 
- `KAKAO_CLIENT_ID`: 카카오 개발자 콘솔의 REST API 키
- `KAKAO_REDIRECT_URI`: 클라이언트 앱에서 사용할 리다이렉트 URI
- `APP_JWT_SECRET`: 32자 이상의 안전한 랜덤 문자열

### 2. Django 설정 확인

**기본 설정들이 이미 구성되어 있습니다:**

- **사용자 모델**: `users.User` (카카오 로그인 지원)
- **인증 클래스**: JWT + DRF Token 인증
- **카카오 로그인 뷰**: `users.views.KakaoLogin`
- **URL 라우팅**: `/api/v1/auth/kakao/`

### 3. 필요 패키지 확인

```bash
# 이미 설치되어 있는 패키지들
pip list | grep -E "(requests|PyJWT|djangorestframework)"
```

---

## 📱 클라이언트 연동

### React Native 예제

#### 1. 카카오 SDK 설치
```bash
npm install @react-native-seoul/kakao-login
cd ios && pod install  # iOS 전용
```

#### 2. 카카오 로그인 구현
```javascript
// KakaoLogin.js
import {KakaoOAuthToken, getProfile, login} from '@react-native-seoul/kakao-login';

const KakaoLoginButton = () => {
  const handleKakaoLogin = async () => {
    try {
      // 1. 카카오 로그인으로 토큰 획득
      const token = await login();
      console.log('카카오 토큰:', token);

      // 2. 백엔드 서버에 토큰 전송
      const response = await fetch('https://api.selo-ai.my/api/v1/auth/kakao/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          access_token: token.accessToken, // 카카오 액세스 토큰
        }),
      });

      const result = await response.json();

      if (response.ok) {
        // 3. 로그인 성공 - JWT 토큰 저장
        await AsyncStorage.setItem('jwt_token', result.jwt_token);
        await AsyncStorage.setItem('user_data', JSON.stringify(result.user));
        
        console.log('로그인 성공:', result);
        // 메인 화면으로 이동
        navigation.navigate('Main');
      } else {
        console.error('로그인 실패:', result);
        Alert.alert('로그인 실패', result.error);
      }
    } catch (error) {
      console.error('카카오 로그인 에러:', error);
      Alert.alert('로그인 에러', error.message);
    }
  };

  return (
    <TouchableOpacity onPress={handleKakaoLogin} style={styles.kakaoButton}>
      <Text style={styles.buttonText}>카카오로 로그인</Text>
    </TouchableOpacity>
  );
};
```

### Web/JavaScript 예제

```html
<!-- 카카오 JavaScript SDK -->
<script src="https://t1.kakaocdn.net/kakao_js_sdk/2.6.0/kakao.min.js"></script>

<script>
// 1. SDK 초기화
Kakao.init('YOUR_KAKAO_JAVASCRIPT_KEY'); // JavaScript 키 사용

// 2. 로그인 함수
function loginWithKakao() {
  Kakao.Auth.authorize({
    redirectUri: 'http://127.0.0.1:3000/social/kakao',
    state: 'optional_state_parameter',
  });
}

// 3. 콜백 처리 (리다이렉트된 페이지에서)
function handleKakaoCallback() {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get('code');
  
  if (code) {
    // 백엔드로 인가 코드 전송
    fetch('https://api.selo-ai.my/api/v1/auth/kakao/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code: code }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.jwt_token) {
        // JWT 토큰 저장 및 로그인 성공 처리
        localStorage.setItem('jwt_token', data.jwt_token);
        localStorage.setItem('user_data', JSON.stringify(data.user));
        window.location.href = '/dashboard';
      }
    })
    .catch(error => {
      console.error('Login error:', error);
    });
  }
}
</script>
```

---

## 🔗 API 사용법

### 카카오 로그인 API

**Endpoint:** `POST /api/v1/auth/kakao/`

#### 요청
```json
{
  "code": "카카오_인가_코드"
}
```

**또는 (React Native용):**
```json
{
  "access_token": "카카오_액세스_토큰"
}
```

#### 성공 응답 (200 OK)
```json
{
  "message": "카카오 로그인 성공",
  "user": {
    "id": 1,
    "username": "kakao_1234567890",
    "email": "user@example.com",
    "nickname": "홍길동",
    "profile_image": "https://k.kakaocdn.net/dn/profile.jpg",
    "is_onboarding": false,
    "user_type": {
      "id": 2,
      "seloing_type": "성장중인 소통 초보형",
      "description": "설명이 없습니다."
    },
    "seloing_info": [],
    "isConsentPersonalInfo": false,
    "isConsentMarketing": false,
    "date_joined": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T12:00:00Z"
  },
  "jwt_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "drf_token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "is_new_user": true
}
```

#### 에러 응답
```json
// 400 Bad Request
{
  "error": "인가 코드가 필요합니다."
}

// 400 Bad Request  
{
  "error": "카카오 토큰 받기에 실패했습니다."
}

// 500 Internal Server Error
{
  "error": "로그인 처리 중 오류가 발생했습니다: 상세 에러 메시지"
}
```

### JWT 토큰 검증 API

**Endpoint:** `POST /api/v1/auth/verify/`

#### 요청
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 응답
```json
// 유효한 토큰
{
  "valid": true,
  "user": {
    "id": 1,
    "username": "kakao_1234567890",
    "nickname": "홍길동"
    // ... 사용자 정보
  }
}

// 무효한 토큰  
{
  "valid": false,
  "error": "유효하지 않은 토큰입니다."
}
```

### 인증된 API 호출

#### JWT 토큰 사용
```bash
curl -H "Authorization: Bearer your_jwt_token" \
     https://api.selo-ai.my/api/v1/users/1/
```

#### DRF 토큰 사용 (기존 방식)
```bash
curl -H "Authorization: Token your_drf_token" \
     https://api.selo-ai.my/api/v1/users/1/
```

---

## 🔧 문제 해결

### 자주 발생하는 문제들

#### 1. "카카오 토큰 받기에 실패했습니다"
**원인:**
- 잘못된 `KAKAO_CLIENT_ID`
- 잘못된 `KAKAO_REDIRECT_URI`
- 인가 코드 만료 (10분 유효)

**해결책:**
```bash
# 1. 환경변수 확인
grep KAKAO /home/ubuntu/dev/selo-v2-be/app.env

# 2. 카카오 개발자 콘솔에서 앱 키 재확인
# 3. Redirect URI가 정확히 일치하는지 확인
```

#### 2. "Invalid token header" 에러
**원인:** JWT 토큰 헤더 형식 오류

**해결책:**
```javascript
// 올바른 헤더 형식
headers: {
  'Authorization': 'Bearer ' + jwt_token,  // 'Bearer ' 접두사 필수
  'Content-Type': 'application/json'
}
```

#### 3. CORS 에러 (웹 클라이언트)
**원인:** CORS 설정 문제

**해결책:**
```python
# config/settings/base.py에서 CORS 설정 확인
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:3000",
    "https://your-frontend-domain.com",
]

CORS_ALLOW_CREDENTIALS = True
```

#### 4. 카카오 앱 검수 관련
**현재 상태:** 개발 중 (검수 불필요)
**배포 시:** 카카오 앱 검수 신청 필요

**검수 준비사항:**
- 개인정보처리방침
- 서비스 이용약관  
- 앱 아이콘 및 스크린샷
- 카카오 로그인 사용 목적 설명

### 디버깅 방법

#### 1. 백엔드 로그 확인
```bash
# Docker 로그 확인
sudo docker compose logs web -f --tail=100

# Django 로그 확인
tail -f /home/ubuntu/dev/selo-v2-be/logs/django.log
```

#### 2. 카카오 API 응답 테스트
```bash
# 토큰 발급 테스트
curl -X POST "https://kauth.kakao.com/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&code=YOUR_CODE"

# 사용자 정보 조회 테스트  
curl -X GET "https://kapi.kakao.com/v2/user/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 3. 클라이언트 디버깅
```javascript
// React Native에서 네트워크 요청 로깅
import {XMLHttpRequest} from 'xmlhttprequest';
global.XMLHttpRequest = XMLHttpRequest;

// 요청/응답 로그 출력
fetch(url, options)
  .then(response => {
    console.log('Response status:', response.status);
    console.log('Response headers:', response.headers);
    return response.json();
  })
  .then(data => {
    console.log('Response data:', data);
  });
```

---

## 🚀 운영 환경 배포 시 체크리스트

- [ ] **환경변수 설정**
  - [ ] `KAKAO_CLIENT_ID` 운영 키로 변경
  - [ ] `KAKAO_REDIRECT_URI` 운영 도메인으로 변경
  - [ ] `APP_JWT_SECRET` 안전한 키로 변경

- [ ] **카카오 앱 설정**
  - [ ] 운영 도메인 플랫폼 추가
  - [ ] 운영 Redirect URI 추가  
  - [ ] 앱 검수 신청 (필요시)

- [ ] **보안 설정**
  - [ ] HTTPS 인증서 적용
  - [ ] CORS 설정 확인
  - [ ] 로그 레벨 조정

- [ ] **모니터링**
  - [ ] 로그인 성공/실패 로그 모니터링
  - [ ] API 응답 시간 모니터링
  - [ ] 에러 알림 설정

---

## 📞 지원 및 문의

문제가 발생하면 다음을 확인해주세요:

1. **카카오 개발자 문서**: https://developers.kakao.com/docs
2. **Django REST Framework 문서**: https://www.django-rest-framework.org/
3. **프로젝트 로그**: `/home/ubuntu/dev/selo-v2-be/logs/`
4. **GitHub Issues**: 프로젝트 저장소의 Issues 탭

