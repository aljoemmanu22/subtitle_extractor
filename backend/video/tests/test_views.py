# backend/video/tests/test_views.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from video.models import Video, Subtitle
import json

class VideoAPITest(APITestCase):
    def setUp(self):
        self.upload_url = reverse('video-list')  # Assuming router basename is 'video'
        self.sample_video = SimpleUploadedFile(
            "test_video.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        self.video_data = {
            'title': 'Sample Video',
            'video_file': self.sample_video
        }

    def test_upload_video(self):
        response = self.client.post(self.upload_url, self.video_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Video.objects.count(), 1)
        self.assertEqual(Video.objects.get().title, 'Sample Video')

    def test_get_video_list(self):
        Video.objects.create(title="Video 1", video_file=self.sample_video)
        Video.objects.create(title="Video 2", video_file=self.sample_video)
        response = self.client.get(self.upload_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_subtitles_no_query(self):
        video = Video.objects.create(title="Video with Subtitles", video_file=self.sample_video)
        search_url = reverse('video-search-subtitles', kwargs={'pk': video.id})
        response = self.client.get(search_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_subtitles_not_found(self):
        video = Video.objects.create(title="Video without Subtitles", video_file=self.sample_video)
        search_url = reverse('video-search-subtitles', kwargs={'pk': video.id})
        response = self.client.get(search_url, {'q': 'Hello'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_search_subtitles_success(self):
        video = Video.objects.create(title="Video with Subtitles", video_file=self.sample_video)
        Subtitle.objects.create(
            video=video,
            language="en",
            content="",
            timestamp=[
                {"start": "00:00:01,000", "end": "00:00:03,000", "text": "Hello World"},
                {"start": "00:00:04,000", "end": "00:00:06,000", "text": "Another Subtitle"}
            ]
        )
        search_url = reverse('video-search-subtitles', kwargs={'pk': video.id})
        response = self.client.get(search_url, {'q': 'hello'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['text'], "Hello World")
