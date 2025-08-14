from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserType, UserSelloingInfo
from stats.models import UserStats


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = ['id', 'seloing_type', 'description', 'created_at', 'updated_at']


class UserSelloingInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSelloingInfo
        fields = ['id', 'goal', 'job', 'interest', 'created_at', 'updated_at']


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'nickname', 'profile_image', 'user_type',
            'isConsentPersonalInfo', 'isConsentMarketing'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")
        return attrs
    
    def validate_password(self, value):
        validate_password(value)
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        # UserStats 생성
        UserStats.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('로그인 정보가 올바르지 않습니다.')
            if not user.is_active:
                raise serializers.ValidationError('비활성화된 계정입니다.')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('아이디와 비밀번호를 입력해주세요.')


class UserSerializer(serializers.ModelSerializer):
    user_type = UserTypeSerializer(read_only=True)
    seloing_info = UserSelloingInfoSerializer(source='seloing_infos', many=True, read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'nickname', 'profile_image',
            'is_onboarding', 'user_type', 'seloing_info',
            'isConsentPersonalInfo', 'isConsentMarketing',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'username', 'date_joined', 'last_login']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'nickname', 'profile_image', 'user_type',
            'is_onboarding', 'isConsentPersonalInfo', 'isConsentMarketing'
        ]


class UserListSerializer(serializers.ModelSerializer):
    """관리자용 유저 리스트 조회"""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'nickname', 'is_active',
            'date_joined', 'last_login'
        ]