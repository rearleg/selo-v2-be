from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth import get_user_model
from .jwt_utils import decode_jwt_token

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    """
    JWT 토큰 기반 인증
    Header: Authorization: Bearer <jwt_token>
    """
    
    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        
        if not auth_header or auth_header[0].lower() != b'bearer':
            return None
            
        if len(auth_header) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth_header) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)
            
        try:
            token = auth_header[1].decode('utf-8')
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)
            
        return self.authenticate_credentials(token)
    
    def authenticate_credentials(self, token):
        payload = decode_jwt_token(token)
        if not payload:
            raise exceptions.AuthenticationFailed('Invalid token.')
            
        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')
            
        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')
            
        return (user, token)