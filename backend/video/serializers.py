from rest_framework import serializers
from .models import Video, Subtitle

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['id', 'title', 'video_file', 'uploaded_at']

class SubtileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtitle
        fields = ['id', 'video', 'language', 'content', 'timestamp']