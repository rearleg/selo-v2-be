from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserType, UserSelloingInfo, OnboardingSession, OnboardingMessage
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


class UserOnboardingSerializer(serializers.Serializer):
    """온보딩 정보 업데이트"""
    goal = serializers.CharField(max_length=200, required=False, allow_blank=True)
    job = serializers.CharField(max_length=200, required=False, allow_blank=True)
    interest = serializers.CharField(max_length=200, required=False, allow_blank=True)
    user_type_id = serializers.IntegerField(required=False)
    
    def update(self, instance, validated_data):
        # UserSelloingInfo 업데이트
        seloing_info = instance.seloing_infos.first()
        if seloing_info:
            if 'goal' in validated_data:
                seloing_info.goal = validated_data['goal']
            if 'job' in validated_data:
                seloing_info.job = validated_data['job']
            if 'interest' in validated_data:
                seloing_info.interest = validated_data['interest']
            seloing_info.save()
        
        # User 정보 업데이트
        if 'user_type_id' in validated_data:
            try:
                user_type = UserType.objects.get(id=validated_data['user_type_id'])
                instance.user_type = user_type
            except UserType.DoesNotExist:
                pass
        
        # 온보딩 완료 처리
        instance.is_onboarding = True
        instance.save()
        
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """관리자용 유저 리스트 조회"""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'nickname', 'is_active',
            'date_joined', 'last_login'
        ]


class OnboardingMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingMessage
        fields = ['id', 'sender', 'content', 'step', 'created_at']


class OnboardingSessionSerializer(serializers.ModelSerializer):
    messages = OnboardingMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = OnboardingSession
        fields = ['id', 'current_step', 'is_active', 'messages', 'created_at', 'updated_at']


class OnboardingChatSerializer(serializers.Serializer):
    """온보딩 대화 요청"""
    message = serializers.CharField(max_length=1000)