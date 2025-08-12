from rest_framework import serializers
from .models import Seloing, SeloingAnalysis, SeloingResult, SeloingAudio, SeloingReward


class SeloingAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeloingAudio
        fields = ['id', 'filename', 'file_url', 'duration_seconds', 'created_at']


class SeloingAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeloingAnalysis
        fields = [
            'id', 'original_transcript', 'analyzed_transcript',
            'disfluency_feedback', 'topic_feedback', 'stability_feedback',
            'created_at'
        ]


class SeloingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeloingResult
        fields = [
            'id', 'total_score', 'repeat_score', 'topic_score',
            'filler_score', 'stability_score', 'repeat_count',
            'filler_count', 'created_at'
        ]


class SeloingRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeloingReward
        fields = ['id', 'earned_exp', 'earned_candy', 'created_at']


class SeloingSerializer(serializers.ModelSerializer):
    audio = SeloingAudioSerializer(source='seloingaudio', read_only=True)
    analysis = SeloingAnalysisSerializer(source='seloinganalysis', read_only=True)
    result = SeloingResultSerializer(source='seloingresult', read_only=True)
    reward = SeloingRewardSerializer(source='seloingreward', read_only=True)
    
    class Meta:
        model = Seloing
        fields = [
            'id', 'selected_topic', 'is_completed', 'created_at', 'updated_at',
            'audio', 'analysis', 'result', 'reward'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class SeloingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seloing
        fields = ['selected_topic']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class SeloingListSerializer(serializers.ModelSerializer):
    """완료된 셀로잉 이력 조회용"""
    result = SeloingResultSerializer(source='seloingresult', read_only=True)
    
    class Meta:
        model = Seloing
        fields = [
            'id', 'selected_topic', 'is_completed', 'created_at', 'result'
        ]


class TopicCreateSerializer(serializers.Serializer):
    """관심사 주제 생성 - 단순 텍스트 반환"""
    user_interests = serializers.ListField(
        child=serializers.CharField(max_length=100),
        help_text="사용자 관심사 리스트"
    )
    
    def create(self, validated_data):
        # AI나 로직을 통해 주제 생성 후 반환
        # 현재는 예시 구현
        interests = validated_data['user_interests']
        topics = [f"{interest}에 대한 스피치 연습" for interest in interests]
        return {'generated_topics': topics}


class RecordingUploadSerializer(serializers.Serializer):
    """녹음 파일 업로드"""
    audio_file = serializers.FileField()
    duration_seconds = serializers.FloatField()
    
    def validate_audio_file(self, value):
        # 파일 형식 및 크기 검증
        if not value.name.lower().endswith(('.mp3', '.wav', '.m4a')):
            raise serializers.ValidationError('지원되지 않는 오디오 형식입니다.')
        
        # 파일 크기 제한 (예: 50MB)
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError('파일 크기가 너무 큽니다. (최대 50MB)')
        
        return value


class AnalysisProgressSerializer(serializers.Serializer):
    """분석 진행 상태"""
    status = serializers.ChoiceField(choices=[
        ('pending', '대기중'),
        ('processing', '분석중'),
        ('completed', '완료'),
        ('failed', '실패')
    ])
    progress_percentage = serializers.IntegerField(min_value=0, max_value=100)
    message = serializers.CharField(max_length=200)


class AICallbackSerializer(serializers.Serializer):
    """AI 분석 결과 콜백"""
    original_transcript = serializers.CharField()
    analyzed_transcript = serializers.CharField()
    disfluency_feedback = serializers.CharField()
    topic_feedback = serializers.CharField()
    stability_feedback = serializers.CharField()
    
    total_score = serializers.IntegerField(min_value=0, max_value=100)
    repeat_score = serializers.IntegerField(min_value=0, max_value=100)
    topic_score = serializers.IntegerField(min_value=0, max_value=100)
    filler_score = serializers.IntegerField(min_value=0, max_value=100)
    stability_score = serializers.IntegerField(min_value=0, max_value=100)
    
    repeat_count = serializers.IntegerField(min_value=0)
    filler_count = serializers.IntegerField(min_value=0)


class StatSaveSerializer(serializers.Serializer):
    """스탯 저장용"""
    earned_exp = serializers.IntegerField(min_value=0)
    earned_candy = serializers.IntegerField(min_value=0)