# Selo v2 Backend API Documentation

## Base URL
```
http://localhost:8000/api/v1/
```

## Authentication
- **JWT Authentication**: Include `Authorization: Bearer <access_token>` header for all authenticated requests
- **Token System**: 
  - Access Token: 5분 만료, API 호출용
  - Refresh Token: 4주 만료, 토큰 갱신용
  - 토큰 로테이션: Refresh 시 새로운 토큰 쌍 발급, 기존 토큰 무효화

---

## 1. Authentication

### 1.1 회원가입
```
POST /api/v1/signup/
```

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "password_confirm": "string",
    "nickname": "string",
    "profile_image": "string (optional)",
    "user_type": "integer (optional)",
    "isConsentPersonalInfo": "boolean",
    "isConsentMarketing": "boolean"
}
```

**Response (201 Created):**
```json
{
    "message": "회원가입이 완료되었습니다.",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "nickname": "테스트유저",
        "profile_image": "",
        "is_onboarding": false,
        "user_type": null,
        "seloing_info": [],
        "isConsentPersonalInfo": true,
        "isConsentMarketing": false,
        "date_joined": "2025-01-01T00:00:00Z",
        "last_login": null
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access_expires_in": 300,
    "refresh_expires_in": 2419200
}
```

**Error Responses:**
- `400 Bad Request`: 필수 필드 누락, 비밀번호 불일치, 이미 존재하는 사용자명, 비밀번호 정책 위반
- `500 Internal Server Error`: 서버 내부 오류

### 1.2 로그인
```
POST /api/v1/login/
```

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response (200 OK):**
```json
{
    "message": "로그인되었습니다.",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "nickname": "테스트유저",
        "profile_image": "",
        "is_onboarding": true,
        "user_type": {
            "id": 1,
            "seloing_type": "성장중인 소통 초보형",
            "description": "설명이 없습니다.",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        },
        "seloing_info": [
            {
                "id": 1,
                "goal": "발표 실력 향상",
                "job": "개발자",
                "interest": "기술 발표",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        ],
        "isConsentPersonalInfo": true,
        "isConsentMarketing": false,
        "date_joined": "2025-01-01T00:00:00Z",
        "last_login": "2025-01-01T00:00:00Z"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access_expires_in": 300,
    "refresh_expires_in": 2419200
}
```

**Error Responses:**
- `400 Bad Request`: 필수 필드 누락, 잘못된 로그인 정보
- `401 Unauthorized`: 비활성화된 계정
- `500 Internal Server Error`: 서버 내부 오류

### 1.3 로그아웃
```
POST /api/v1/logout/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body (Optional):**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "message": "로그아웃되었습니다."
}
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `500 Internal Server Error`: 서버 오류

### 1.4 카카오 소셜 로그인
```
POST /api/v1/auth/kakao/
```

**Headers:**
```
Content-Type: application/json
```

**Request Body (Web):**
```json
{
    "code": "카카오_인가_코드"
}
```

**Request Body (React Native):**
```json
{
    "access_token": "카카오_액세스_토큰"
}
```

**Response (200 OK):**
```json
{
    "message": "카카오 로그인 성공",
    "user": {
        "id": 2,
        "username": "kakao_1234567890",
        "email": "user@kakao.local",
        "nickname": "카카오사용자_12345678",
        "profile_image": "https://...",
        "is_onboarding": false,
        "user_type": null,
        "seloing_info": [],
        "isConsentPersonalInfo": false,
        "isConsentMarketing": false,
        "date_joined": "2025-01-01T00:00:00Z",
        "last_login": "2025-01-01T00:00:00Z"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access_expires_in": 300,
    "refresh_expires_in": 2419200,
    "is_new_user": true
}
```

**Error Responses:**
- `400 Bad Request`: 인가 코드 또는 액세스 토큰 누락, 잘못된 카카오 토큰
- `500 Internal Server Error`: 카카오 API 오류, 서버 내부 오류

### 1.5 토큰 리프레시
```
POST /api/v1/auth/refresh/
```

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access_expires_in": 300,
    "refresh_expires_in": 2419200
}
```

**Error Responses:**
- `400 Bad Request`: refresh_token 필드 누락
- `401 Unauthorized`: 유효하지 않거나 만료된 refresh token, 블랙리스트된 토큰
- `500 Internal Server Error`: 서버 오류

### 1.6 JWT 토큰 검증
```
POST /api/v1/auth/verify/
```

**Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
    "token": "jwt_token"
}
```

**Response (200 OK):**
```json
{
    "valid": true,
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "nickname": "테스트유저",
        "profile_image": "",
        "is_onboarding": true,
        "user_type": {
            "id": 1,
            "seloing_type": "성장중인 소통 초보형",
            "description": "설명이 없습니다.",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        },
        "seloing_info": [],
        "isConsentPersonalInfo": true,
        "isConsentMarketing": false,
        "date_joined": "2025-01-01T00:00:00Z",
        "last_login": "2025-01-01T00:00:00Z"
    }
}
```

**Error Responses:**
- `400 Bad Request`: token 필드 누락
- `401 Unauthorized`: 유효하지 않거나 만료된 토큰, 블랙리스트된 토큰

---

## 2. User Management

### 2.1 유저 리스트 조회 (관리자만)
```
GET /api/v1/users/
```

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "nickname": "테스트유저",
        "is_active": true,
        "date_joined": "2025-01-01T00:00:00Z",
        "last_login": "2025-01-01T00:00:00Z"
    }
]
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `403 Forbidden`: 관리자 권한 없음

### 2.2 유저 정보 조회 (본인만)
```
GET /api/v1/users/{user_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "nickname": "테스트유저",
    "profile_image": "",
    "is_onboarding": true,
    "user_type": {
        "id": 1,
        "seloing_type": "성장중인 소통 초보형",
        "description": "설명이 없습니다.",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    },
    "seloing_info": [
        {
            "id": 1,
            "goal": "발표 실력 향상",
            "job": "개발자",
            "interest": "기술 발표",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        }
    ],
    "isConsentPersonalInfo": true,
    "isConsentMarketing": false,
    "date_joined": "2025-01-01T00:00:00Z",
    "last_login": "2025-01-01T00:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `403 Forbidden`: 본인의 정보가 아님
- `404 Not Found`: 존재하지 않는 사용자

### 2.3 유저 정보 수정 (본인만)
```
PUT /api/v1/users/{user_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "nickname": "새로운닉네임",
    "profile_image": "https://...",
    "user_type": 2,
    "is_onboarding": true,
    "isConsentPersonalInfo": true,
    "isConsentMarketing": false
}
```

**Response (200 OK):**
```json
{
    "nickname": "새로운닉네임",
    "profile_image": "https://...",
    "user_type": 2,
    "is_onboarding": true,
    "isConsentPersonalInfo": true,
    "isConsentMarketing": false
}
```

**Error Responses:**
- `400 Bad Request`: 잘못된 요청 데이터
- `401 Unauthorized`: 유효하지 않은 access token
- `403 Forbidden`: 본인의 정보가 아님
- `404 Not Found`: 존재하지 않는 사용자

### 2.4 유저 회원 탈퇴 (본인만)
```
DELETE /api/v1/users/{user_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (204 No Content):**
```json
{
    "message": "회원 탈퇴가 완료되었습니다."
}
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `403 Forbidden`: 본인의 계정이 아님
- `404 Not Found`: 존재하지 않는 사용자

### 2.5 유저 온보딩 완료 (본인만)
```
PUT /api/v1/users/{user_id}/onboarding/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "goal": "발표 실력 향상",
    "job": "개발자",
    "interest": "기술 발표",
    "user_type_id": 2
}
```

**Response (200 OK):**
```json
{
    "message": "온보딩이 완료되었습니다.",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "nickname": "테스트유저",
        "profile_image": "",
        "is_onboarding": true,
        "user_type": {
            "id": 2,
            "seloing_type": "신중한 전략가형",
            "description": "설명이 없습니다.",
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-01T00:00:00Z"
        },
        "seloing_info": [
            {
                "id": 1,
                "goal": "발표 실력 향상",
                "job": "개발자",
                "interest": "기술 발표",
                "created_at": "2025-01-01T00:00:00Z",
                "updated_at": "2025-01-01T00:00:00Z"
            }
        ],
        "isConsentPersonalInfo": true,
        "isConsentMarketing": false,
        "date_joined": "2025-01-01T00:00:00Z",
        "last_login": "2025-01-01T00:00:00Z"
    }
}
```

**Error Responses:**
- `400 Bad Request`: 잘못된 요청 데이터, 잘못된 user_type_id
- `401 Unauthorized`: 유효하지 않은 access token
- `403 Forbidden`: 본인의 정보가 아님
- `404 Not Found`: 존재하지 않는 사용자

### 2.6 유저 셀로잉 이력 조회 (본인만, 완료된 것만)
```
GET /api/v1/users/{user_id}/seloing/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "topic": {
            "id": 1,
            "title": "효과적인 프레젠테이션 기법",
            "content": "프레젠테이션을 할 때 중요한 것은...",
            "category": "발표",
            "difficulty": "중급",
            "estimated_time": 300,
            "created_at": "2025-01-01T00:00:00Z"
        },
        "is_completed": true,
        "speech_text": "안녕하세요, 오늘은 효과적인 프레젠테이션에 대해...",
        "feedback": {
            "overall_score": 85,
            "pronunciation_score": 80,
            "fluency_score": 90,
            "content_score": 85,
            "detailed_feedback": "전반적으로 좋은 발표였습니다..."
        },
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }
]
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `403 Forbidden`: 본인의 이력이 아님
- `404 Not Found`: 존재하지 않는 사용자

### 2.7 유저 셀로잉 이력 상세 조회 (본인만)
```
GET /api/v1/users/{user_id}/seloing/{seloing_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "topic": {
        "id": 1,
        "title": "효과적인 프레젠테이션 기법",
        "content": "프레젠테이션을 할 때 중요한 것은...",
        "category": "발표",
        "difficulty": "중급",
        "estimated_time": 300,
        "created_at": "2025-01-01T00:00:00Z"
    },
    "is_completed": true,
    "speech_text": "안녕하세요, 오늘은 효과적인 프레젠테이션에 대해...",
    "feedback": {
        "overall_score": 85,
        "pronunciation_score": 80,
        "fluency_score": 90,
        "content_score": 85,
        "detailed_feedback": "전반적으로 좋은 발표였습니다..."
    },
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: 완료되지 않은 셀로잉
- `401 Unauthorized`: 유효하지 않은 access token
- `403 Forbidden`: 본인의 이력이 아님
- `404 Not Found`: 존재하지 않는 사용자 또는 셀로잉

### 2.8 유저 보상 정보 조회 (본인만)
```
GET /api/v1/users/me/rewards/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "total_exp": 150,
    "total_candy": 300
}
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `404 Not Found`: 해당 유저의 통계가 존재하지 않습니다

### 2.9 특정 유저 보상 정보 조회 (본인만 또는 관리자)
```
GET /api/v1/users/{user_id}/rewards/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "total_exp": 150,
    "total_candy": 300
}
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `403 Forbidden`: 본인의 정보만 조회할 수 있습니다
- `404 Not Found`: 존재하지 않는 사용자 또는 해당 유저의 통계가 존재하지 않습니다

### 2.10 온보딩 대화 세션 시작/조회
```
GET /api/v1/users/onboarding/chat/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "current_step": "goal",
    "is_active": true,
    "messages": [
        {
            "id": 1,
            "sender": "ai",
            "content": "안녕하세요! 셀로에 오신 것을 환영합니다 🎉\n\n셀로 사용을 위해 몇 가지 질문을 드릴게요. 먼저 셀로를 사용하는 목표가 무엇인가요?\n\n예를 들어:\n- 발표 실력 향상\n- 면접 준비\n- 일상 대화 실력 향상\n- 영업 스킬 개발\n\n어떤 목표를 가지고 계신지 자유롭게 말씀해 주세요!",
            "step": "goal",
            "created_at": "2025-01-01T00:00:00Z"
        }
    ],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
}
```

**설명:**
- 첫 호출 시 새 온보딩 세션이 생성되고 AI의 환영 메시지가 포함됩니다
- 이미 활성 세션이 있다면 기존 세션 정보를 반환합니다

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token

### 2.11 온보딩 대화 메시지 전송
```
POST /api/v1/users/onboarding/chat/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "message": "발표 실력을 향상시켜서 회사에서 자신있게 프레젠테이션하고 싶어요"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "current_step": "job",
    "is_active": true,
    "messages": [
        {
            "id": 1,
            "sender": "ai",
            "content": "안녕하세요! 셀로에 오신 것을 환영합니다 🎉...",
            "step": "goal",
            "created_at": "2025-01-01T00:00:00Z"
        },
        {
            "id": 2,
            "sender": "user",
            "content": "발표 실력을 향상시켜서 회사에서 자신있게 프레젠테이션하고 싶어요",
            "step": "goal",
            "created_at": "2025-01-01T00:00:00Z"
        },
        {
            "id": 3,
            "sender": "ai",
            "content": "발표 실력 향상이 목표시군요! 정말 좋은 목표입니다 👍 그렇다면 현재 어떤 일을 하고 계신가요? 직업이나 상황을 알려주시면 더 맞춤형 피드백을 드릴 수 있어요!",
            "step": "goal",
            "created_at": "2025-01-01T00:00:00Z"
        }
    ],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
}
```

**온보딩 단계:**
- `goal`: 목표 파악 단계
- `job`: 직업/상황 파악 단계
- `interest`: 관심사 파악 단계
- `completed`: 온보딩 완료

**온보딩 완료 시 자동 처리:**
- `UserSelloingInfo`에 목표, 직업, 관심사 정보 저장
- 사용자의 `is_onboarding` 필드가 `true`로 변경
- 세션이 비활성화(`is_active: false`)

**Error Responses:**
- `400 Bad Request`: message 필드 누락, 활성 온보딩 세션이 없음
- `401 Unauthorized`: 유효하지 않은 access token

---

## 3. Seloing (Speech Analysis)

### 3.1 새로운 주제 생성 (AI 기반)
```
POST /api/v1/seloing/topics/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:** 없음 (AI가 사용자 정보를 기반으로 자동 생성)

**Response (201 Created):**
```json
{
    "id": 1,
    "topic1": "효과적인 프레젠테이션 기법에 대해 3분간 발표해보세요",
    "topic2": "새로운 기술 트렌드에 대한 본인의 견해를 말해보세요",
    "topic3": "팀워크의 중요성에 대해 설명해보세요",
    "is_select": "none",
    "created_at": "2025-01-01T00:00:00Z"
}
```

**또는 최근 주제 조회:**
```
GET /api/v1/seloing/topics/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "topic1": "효과적인 프레젠테이션 기법에 대해 3분간 발표해보세요",
    "topic2": "새로운 기술 트렌드에 대한 본인의 견해를 말해보세요",
    "topic3": "팀워크의 중요성에 대해 설명해보세요",
    "is_select": "none",
    "created_at": "2025-01-01T00:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `404 Not Found`: (GET) 생성된 주제가 없음
- `500 Internal Server Error`: AI 서비스 오류

### 3.2 주제 상세 조회 및 선택
```
GET /api/v1/seloing/topics/{topic_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "topic1": "효과적인 프레젠테이션 기법에 대해 3분간 발표해보세요",
    "topic2": "새로운 기술 트렌드에 대한 본인의 견해를 말해보세요",
    "topic3": "팀워크의 중요성에 대해 설명해보세요",
    "is_select": "none",
    "created_at": "2025-01-01T00:00:00Z"
}
```

**주제 선택 업데이트:**
```
PUT /api/v1/seloing/topics/{topic_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "is_select": "1"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "topic1": "효과적인 프레젠테이션 기법에 대해 3분간 발표해보세요",
    "topic2": "새로운 기술 트렌드에 대한 본인의 견해를 말해보세요",
    "topic3": "팀워크의 중요성에 대해 설명해보세요",
    "is_select": "1",
    "created_at": "2025-01-01T00:00:00Z"
}
```

**is_select 값:**
- `"none"`: 선택안함
- `"1"`: 첫번째 주제
- `"2"`: 두번째 주제  
- `"3"`: 세번째 주제
- `"skip"`: 다시뽑기

**Error Responses:**
- `400 Bad Request`: 잘못된 is_select 값
- `401 Unauthorized`: 유효하지 않은 access token
- `403 Forbidden`: 본인의 주제가 아님
- `404 Not Found`: 존재하지 않는 주제

### 3.3 셀로잉 세션 생성
```
POST /api/v1/seloing/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
    "selected_topic": "효과적인 프레젠테이션 기법에 대해 3분간 발표해보세요"
}
```

**Response (201 Created):**
```json
{
    "message": "셀로잉이 생성되었습니다.",
    "seloing_id": 1,
    "selected_topic": "효과적인 프레젠테이션 기법에 대해 3분간 발표해보세요"
}
```

**Error Responses:**
- `400 Bad Request`: selected_topic 필드 누락
- `401 Unauthorized`: 유효하지 않은 access token

### 3.4 녹음 파일 업로드 및 분석 요청
```
POST /api/v1/seloing/{seloing_id}/recording/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
audio_file: <audio_file.wav>
```

**Response (202 Accepted):**
```json
{
    "message": "분석 요청이 처리되었습니다.",
    "seloing_id": 1,
    "status": "processing"
}
```

**Error Responses:**
- `400 Bad Request`: 오디오 파일 누락, 지원하지 않는 파일 형식, 파일 크기 초과
- `401 Unauthorized`: 유효하지 않은 access token
- `403 Forbidden`: 본인의 셀로잉이 아님
- `404 Not Found`: 존재하지 않는 셀로잉
- `409 Conflict`: 이미 완료된 셀로잉

### 3.5 분석 진행 상태 조회
```
GET /api/v1/seloing/{seloing_id}/progress/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "seloing_id": 1,
    "status": "processing",
    "progress": 75,
    "message": "음성 분석 중입니다..."
}
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `403 Forbidden`: 본인의 셀로잉이 아님
- `404 Not Found`: 존재하지 않는 셀로잉

### 3.6 분석 결과 조회
```
GET /api/v1/seloing/{seloing_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "id": 1,
    "topic": {
        "id": 1,
        "title": "효과적인 프레젠테이션 기법",
        "content": "프레젠테이션을 할 때 중요한 것은...",
        "category": "발표",
        "difficulty": "중급",
        "estimated_time": 300,
        "created_at": "2025-01-01T00:00:00Z"
    },
    "is_completed": true,
    "speech_text": "안녕하세요, 오늘은 효과적인 프레젠테이션에 대해 말씀드리겠습니다...",
    "feedback": {
        "overall_score": 85,
        "pronunciation_score": 80,
        "fluency_score": 90,
        "content_score": 85,
        "detailed_feedback": "전반적으로 좋은 발표였습니다. 발음이 명확하고 내용 구성이 체계적입니다. 다만 말하는 속도를 조금 더 천천히 하시면 더 좋을 것 같습니다."
    },
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-01T00:00:00Z"
}
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `403 Forbidden`: 본인의 셀로잉이 아님
- `404 Not Found`: 존재하지 않는 셀로잉

### 3.7 AI 결과 콜백 (AI 서버 전용)
```
POST /api/v1/seloing/{seloing_id}/callback/
```

**Headers:**
```
Content-Type: application/json
X-API-Key: <ai_server_api_key>
```

**Request Body:**
```json
{
    "speech_text": "안녕하세요, 오늘은 효과적인 프레젠테이션에 대해...",
    "feedback": {
        "overall_score": 85,
        "pronunciation_score": 80,
        "fluency_score": 90,
        "content_score": 85,
        "detailed_feedback": "전반적으로 좋은 발표였습니다..."
    }
}
```

**Response (200 OK):**
```json
{
    "message": "분석 결과가 저장되었습니다.",
    "seloing_id": 1
}
```

**Error Responses:**
- `400 Bad Request`: 필수 필드 누락, 잘못된 데이터 형식
- `401 Unauthorized`: 유효하지 않은 API 키
- `404 Not Found`: 존재하지 않는 셀로잉
- `409 Conflict`: 이미 완료된 셀로잉

### 3.8 보상 지급 (자동/수동)

**자동 보상 지급:**
- 셀로잉이 완료(`is_completed = True`)되면 자동으로 보상이 지급됩니다
- AI 콜백에서 분석 결과 저장 시 자동 실행
- Signal을 통해 `SeloingReward` 생성 및 `UserStats` 업데이트

**수동 보상 지급 (백업/디버깅용):**
```
POST /api/v1/seloing/{seloing_id}/stat/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Response (201 Created):**
```json
{
    "message": "보상이 지급되었습니다."
}
```

**보상 계산 로직:**
- 점수 있음: `points = total_score * 10`, `experience = total_score * 5`
- 점수 없음: `points = 50`, `experience = 25`

**자동 업데이트 항목:**
- `UserStats`: total_seloings, total_points, total_experience, average_score
- `GlobalStats`: 3회 이상 완료 시 글로벌 랭킹에 포함

**Error Responses:**
- `400 Bad Request`: 완료되지 않은 셀로잉, 이미 보상을 받은 셀로잉
- `401 Unauthorized`: 유효하지 않은 access token
- `403 Forbidden`: 본인의 셀로잉이 아님
- `404 Not Found`: 존재하지 않는 셀로잉

---

## 4. Statistics & Ranking

### 4.1 랭킹 리스트 조회
```
GET /api/v1/ranking/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `category`: 카테고리별 필터링 (optional)
- `limit`: 결과 수 제한 (default: 10)

**Response (200 OK):**
```json
{
    "global_ranking": [
        {
            "rank": 1,
            "user": {
                "id": 2,
                "username": "topuser",
                "nickname": "최고유저",
                "profile_image": "https://..."
            },
            "total_seloings": 25,
            "average_score": 92.5,
            "total_points": 2500
        },
        {
            "rank": 2,
            "user": {
                "id": 1,
                "username": "testuser",
                "nickname": "테스트유저",
                "profile_image": ""
            },
            "total_seloings": 5,
            "average_score": 85.0,
            "total_points": 500
        }
    ],
    "my_ranking": {
        "rank": 2,
        "total_seloings": 5,
        "average_score": 85.0,
        "total_points": 500
    }
}
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `500 Internal Server Error`: 서버 오류

### 4.2 특정 유저 랭킹 상세 조회
```
GET /api/v1/ranking/{user_id}/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
    "user": {
        "id": 1,
        "username": "testuser",
        "nickname": "테스트유저",
        "profile_image": ""
    },
    "ranking": {
        "global_rank": 2,
        "total_seloings": 5,
        "average_score": 85.0,
        "total_points": 500,
        "total_experience": 250
    },
    "category_rankings": {
        "발표": {
            "rank": 1,
            "seloings_count": 3,
            "average_score": 88.0
        },
        "토론": {
            "rank": 5,
            "seloings_count": 2,
            "average_score": 82.0
        }
    },
    "recent_activity": [
        {
            "seloing_id": 5,
            "topic_title": "효과적인 프레젠테이션 기법",
            "score": 90,
            "completed_at": "2025-01-01T00:00:00Z"
        }
    ]
}
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `404 Not Found`: 존재하지 않는 사용자
- `500 Internal Server Error`: 서버 오류

---

## 5. Knowledge & Tips

### 5.1 지식 리스트 조회
```
GET /api/v1/knowledge/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `category`: 카테고리별 필터링 (optional)
- `search`: 검색어 (optional)

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "title": "효과적인 발표 기법",
        "content": "좋은 발표를 위한 핵심 요소들...",
        "category": "발표",
        "tags": ["프레젠테이션", "커뮤니케이션"],
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    }
]
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `500 Internal Server Error`: 서버 오류

### 5.2 팁 리스트 조회
```
GET /api/v1/tips/
```

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `category`: 카테고리별 필터링 (optional)

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "title": "긴장하지 않고 발표하는 방법",
        "content": "발표 전 긴장을 완화하는 효과적인 방법들...",
        "category": "발표",
        "difficulty": "초급",
        "read_time": 3,
        "created_at": "2025-01-01T00:00:00Z"
    }
]
```

**Error Responses:**
- `401 Unauthorized`: 유효하지 않은 access token
- `500 Internal Server Error`: 서버 오류

---

## 6. Media (Optional)

### 6.1 이미지 업로드
```
POST /api/v1/media/images/upload/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
image: <image_file.jpg>
description: "이미지 설명 (optional)"
```

**Response (201 Created):**
```json
{
    "id": 1,
    "url": "https://your-domain.com/media/images/image_file.jpg",
    "description": "이미지 설명",
    "uploaded_at": "2025-01-01T00:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: 이미지 파일 누락, 지원하지 않는 파일 형식, 파일 크기 초과
- `401 Unauthorized`: 유효하지 않은 access token
- `500 Internal Server Error`: 파일 업로드 오류

### 6.2 프로필 이미지 업로드
```
POST /api/v1/media/profile-images/upload/
```

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**
```
image: <profile_image.jpg>
```

**Response (201 Created):**
```json
{
    "id": 1,
    "url": "https://your-domain.com/media/profile-images/profile_image.jpg",
    "uploaded_at": "2025-01-01T00:00:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: 이미지 파일 누락, 지원하지 않는 파일 형식, 파일 크기 초과
- `401 Unauthorized`: 유효하지 않은 access token
- `500 Internal Server Error`: 파일 업로드 오류

---

## Global Error Responses

### 400 Bad Request
```json
{
    "error": "잘못된 요청입니다.",
    "details": {
        "field_name": ["필드 관련 오류 메시지"]
    }
}
```

### 401 Unauthorized
```json
{
    "error": "인증이 필요합니다.",
    "detail": "Authentication credentials were not provided."
}
```

**또는**

```json
{
    "error": "유효하지 않은 토큰입니다.",
    "detail": "Token is invalid or expired."
}
```

### 403 Forbidden
```json
{
    "error": "접근 권한이 없습니다.",
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "error": "요청한 리소스를 찾을 수 없습니다.",
    "detail": "Not found."
}
```

### 409 Conflict
```json
{
    "error": "요청이 현재 서버 상태와 충돌합니다.",
    "detail": "Conflict with current state."
}
```

### 429 Too Many Requests
```json
{
    "error": "요청 한도를 초과했습니다.",
    "detail": "Request was throttled. Expected available in X seconds."
}
```

### 500 Internal Server Error
```json
{
    "error": "서버 내부 오류가 발생했습니다.",
    "detail": "Internal server error occurred."
}
```

---

## Rate Limiting

- **일반 API**: 분당 100회 요청
- **인증 관련 API**: 분당 10회 요청
- **파일 업로드 API**: 분당 20회 요청

Rate limit 초과 시 429 에러와 함께 `Retry-After` 헤더가 반환됩니다.

## Notes

1. **보안**: 모든 API는 HTTPS를 통해 접근해야 합니다.
2. **날짜/시간**: ISO 8601 형식 (UTC)으로 반환됩니다.
3. **파일 업로드**: 최대 용량 제한이 있을 수 있습니다.
4. **토큰 만료**: Access Token은 5분, Refresh Token은 4주 후 만료됩니다.
5. **토큰 로테이션**: Refresh Token 사용 시 새로운 토큰 쌍이 발급되고 기존 토큰은 무효화됩니다.
6. **블랙리스트**: 무효화된 토큰들은 자동으로 블랙리스트에 등록되어 재사용이 차단됩니다.