import jwt
import datetime
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_jwt_token(user):
    """사용자를 위한 JWT 토큰 생성"""
    payload = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=settings.APP_JWT_EXP_MINUTES),
        'iat': datetime.datetime.utcnow(),
    }
    
    token = jwt.encode(payload, settings.APP_JWT_SECRET, algorithm=settings.APP_JWT_ALG)
    return token


def decode_jwt_token(token):
    """JWT 토큰 디코딩 및 검증"""
    try:
        payload = jwt.decode(token, settings.APP_JWT_SECRET, algorithms=[settings.APP_JWT_ALG])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_from_token(token):
    """JWT 토큰에서 사용자 객체 가져오기"""
    payload = decode_jwt_token(token)
    if payload:
        try:
            user = User.objects.get(id=payload['user_id'])
            return user
        except User.DoesNotExist:
            return None
    return None