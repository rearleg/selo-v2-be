import jwt
import datetime
import hashlib
import secrets
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import RefreshToken, BlacklistedToken

User = get_user_model()


def generate_jwt_tokens(user):
    """사용자를 위한 Access Token과 Refresh Token 생성"""
    # Access Token (5분)
    access_payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'type': 'access',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.APP_JWT_ACCESS_EXP_MINUTES),
        'iat': datetime.datetime.utcnow(),
    }
    
    # Refresh Token (4주)
    refresh_token_value = secrets.token_urlsafe(32)
    refresh_payload = {
        'user_id': user.id,
        'token_value': refresh_token_value,
        'type': 'refresh',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(weeks=settings.APP_JWT_REFRESH_EXP_WEEKS),
        'iat': datetime.datetime.utcnow(),
    }
    
    access_token = jwt.encode(access_payload, settings.APP_JWT_SECRET, algorithm=settings.APP_JWT_ALG)
    refresh_token = jwt.encode(refresh_payload, settings.APP_JWT_SECRET, algorithm=settings.APP_JWT_ALG)
    
    # Refresh Token을 데이터베이스에 저장
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    RefreshToken.objects.create(
        user=user,
        token_hash=refresh_token_hash,
        expires_at=timezone.now() + datetime.timedelta(weeks=settings.APP_JWT_REFRESH_EXP_WEEKS)
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'access_expires_in': settings.APP_JWT_ACCESS_EXP_MINUTES * 60,  # seconds
        'refresh_expires_in': settings.APP_JWT_REFRESH_EXP_WEEKS * 7 * 24 * 60 * 60,  # seconds
    }


def generate_jwt_token(user):
    """기존 호환성을 위한 함수 - access token만 반환"""
    tokens = generate_jwt_tokens(user)
    return tokens['access_token']


def decode_jwt_token(token):
    """JWT 토큰 디코딩 및 검증"""
    try:
        payload = jwt.decode(token, settings.APP_JWT_SECRET, algorithms=[settings.APP_JWT_ALG])
        
        # 블랙리스트 체크
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if BlacklistedToken.objects.filter(token_hash=token_hash).exists():
            return None
            
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_from_token(token):
    """JWT 토큰에서 사용자 객체 가져오기"""
    payload = decode_jwt_token(token)
    if payload and payload.get('type') == 'access':
        try:
            user = User.objects.get(id=payload['user_id'])
            return user
        except User.DoesNotExist:
            return None
    return None


def refresh_access_token(refresh_token):
    """Refresh Token으로 새로운 Access Token 생성 (로테이션)"""
    try:
        # Refresh Token 디코딩
        payload = jwt.decode(refresh_token, settings.APP_JWT_SECRET, algorithms=[settings.APP_JWT_ALG])
        
        if payload.get('type') != 'refresh':
            return None
            
        # 블랙리스트 체크
        refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        if BlacklistedToken.objects.filter(token_hash=refresh_token_hash).exists():
            return None
            
        # DB에서 Refresh Token 검증
        try:
            refresh_token_obj = RefreshToken.objects.get(
                token_hash=refresh_token_hash,
                is_revoked=False,
                expires_at__gt=timezone.now()
            )
        except RefreshToken.DoesNotExist:
            return None
            
        user = User.objects.get(id=payload['user_id'])
        
        # 기존 Refresh Token 무효화 (로테이션)
        refresh_token_obj.is_revoked = True
        refresh_token_obj.save()
        
        # 기존 토큰을 블랙리스트에 추가
        BlacklistedToken.objects.create(
            token_hash=refresh_token_hash,
            expires_at=refresh_token_obj.expires_at
        )
        
        # 새로운 토큰 쌍 생성
        return generate_jwt_tokens(user)
        
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
        return None


def revoke_refresh_token(refresh_token):
    """Refresh Token 무효화"""
    try:
        payload = jwt.decode(refresh_token, settings.APP_JWT_SECRET, algorithms=[settings.APP_JWT_ALG])
        
        if payload.get('type') != 'refresh':
            return False
            
        refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        
        # DB에서 토큰 무효화
        refresh_token_obj = RefreshToken.objects.filter(
            token_hash=refresh_token_hash,
            is_revoked=False
        ).first()
        
        if refresh_token_obj:
            refresh_token_obj.is_revoked = True
            refresh_token_obj.save()
            
            # 블랙리스트에 추가
            BlacklistedToken.objects.create(
                token_hash=refresh_token_hash,
                expires_at=refresh_token_obj.expires_at
            )
            return True
            
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        pass
        
    return False


def revoke_all_user_tokens(user):
    """사용자의 모든 Refresh Token 무효화"""
    refresh_tokens = RefreshToken.objects.filter(user=user, is_revoked=False)
    
    for token_obj in refresh_tokens:
        token_obj.is_revoked = True
        token_obj.save()
        
        # 블랙리스트에 추가
        BlacklistedToken.objects.create(
            token_hash=token_obj.token_hash,
            expires_at=token_obj.expires_at
        )


def cleanup_expired_tokens():
    """만료된 토큰들 정리 (관리 명령어에서 사용)"""
    now = timezone.now()
    
    # 만료된 Refresh Token 삭제
    RefreshToken.objects.filter(expires_at__lt=now).delete()
    
    # 만료된 블랙리스트 토큰 삭제
    BlacklistedToken.objects.filter(expires_at__lt=now).delete()