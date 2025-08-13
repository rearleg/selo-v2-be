# 🚀 Selo v2 Backend API 가이드

## 📋 목차
- [개요](#개요)
- [인증](#인증)
- [공통 응답 형식](#공통-응답-형식)
- [사용자 관리 API](#사용자-관리-api)
- [인증 API](#인증-api)
- [셀로잉 API](#셀로잉-api)
- [통계 및 랭킹 API](#통계-및-랭킹-api)
- [팁과 지식 API](#팁과-지식-api)
- [미디어 API](#미디어-api)
- [에러 코드](#에러-코드)

---

## 🏗️ 개요

**Base URL:** `https://api.selo-ai.my/api/v1/`

**지원 형식:**
- 요청: `application/json`
- 응답: `application/json`
- 파일 업로드: `multipart/form-data`

**API 버전:** v1  
**마지막 업데이트:** 2024년 8월 13일

---

## 🔐 인증

### 지원하는 인증 방식

#### 1. JWT 토큰 (권장)
```http
Authorization: Bearer <jwt_token>
```

#### 2. DRF 토큰 (기존 호환성)
```http
Authorization: Token <drf_token>
```

### 토큰 획득 방법
- 일반 로그인: `POST /login/`
- 카카오 로그인: `POST /auth/kakao/`
- 회원가입: `POST /signup/`

---

## 📝 공통 응답 형식

### 성공 응답
```json
{
  "data": { /* 실제 데이터 */ },
  "message": "요청이 성공적으로 처리되었습니다."
}
```

### 에러 응답
```json
{
  "error": "에러 메시지",
  "code": "ERROR_CODE",
  "details": { /* 추가 에러 정보 */ }
}
```

### 페이지네이션 응답
```json
{
  "count": 100,
  "next": "https://api.selo-ai.my/api/v1/endpoint/?page=3",
  "previous": "https://api.selo-ai.my/api/v1/endpoint/?page=1",
  "results": [ /* 데이터 배열 */ ]
}
```

---

## 👤 사용자 관리 API

### 사용자 목록 조회 (관리자만)

**GET** `/users/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "https://api.selo-ai.my/api/v1/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "user123",
      "email": "user@example.com",
      "nickname": "홍길동",
      "is_active": true,
      "date_joined": "2024-01-01T00:00:00Z",
      "last_login": "2024-08-13T12:00:00Z"
    },
    {
      "id": 2,
      "username": "user456", 
      "email": "user2@example.com",
      "nickname": "김철수",
      "is_active": true,
      "date_joined": "2024-01-02T00:00:00Z",
      "last_login": "2024-08-13T11:30:00Z"
    }
  ]
}
```

### 사용자 정보 조회

**GET** `/users/{user_id}/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "nickname": "홍길동",
  "profile_image": "https://example.com/profile.jpg",
  "is_onboarding": false,
  "user_type": {
    "id": 2,
    "seloing_type": "성장중인 소통 초보형",
    "description": "설명이 없습니다.",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "seloing_info": [
    {
      "id": 1,
      "goal": "프레젠테이션 실력 향상",
      "job": "개발자",
      "interest": "기술, 독서",
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "isConsentPersonalInfo": true,
  "isConsentMarketing": false,
  "date_joined": "2024-01-01T00:00:00Z",
  "last_login": "2024-08-13T12:00:00Z"
}
```

**Response (403 Forbidden):**
```json
{
  "error": "본인의 정보만 조회할 수 있습니다.",
  "code": "USER_003"
}
```

**Response (404 Not Found):**
```json
{
  "error": "사용자를 찾을 수 없습니다.",
  "code": "USER_001"
}
```

### 사용자 정보 수정

**PUT** `/users/{user_id}/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "nickname": "새로운닉네임",
  "profile_image": "https://example.com/new_profile.jpg",
  "user_type": 3,
  "is_onboarding": true,
  "isConsentPersonalInfo": true,
  "isConsentMarketing": true
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "nickname": "새로운닉네임",
  "profile_image": "https://example.com/new_profile.jpg",
  "is_onboarding": true,
  "user_type": {
    "id": 3,
    "seloing_type": "신중한 전략가형",
    "description": "설명이 없습니다."
  },
  "isConsentPersonalInfo": true,
  "isConsentMarketing": true,
  "date_joined": "2024-01-01T00:00:00Z",
  "last_login": "2024-08-13T12:00:00Z"
}
```

### 사용자 정보 부분 수정

**PATCH** `/users/{user_id}/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "nickname": "변경할닉네임만"
}
```

**Response (200 OK):** PUT과 동일한 형식

### 회원 탈퇴

**DELETE** `/users/{user_id}/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (204 No Content):**
```json
{
  "message": "회원 탈퇴가 완료되었습니다."
}
```

### 사용자 셀로잉 이력 조회

**GET** `/users/{user_id}/seloing/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "selected_topic": "오늘의 날씨에 대해 이야기해보세요",
      "is_completed": true,
      "created_at": "2024-08-13T10:00:00Z",
      "updated_at": "2024-08-13T10:30:00Z"
    },
    {
      "id": 2,
      "selected_topic": "좋아하는 음식에 대해 설명해보세요",
      "is_completed": true,
      "created_at": "2024-08-12T15:20:00Z",
      "updated_at": "2024-08-12T15:50:00Z"
    }
  ]
}
```

### 사용자 셀로잉 상세 이력

**GET** `/users/{user_id}/seloing/{seloing_id}/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):** [셀로잉 결과 조회](#셀로잉-결과-조회)와 동일

---

## 🔑 인증 API

### 회원가입

**POST** `/signup/`

**Headers:**
```http
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "newuser123",
  "email": "newuser@example.com",
  "password": "securepassword123",
  "password_confirm": "securepassword123",
  "nickname": "새사용자",
  "profile_image": "https://example.com/profile.jpg",
  "user_type": 2,
  "isConsentPersonalInfo": true,
  "isConsentMarketing": false
}
```

**Response (201 Created):**
```json
{
  "message": "회원가입이 완료되었습니다.",
  "user": {
    "id": 10,
    "username": "newuser123",
    "email": "newuser@example.com",
    "nickname": "새사용자",
    "profile_image": "https://example.com/profile.jpg",
    "is_onboarding": false,
    "user_type": {
      "id": 2,
      "seloing_type": "성장중인 소통 초보형",
      "description": "설명이 없습니다."
    },
    "isConsentPersonalInfo": true,
    "isConsentMarketing": false,
    "date_joined": "2024-08-13T12:00:00Z",
    "last_login": null
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "입력 데이터가 올바르지 않습니다.",
  "code": "VALIDATION_ERROR",
  "details": {
    "username": ["이미 존재하는 사용자명입니다."],
    "password": ["비밀번호가 일치하지 않습니다."]
  }
}
```

### 로그인

**POST** `/login/`

**Headers:**
```http
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "user123",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "message": "로그인되었습니다.",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "nickname": "홍길동",
    "profile_image": "https://example.com/profile.jpg",
    "is_onboarding": false,
    "user_type": {
      "id": 2,
      "seloing_type": "성장중인 소통 초보형",
      "description": "설명이 없습니다."
    },
    "isConsentPersonalInfo": true,
    "isConsentMarketing": false,
    "date_joined": "2024-01-01T00:00:00Z",
    "last_login": "2024-08-13T12:00:00Z"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "로그인 정보가 올바르지 않습니다.",
  "code": "AUTH_004"
}
```

### 로그아웃

**POST** `/logout/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "message": "로그아웃되었습니다."
}
```

### 카카오 로그인

**POST** `/auth/kakao/`

**Headers:**
```http
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
    "id": 11,
    "username": "kakao_1234567890",
    "email": "user@kakao.example.com",
    "nickname": "카카오사용자",
    "profile_image": "https://k.kakaocdn.net/dn/profile.jpg",
    "is_onboarding": false,
    "user_type": {
      "id": 2,
      "seloing_type": "성장중인 소통 초보형",
      "description": "설명이 없습니다."
    },
    "isConsentPersonalInfo": false,
    "isConsentMarketing": false,
    "date_joined": "2024-08-13T12:00:00Z",
    "last_login": "2024-08-13T12:00:00Z"
  },
  "jwt_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMSwidXNlcm5hbWUiOiJrYWthb18xMjM0NTY3ODkwIiwiZW1haWwiOiJ1c2VyQGtha2FvLmV4YW1wbGUuY29tIiwiZXhwIjoxNzI0NTA3MjAwLCJpYXQiOjE3MjM5MDI0MDB9.signature",
  "drf_token": "abc123def456ghi789jkl012mno345pqr678stu",
  "is_new_user": true
}
```

**Response (400 Bad Request):**
```json
{
  "error": "인가 코드가 필요합니다.",
  "code": "KAKAO_001"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "카카오 토큰 받기에 실패했습니다.",
  "code": "KAKAO_002"
}
```

**Response (500 Internal Server Error):**
```json
{
  "error": "로그인 처리 중 오류가 발생했습니다: 상세 에러 메시지",
  "code": "INTERNAL_ERROR"
}
```

### JWT 토큰 검증

**POST** `/auth/verify/`

**Headers:**
```http
Content-Type: application/json
```

**Request Body:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK) - 유효한 토큰:**
```json
{
  "valid": true,
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "nickname": "홍길동",
    "profile_image": "https://example.com/profile.jpg",
    "is_onboarding": false,
    "user_type": {
      "id": 2,
      "seloing_type": "성장중인 소통 초보형"
    }
  }
}
```

**Response (401 Unauthorized) - 무효한 토큰:**
```json
{
  "valid": false,
  "error": "유효하지 않은 토큰입니다.",
  "code": "AUTH_001"
}
```

---

## 🎯 셀로잉 API

### 주제 생성

**POST** `/seloing/topics/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "interests": ["기술", "독서", "여행"],
  "difficulty": "intermediate",
  "category": "daily"
}
```

**Response (201 Created):**
```json
{
  "topics": [
    "최근에 읽은 기술 서적에 대해 설명해보세요",
    "여행 중 가장 인상깊었던 경험을 공유해주세요",
    "독서가 본인에게 미친 영향에 대해 이야기해보세요"
  ],
  "selected_topic": "최근에 읽은 기술 서적에 대해 설명해보세요",
  "difficulty": "intermediate",
  "category": "daily"
}
```

### 셀로잉 생성

**POST** `/seloing/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "selected_topic": "오늘의 날씨에 대해 이야기해보세요"
}
```

**Response (201 Created):**
```json
{
  "message": "셀로잉이 생성되었습니다.",
  "seloing_id": 123,
  "selected_topic": "오늘의 날씨에 대해 이야기해보세요"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "선택된 주제가 필요합니다.",
  "code": "SELOING_001",
  "details": {
    "selected_topic": ["이 필드는 필수입니다."]
  }
}
```

### 녹음 파일 업로드 및 분석 요청

**POST** `/seloing/{seloing_id}/recording/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Request Body (form-data):**
```
audio_file: [녹음 파일 (WAV, MP3, M4A 등)]
duration_seconds: 120.5
```

**Response (200 OK):**
```json
{
  "message": "녹음 파일이 업로드되었습니다. AI 분석이 진행중입니다.",
  "seloing_id": 123,
  "status": "analyzing",
  "filename": "seloing_123_recording.wav",
  "file_url": "https://storage.selo-ai.my/audio/seloing_123_recording.wav",
  "duration_seconds": 120.5,
  "estimated_completion": "2024-08-13T10:05:00Z"
}
```

**Response (400 Bad Request) - 이미 완료된 셀로잉:**
```json
{
  "error": "이미 완료된 셀로잉입니다.",
  "code": "SELOING_002"
}
```

**Response (413 Payload Too Large):**
```json
{
  "error": "파일 크기가 너무 큽니다. 최대 100MB까지 업로드 가능합니다.",
  "code": "FILE_002"
}
```

### 분석 상태 조회

**GET** `/seloing/{seloing_id}/progress/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK) - 분석 중:**
```json
{
  "seloing_id": 123,
  "status": "analyzing",
  "progress_percentage": 75,
  "current_step": "음성 전사 중...",
  "estimated_completion": "2024-08-13T10:05:00Z",
  "message": "AI가 음성을 분석하고 있습니다."
}
```

**Response (200 OK) - 분석 완료:**
```json
{
  "seloing_id": 123,
  "status": "completed",
  "progress_percentage": 100,
  "current_step": "분석 완료",
  "completed_at": "2024-08-13T10:04:30Z",
  "message": "분석이 완료되었습니다."
}
```

**Response (200 OK) - 분석 실패:**
```json
{
  "seloing_id": 123,
  "status": "failed",
  "progress_percentage": 0,
  "current_step": "분석 실패",
  "error_message": "음성 파일을 처리할 수 없습니다.",
  "message": "분석에 실패했습니다. 다시 시도해주세요."
}
```

### 셀로잉 결과 조회

**GET** `/seloing/{seloing_id}/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "id": 123,
  "user": 1,
  "selected_topic": "오늘의 날씨에 대해 이야기해보세요",
  "is_completed": true,
  "created_at": "2024-08-13T10:00:00Z",
  "updated_at": "2024-08-13T10:30:00Z",
  "analysis": {
    "id": 456,
    "original_transcript": "오늘 날씨가 정말 좋네요. 맑고 화창한 날씨입니다. 음... 이런 날에는 밖에 나가서 산책을 하고 싶어요.",
    "analyzed_transcript": "오늘 날씨가 정말 좋네요. 맑고 화창한 날씨입니다. 이런 날에는 밖에 나가서 산책을 하고 싶어요.",
    "disfluency_feedback": "전반적으로 유창한 발화를 보여주셨습니다. '음...' 과 같은 간투사가 1회 발견되었지만 자연스러운 범위 내입니다.",
    "topic_feedback": "주제에 적합한 내용으로 잘 구성되었습니다. 날씨에 대한 구체적인 묘사와 개인적인 감정을 잘 표현했습니다.",
    "stability_feedback": "안정적이고 자연스러운 톤으로 발화하셨습니다. 속도와 억양이 적절했습니다.",
    "created_at": "2024-08-13T10:30:00Z",
    "updated_at": "2024-08-13T10:30:00Z"
  },
  "result": {
    "id": 789,
    "total_score": 85,
    "repeat_score": 90,
    "topic_score": 85,
    "filler_score": 80,
    "stability_score": 85,
    "repeat_count": 1,
    "filler_count": 2,
    "created_at": "2024-08-13T10:30:00Z",
    "updated_at": "2024-08-13T10:30:00Z"
  },
  "audio": {
    "id": 101,
    "filename": "seloing_123_recording.wav",
    "file_url": "https://storage.selo-ai.my/audio/seloing_123_recording.wav",
    "duration_seconds": 120.5,
    "created_at": "2024-08-13T10:01:00Z",
    "updated_at": "2024-08-13T10:01:00Z"
  },
  "reward": {
    "id": 202,
    "earned_exp": 50,
    "earned_candy": 10,
    "created_at": "2024-08-13T10:30:00Z",
    "updated_at": "2024-08-13T10:30:00Z"
  }
}
```

**Response (400 Bad Request) - 완료되지 않은 셀로잉:**
```json
{
  "error": "아직 분석이 완료되지 않았습니다.",
  "code": "SELOING_003"
}
```

### AI 결과 콜백 (AI 서버 전용)

**POST** `/seloing/{seloing_id}/callback/`

**Headers:**
```http
Content-Type: application/json
X-API-Key: <internal_api_key>
```

**Request Body:**
```json
{
  "seloing_id": 123,
  "status": "completed",
  "analysis": {
    "original_transcript": "오늘 날씨가 정말 좋네요. 맑고 화창한 날씨입니다. 음... 이런 날에는 밖에 나가서 산책을 하고 싶어요.",
    "analyzed_transcript": "오늘 날씨가 정말 좋네요. 맑고 화창한 날씨입니다. 이런 날에는 밖에 나가서 산책을 하고 싶어요.",
    "disfluency_feedback": "전반적으로 유창한 발화를 보여주셨습니다.",
    "topic_feedback": "주제에 적합한 내용으로 잘 구성되었습니다.",
    "stability_feedback": "안정적이고 자연스러운 톤으로 발화하셨습니다."
  },
  "result": {
    "total_score": 85,
    "repeat_score": 90,
    "topic_score": 85,
    "filler_score": 80,
    "stability_score": 85,
    "repeat_count": 1,
    "filler_count": 2
  }
}
```

**Response (200 OK):**
```json
{
  "message": "AI 분석 결과가 성공적으로 저장되었습니다.",
  "seloing_id": 123,
  "status": "completed"
}
```

### 보상 지급

**POST** `/seloing/{seloing_id}/stat/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "message": "보상이 지급되었습니다.",
  "reward": {
    "earned_exp": 50,
    "earned_candy": 10
  },
  "user_stats": {
    "total_exp": 550,
    "total_candy": 110,
    "total_seloing_count": 11,
    "total_seloing_score_avg": 83.6
  },
  "level_up": false,
  "new_achievements": []
}
```

**Response (400 Bad Request) - 이미 보상을 받은 경우:**
```json
{
  "error": "이미 보상을 받은 셀로잉입니다.",
  "code": "REWARD_001"
}
```

---

## 📊 통계 및 랭킹 API

### 개인 통계 조회

**GET** `/ranking/user/{user_id}/stats/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "id": 1,
  "user": {
    "id": 1,
    "nickname": "홍길동",
    "profile_image": "https://example.com/profile.jpg"
  },
  "total_exp": 500,
  "total_candy": 100,
  "total_record_time": "02:30:45",
  "total_attendance_count": 15,
  "total_seloing_count": 10,
  "total_seloing_score": 850,
  "total_seloing_score_avg": 85.0,
  "total_repeat_score": 900,
  "total_stable_score": 850,
  "total_topic_score": 800,
  "total_filler_score": 850,
  "total_repeat_count": 5,
  "total_filler_count": 10,
  "rank_info": {
    "exp_rank": 5,
    "score_rank": 3,
    "total_users": 100
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-08-13T10:30:00Z"
}
```

### 글로벌 통계 조회

**GET** `/ranking/global/stats/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "id": 1,
  "global_exp": 50000,
  "global_candy": 10000,
  "global_record_time": "100:15:30",
  "global_attendance_count": 500,
  "global_seloing_count": 1000,
  "global_seloing_score": 85000,
  "global_seloing_score_avg": 85.0,
  "global_repeat_score": 90000,
  "global_stable_score": 85000,
  "global_topic_score": 80000,
  "global_filler_score": 85000,
  "global_repeat_count": 500,
  "global_filler_count": 1000,
  "active_users_count": 250,
  "monthly_stats": {
    "monthly_seloing_count": 150,
    "monthly_new_users": 25,
    "monthly_avg_score": 86.5
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-08-13T10:30:00Z"
}
```

### 사용자 랭킹 조회

**GET** `/ranking/leaderboard/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Query Parameters:**
- `type`: `exp` | `candy` | `score` | `count` (기본값: `score`)
- `limit`: 조회할 순위 수 (기본값: 10, 최대: 100)
- `period`: `all` | `monthly` | `weekly` (기본값: `all`)

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "ranking_type": "score",
  "period": "all",
  "updated_at": "2024-08-13T10:30:00Z",
  "my_rank": {
    "rank": 15,
    "score": 75.5,
    "seloing_count": 8
  },
  "results": [
    {
      "rank": 1,
      "user": {
        "id": 2,
        "nickname": "스피치마스터",
        "profile_image": "https://example.com/profile2.jpg"
      },
      "score": 95.5,
      "seloing_count": 50,
      "total_exp": 2500,
      "badge": "🏆"
    },
    {
      "rank": 2,
      "user": {
        "id": 5,
        "nickname": "발표의신",
        "profile_image": "https://example.com/profile5.jpg"
      },
      "score": 92.3,
      "seloing_count": 45,
      "total_exp": 2250,
      "badge": "🥈"
    },
    {
      "rank": 3,
      "user": {
        "id": 1,
        "nickname": "홍길동",
        "profile_image": "https://example.com/profile1.jpg"
      },
      "score": 85.0,
      "seloing_count": 10,
      "total_exp": 500,
      "badge": "🥉"
    }
  ]
}
```

---

## 💡 팁과 지식 API

### 팁 목록 조회

**GET** `/tips/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Query Parameters:**
- `search`: 검색 키워드 (선택)
- `category`: 카테고리 (선택)
- `page`: 페이지 번호 (기본값: 1)

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "count": 50,
  "next": "https://api.selo-ai.my/api/v1/tips/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "text": "발표할 때는 청중과 아이컨택을 유지하세요. 이를 통해 더 강한 연결감을 만들 수 있습니다.",
      "category": "presentation",
      "difficulty": "beginner",
      "likes_count": 45,
      "is_liked": false,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "text": "말하기 전에 깊게 숨을 쉬고 시작하세요. 이는 긴장을 완화하고 목소리를 안정시킵니다.",
      "category": "breathing",
      "difficulty": "beginner",
      "likes_count": 32,
      "is_liked": true,
      "created_at": "2024-01-02T00:00:00Z",
      "updated_at": "2024-01-02T00:00:00Z"
    }
  ]
}
```

### 특정 팁 조회

**GET** `/tips/{tip_id}/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "id": 1,
  "text": "발표할 때는 청중과 아이컨택을 유지하세요. 이를 통해 더 강한 연결감을 만들 수 있습니다.",
  "category": "presentation",
  "difficulty": "beginner",
  "likes_count": 45,
  "is_liked": false,
  "detailed_explanation": "아이컨택은 발표에서 가장 중요한 요소 중 하나입니다. 청중의 눈을 바라보면서 이야기하면 신뢰감을 높이고...",
  "related_tips": [2, 5, 8],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 팁 좋아요

**POST** `/tips/{tip_id}/like/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "message": "좋아요가 추가되었습니다.",
  "is_liked": true,
  "likes_count": 46
}
```

### 지식 목록 조회

**GET** `/knowledge/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Query Parameters:**
- `search`: 검색 키워드 (선택)
- `category`: 카테고리 (선택)
- `page`: 페이지 번호 (기본값: 1)

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "count": 30,
  "next": "https://api.selo-ai.my/api/v1/knowledge/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "효과적인 발표 기법",
      "summary": "발표에서 성공하기 위한 핵심 기법들을 소개합니다.",
      "category": "presentation",
      "difficulty": "intermediate",
      "read_time": 5,
      "likes_count": 128,
      "is_liked": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "title": "목소리 트레이닝 방법",
      "summary": "목소리의 질을 향상시키기 위한 실질적인 방법들을 알아봅시다.",
      "category": "voice_training",
      "difficulty": "beginner",
      "read_time": 7,
      "likes_count": 89,
      "is_liked": false,
      "created_at": "2024-01-02T00:00:00Z",
      "updated_at": "2024-01-02T00:00:00Z"
    }
  ]
}
```

### 특정 지식 조회

**GET** `/knowledge/{knowledge_id}/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "id": 1,
  "title": "효과적인 발표 기법",
  "detail": "효과적인 발표를 위해서는 다음과 같은 기법들을 활용할 수 있습니다.\n\n1. 구조화된 내용 구성\n- 서론, 본론, 결론의 명확한 구분\n- 각 섹션별 핵심 메시지 설정\n\n2. 청중과의 소통\n- 아이컨택 유지\n- 적절한 제스처 사용\n- 질문을 통한 상호작용\n\n3. 시각적 자료 활용\n- 간결하고 명확한 슬라이드\n- 그래프와 이미지의 효과적 사용\n\n이러한 기법들을 지속적으로 연습하면 발표 실력을 크게 향상시킬 수 있습니다.",
  "category": "presentation",
  "difficulty": "intermediate",
  "read_time": 5,
  "likes_count": 128,
  "is_liked": true,
  "tags": ["발표", "스피치", "커뮤니케이션"],
  "related_knowledge": [2, 5, 8],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### 지식 좋아요

**POST** `/knowledge/{knowledge_id}/like/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "message": "좋아요가 추가되었습니다.",
  "is_liked": true,
  "likes_count": 129
}
```

---

## 📁 미디어 API

### 파일 업로드

**POST** `/media/upload/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Request Body (form-data):**
```
file: [업로드할 파일]
file_type: "image" | "audio" | "document"
description: "파일 설명 (선택사항)"
```

**Response (201 Created):**
```json
{
  "id": 1,
  "filename": "uploaded_file.jpg",
  "original_filename": "my_photo.jpg",
  "file_url": "https://storage.selo-ai.my/media/uploaded_file.jpg",
  "file_type": "image",
  "file_size": 1048576,
  "description": "프로필 사진",
  "uploaded_by": {
    "id": 1,
    "nickname": "홍길동"
  },
  "created_at": "2024-08-13T10:00:00Z",
  "updated_at": "2024-08-13T10:00:00Z"
}
```

**Response (400 Bad Request) - 지원하지 않는 파일 형식:**
```json
{
  "error": "지원하지 않는 파일 형식입니다.",
  "code": "FILE_001",
  "details": {
    "supported_formats": ["jpg", "jpeg", "png", "gif", "wav", "mp3", "m4a", "pdf", "doc", "docx"]
  }
}
```

**Response (413 Payload Too Large):**
```json
{
  "error": "파일 크기가 너무 큽니다. 최대 50MB까지 업로드 가능합니다.",
  "code": "FILE_002"
}
```

### 파일 정보 조회

**GET** `/media/{media_id}/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "id": 1,
  "filename": "uploaded_file.jpg",
  "original_filename": "my_photo.jpg",
  "file_url": "https://storage.selo-ai.my/media/uploaded_file.jpg",
  "file_type": "image",
  "file_size": 1048576,
  "description": "프로필 사진",
  "uploaded_by": {
    "id": 1,
    "nickname": "홍길동",
    "profile_image": "https://example.com/profile.jpg"
  },
  "download_count": 5,
  "is_public": false,
  "created_at": "2024-08-13T10:00:00Z",
  "updated_at": "2024-08-13T10:00:00Z"
}
```

**Response (403 Forbidden):**
```json
{
  "error": "이 파일에 대한 접근 권한이 없습니다.",
  "code": "FILE_004"
}
```

### 내 파일 목록 조회

**GET** `/media/my/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Query Parameters:**
- `file_type`: `image` | `audio` | `document` (선택)
- `search`: 파일명 검색 (선택)
- `page`: 페이지 번호 (기본값: 1)

**Request Body:** 없음

**Response (200 OK):**
```json
{
  "count": 25,
  "next": "https://api.selo-ai.my/api/v1/media/my/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "filename": "profile.jpg",
      "original_filename": "my_profile_photo.jpg",
      "file_url": "https://storage.selo-ai.my/media/profile.jpg",
      "file_type": "image",
      "file_size": 1048576,
      "description": "프로필 사진",
      "download_count": 0,
      "created_at": "2024-08-13T10:00:00Z"
    },
    {
      "id": 2,
      "filename": "recording_20240813.wav",
      "original_filename": "voice_memo.wav",
      "file_url": "https://storage.selo-ai.my/media/recording_20240813.wav",
      "file_type": "audio",
      "file_size": 2097152,
      "description": "연습용 녹음",
      "download_count": 3,
      "created_at": "2024-08-12T15:30:00Z"
    }
  ]
}
```

### 파일 삭제

**DELETE** `/media/{media_id}/`

**Headers:**
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:** 없음

**Response (204 No Content):**
```json
{
  "message": "파일이 성공적으로 삭제되었습니다."
}
```

---

## ❌ 에러 코드

### HTTP 상태 코드

| 코드 | 의미 | 설명 |
|-----|-----|------|
| 200 | OK | 요청 성공 |
| 201 | Created | 리소스 생성 성공 |
| 204 | No Content | 요청 성공, 응답 본문 없음 |
| 400 | Bad Request | 잘못된 요청 |
| 401 | Unauthorized | 인증 필요 |
| 403 | Forbidden | 권한 없음 |
| 404 | Not Found | 리소스 없음 |
| 405 | Method Not Allowed | 허용되지 않은 HTTP 메서드 |
| 413 | Payload Too Large | 요청 본문이 너무 큼 |
| 429 | Too Many Requests | 요청 빈도 제한 초과 |
| 500 | Internal Server Error | 서버 내부 오류 |

### 커스텀 에러 코드

#### 인증 관련
- `AUTH_001`: 유효하지 않은 토큰
- `AUTH_002`: 토큰 만료
- `AUTH_003`: 권한 없음
- `AUTH_004`: 로그인 정보 불일치
- `AUTH_005`: 비활성화된 계정

#### 사용자 관련
- `USER_001`: 사용자를 찾을 수 없음
- `USER_002`: 중복된 사용자명
- `USER_003`: 접근 권한 없음 (본인 정보만 조회 가능)
- `USER_004`: 비밀번호 불일치

#### 셀로잉 관련
- `SELOING_001`: 선택된 주제가 필요함
- `SELOING_002`: 이미 완료된 셀로잉
- `SELOING_003`: 아직 분석이 완료되지 않음
- `SELOING_004`: 분석 실패
- `SELOING_005`: 오디오 파일 업로드 실패

#### 카카오 로그인 관련
- `KAKAO_001`: 인가 코드가 필요함
- `KAKAO_002`: 카카오 토큰 받기 실패
- `KAKAO_003`: 카카오 사용자 정보 조회 실패

#### 보상 관련
- `REWARD_001`: 이미 보상을 받은 셀로잉

#### 파일 관련
- `FILE_001`: 지원하지 않는 파일 형식
- `FILE_002`: 파일 크기 초과
- `FILE_003`: 파일 업로드 실패
- `FILE_004`: 파일 접근 권한 없음

#### 검증 관련
- `VALIDATION_ERROR`: 입력 데이터 검증 오류

### 에러 응답 예시

```json
{
  "error": "유효하지 않은 토큰입니다.",
  "code": "AUTH_001",
  "details": {
    "token": "만료되었거나 잘못된 형식의 토큰입니다.",
    "suggestion": "새로운 토큰을 발급받아 주세요."
  },
  "timestamp": "2024-08-13T10:00:00Z"
}
```

---

## 📋 사용 예시

### Python/requests 예시

```python
import requests
import json

# 베이스 URL
BASE_URL = "https://api.selo-ai.my/api/v1"

# 로그인
def login(username, password):
    response = requests.post(f"{BASE_URL}/login/", json={
        "username": username,
        "password": password
    })
    
    if response.status_code == 200:
        data = response.json()
        return data["token"]
    else:
        print(f"로그인 실패: {response.json()}")
        return None

# 사용자 정보 조회
def get_user_info(token, user_id):
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(f"{BASE_URL}/users/{user_id}/", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"사용자 정보 조회 실패: {response.json()}")
        return None

# 셀로잉 생성
def create_seloing(token, topic):
    headers = {
        "Authorization": f"Token {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(f"{BASE_URL}/seloing/", 
        headers=headers,
        json={"selected_topic": topic}
    )
    
    if response.status_code == 201:
        return response.json()["seloing_id"]
    else:
        print(f"셀로잉 생성 실패: {response.json()}")
        return None

# 녹음 파일 업로드
def upload_recording(token, seloing_id, audio_file_path, duration):
    headers = {"Authorization": f"Token {token}"}
    
    with open(audio_file_path, "rb") as audio_file:
        files = {"audio_file": audio_file}
        data = {"duration_seconds": duration}
        
        response = requests.post(
            f"{BASE_URL}/seloing/{seloing_id}/recording/",
            headers=headers,
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"녹음 파일 업로드 실패: {response.json()}")
        return None

# 사용 예시
if __name__ == "__main__":
    # 1. 로그인
    token = login("myusername", "mypassword")
    if not token:
        exit(1)
    
    # 2. 사용자 정보 확인
    user_info = get_user_info(token, 1)
    print(f"사용자: {user_info['nickname']}")
    
    # 3. 셀로잉 생성
    seloing_id = create_seloing(token, "오늘의 날씨에 대해 이야기해보세요")
    print(f"셀로잉 ID: {seloing_id}")
    
    # 4. 녹음 파일 업로드
    result = upload_recording(token, seloing_id, "recording.wav", 120.5)
    if result:
        print("녹음 파일 업로드 성공, 분석 진행 중...")
```

### JavaScript/fetch 예시

```javascript
const BASE_URL = "https://api.selo-ai.my/api/v1";

class SeloAPI {
  constructor() {
    this.token = null;
  }

  // 로그인
  async login(username, password) {
    try {
      const response = await fetch(`${BASE_URL}/login/`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password})
      });

      if (response.ok) {
        const data = await response.json();
        this.token = data.token;
        localStorage.setItem('selo_token', this.token);
        return data;
      } else {
        const error = await response.json();
        throw new Error(error.error);
      }
    } catch (error) {
      console.error('로그인 실패:', error);
      throw error;
    }
  }

  // 인증 헤더 생성
  getAuthHeaders() {
    if (!this.token) {
      throw new Error('토큰이 없습니다. 먼저 로그인해주세요.');
    }
    return {
      "Authorization": `Token ${this.token}`,
      "Content-Type": "application/json"
    };
  }

  // 사용자 정보 조회
  async getUserInfo(userId) {
    try {
      const response = await fetch(`${BASE_URL}/users/${userId}/`, {
        headers: this.getAuthHeaders()
      });

      if (response.ok) {
        return await response.json();
      } else {
        const error = await response.json();
        throw new Error(error.error);
      }
    } catch (error) {
      console.error('사용자 정보 조회 실패:', error);
      throw error;
    }
  }

  // 셀로잉 생성
  async createSeloing(topic) {
    try {
      const response = await fetch(`${BASE_URL}/seloing/`, {
        method: "POST",
        headers: this.getAuthHeaders(),
        body: JSON.stringify({selected_topic: topic})
      });

      if (response.ok) {
        const data = await response.json();
        return data.seloing_id;
      } else {
        const error = await response.json();
        throw new Error(error.error);
      }
    } catch (error) {
      console.error('셀로잉 생성 실패:', error);
      throw error;
    }
  }

  // 녹음 파일 업로드
  async uploadRecording(seloingId, audioFile, duration) {
    try {
      const formData = new FormData();
      formData.append("audio_file", audioFile);
      formData.append("duration_seconds", duration.toString());

      const response = await fetch(
        `${BASE_URL}/seloing/${seloingId}/recording/`,
        {
          method: "POST",
          headers: {"Authorization": `Token ${this.token}`},
          body: formData
        }
      );

      if (response.ok) {
        return await response.json();
      } else {
        const error = await response.json();
        throw new Error(error.error);
      }
    } catch (error) {
      console.error('녹음 파일 업로드 실패:', error);
      throw error;
    }
  }

  // 분석 상태 조회
  async checkAnalysisProgress(seloingId) {
    try {
      const response = await fetch(
        `${BASE_URL}/seloing/${seloingId}/progress/`,
        {headers: this.getAuthHeaders()}
      );

      if (response.ok) {
        return await response.json();
      } else {
        const error = await response.json();
        throw new Error(error.error);
      }
    } catch (error) {
      console.error('분석 상태 조회 실패:', error);
      throw error;
    }
  }

  // 셀로잉 결과 조회
  async getSeloingResult(seloingId) {
    try {
      const response = await fetch(
        `${BASE_URL}/seloing/${seloingId}/`,
        {headers: this.getAuthHeaders()}
      );

      if (response.ok) {
        return await response.json();
      } else {
        const error = await response.json();
        throw new Error(error.error);
      }
    } catch (error) {
      console.error('셀로잉 결과 조회 실패:', error);
      throw error;
    }
  }
}

// 사용 예시
async function example() {
  const api = new SeloAPI();
  
  try {
    // 1. 로그인
    const loginResult = await api.login("myusername", "mypassword");
    console.log("로그인 성공:", loginResult.user.nickname);

    // 2. 사용자 정보 조회
    const userInfo = await api.getUserInfo(1);
    console.log("사용자 정보:", userInfo);

    // 3. 셀로잉 생성
    const seloingId = await api.createSeloing("오늘의 날씨에 대해 이야기해보세요");
    console.log("셀로잉 ID:", seloingId);

    // 4. 녹음 파일 업로드 (파일 input에서 가져온다고 가정)
    const audioFile = document.getElementById('audioFile').files[0];
    if (audioFile) {
      const uploadResult = await api.uploadRecording(seloingId, audioFile, 120.5);
      console.log("업로드 결과:", uploadResult);

      // 5. 분석 완료까지 대기 (폴링)
      let isCompleted = false;
      while (!isCompleted) {
        await new Promise(resolve => setTimeout(resolve, 5000)); // 5초 대기
        
        const progress = await api.checkAnalysisProgress(seloingId);
        console.log("분석 진행률:", progress.progress_percentage + "%");
        
        if (progress.status === "completed") {
          isCompleted = true;
          
          // 6. 최종 결과 조회
          const result = await api.getSeloingResult(seloingId);
          console.log("분석 결과:", result);
        } else if (progress.status === "failed") {
          throw new Error("분석 실패");
        }
      }
    }
    
  } catch (error) {
    console.error("에러 발생:", error.message);
  }
}

// DOM이 로드된 후 실행
document.addEventListener('DOMContentLoaded', example);
```

---

## 🔧 개발 참고사항

### 환경별 설정

#### 개발 환경
- **Base URL:** `http://127.0.0.1:8000/api/v1/`
- **데이터베이스:** SQLite
- **파일 스토리지:** 로컬 파일 시스템
- **CORS:** 모든 도메인 허용

#### 운영 환경
- **Base URL:** `https://api.selo-ai.my/api/v1/`
- **데이터베이스:** PostgreSQL (옵션)
- **파일 스토리지:** AWS S3 (계획)
- **CORS:** 특정 도메인만 허용

### Rate Limiting

| API 종류 | 제한 |
|---------|-----|
| 인증 필요 API | 분당 60회 |
| 인증 불필요 API | 분당 20회 |
| 파일 업로드 | 시간당 50회 |
| 카카오 로그인 | 분당 10회 |

### CORS 설정
```javascript
// 허용된 Origin
const allowedOrigins = [
  "http://127.0.0.1:3000",
  "https://selo-ai.my",
  "https://app.selo-ai.my"
];
```

### 보안 고려사항
- 모든 API 요청은 HTTPS 사용 권장
- JWT 토큰은 7일 후 만료
- 민감한 정보는 로그에 기록되지 않음
- 파일 업로드 시 악성 파일 검사
- SQL Injection 방지
- XSS 공격 방지

### 파일 업로드 제한

| 파일 타입 | 최대 크기 | 지원 형식 |
|---------|---------|----------|
| 이미지 | 10MB | JPG, JPEG, PNG, GIF |
| 오디오 | 100MB | WAV, MP3, M4A, FLAC |
| 문서 | 50MB | PDF, DOC, DOCX, TXT |

---

**⚠️ 주의사항:**
1. 이 API는 개발 중이며 변경될 수 있습니다.
2. 운영 환경에서는 적절한 Rate Limiting이 적용됩니다.
3. 대용량 파일 업로드는 별도 상담이 필요합니다.
4. AI 분석 결과는 예시이며 실제 구현과 다를 수 있습니다.
5. 모든 시간은 UTC 기준입니다.

**문의:** 개발팀 또는 GitHub Issues  
**API 상태 확인:** `GET /api/healthz`