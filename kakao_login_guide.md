# 🔐 JWT 기반 카카오 소셜 로그인 가이드

## 📱 React Native 앱에서 사용하기

### 1. 카카오 로그인 플로우

```
1. 앱에서 카카오 SDK로 인가 코드 받기
2. 인가 코드를 백엔드로 전송
3. 백엔드에서 카카오 API로 토큰 교환
4. 사용자 정보로 회원가입/로그인 처리
5. JWT 토큰 발급하여 앱으로 반환
```

### 2. API 엔드포인트

#### 카카오 로그인
```
POST /api/v1/auth/kakao/
Content-Type: application/json

Request Body:
{
    "code": "카카오_인가_코드"
}

Response (성공):
{
    "message": "카카오 로그인 성공",
    "user": {
        "id": 1,
        "username": "kakao_123456789",
        "email": "user@kakao.com",
        "nickname": "카카오사용자",
        "profile_image": "http://...",
        "is_onboarding": false,
        "user_type": null
    },
    "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "drf_token": "abc123def456...",
    "is_new_user": true
}

Response (실패):
{
    "error": "인가 코드가 필요합니다."
}
```

#### JWT 토큰 검증
```
POST /api/v1/auth/verify/
Content-Type: application/json

Request Body:
{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response (유효):
{
    "valid": true,
    "user": {
        "id": 1,
        "username": "kakao_123456789",
        "email": "user@kakao.com",
        "nickname": "카카오사용자"
    }
}

Response (무효):
{
    "valid": false,
    "error": "유효하지 않은 토큰입니다."
}
```

### 3. React Native 구현 예시

```javascript
// 카카오 로그인 함수
const kakaoLogin = async () => {
  try {
    // 1. 카카오 SDK로 인가 코드 받기
    const result = await KakaoSDK.login();
    const authCode = result.code;
    
    // 2. 백엔드로 인가 코드 전송
    const response = await fetch('/api/v1/auth/kakao/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code: authCode
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // 3. JWT 토큰 저장
      await AsyncStorage.setItem('jwt_token', data.jwt_token);
      await AsyncStorage.setItem('user_info', JSON.stringify(data.user));
      
      // 4. 신규 사용자면 온보딩으로, 기존 사용자면 메인으로
      if (data.is_new_user) {
        navigation.navigate('Onboarding');
      } else {
        navigation.navigate('Main');
      }
    } else {
      Alert.alert('로그인 실패', data.error);
    }
  } catch (error) {
    Alert.alert('오류', '로그인 중 오류가 발생했습니다.');
  }
};
```

### 4. JWT 토큰으로 API 호출

```javascript
// JWT 토큰으로 보호된 API 호출
const callProtectedAPI = async () => {
  const token = await AsyncStorage.getItem('jwt_token');
  
  const response = await fetch('/api/v1/users/1/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    }
  });
  
  if (response.status === 401) {
    // 토큰 만료 시 재로그인 필요
    navigation.navigate('Login');
  }
  
  const data = await response.json();
  return data;
};
```

### 5. 환경변수 설정

`.env` 파일에 다음 값들을 설정해야 합니다:

```bash
# 카카오 개발자 설정
KAKAO_CLIENT_ID=your_kakao_app_key
KAKAO_REDIRECT_URI=your_redirect_uri

# JWT 설정  
APP_JWT_SECRET=your_super_secret_jwt_key_here
```

### 6. 토큰 정보

- **JWT 토큰 만료**: 7일 (설정 가능)
- **알고리즘**: HS256
- **포함 정보**: user_id, username, email, exp, iat

### 7. 보안 고려사항

1. **JWT Secret**: 운영환경에서는 강력한 시크릿 키 사용
2. **HTTPS**: 운영환경에서 HTTPS 필수
3. **토큰 저장**: 앱에서 SecureStore 사용 권장
4. **만료 처리**: 토큰 만료 시 자동 재로그인 로직 구현

### 8. 트러블슈팅

#### 일반적인 오류들:

- `인가 코드가 필요합니다`: 카카오 SDK에서 올바른 인가 코드를 받지 못함
- `카카오 토큰 받기에 실패했습니다`: 카카오 클라이언트 ID나 리다이렉트 URI 확인
- `카카오 사용자 정보를 가져올 수 없습니다`: 카카오 API 호출 실패
- `유효하지 않은 토큰입니다`: JWT 토큰이 만료되었거나 변조됨

#### 디버깅:
```bash
# Django 로그 확인
tail -f logs/django.log

# 카카오 API 응답 확인  
curl -X POST https://kauth.kakao.com/oauth/token \
  -d "grant_type=authorization_code" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "redirect_uri=YOUR_REDIRECT_URI" \
  -d "code=YOUR_AUTH_CODE"
```

## 🎯 완료된 기능

✅ JWT 토큰 생성 및 검증  
✅ 카카오 OAuth 2.0 연동  
✅ 자동 회원가입/로그인  
✅ 사용자 정보 동기화  
✅ React Native 호환  
✅ 기존 DRF 토큰과 병행 지원  

이제 React Native 앱에서 카카오 소셜 로그인을 완전히 사용할 수 있습니다! 🚀