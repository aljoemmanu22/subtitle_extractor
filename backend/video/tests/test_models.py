# backend/video/tests/test_models.py

from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from video.models import Video, Subtitle

class VideoModelTest(TestCase):
    def setUp(self):
        # Create a sample video file
        self.video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"file_content",
            content_type="video/mp4"
        )
        self.video = Video.objects.create(
            title="Test Video",
            video_file=self.video_file
        )

    def test_video_creation(self):
        print(self.video.video_file.name)
        self.assertEqual(self.video.title, "Test Video")
        self.assertTrue(self.video.video_file.name.startswith("videos/test_video"))
        self.assertTrue(self.video.video_file.name.endswith(".mp4"))
        self.assertIsNotNone(self.video.uploaded_at)

class SubtitleModelTest(TestCase):
    def setUp(self):
        self.video = Video.objects.create(
            title="Test Video",
            video_file=SimpleUploadedFile(
                "test_video.mp4",
                b"file_content",
                content_type="video/mp4"
            )
        )
        self.subtitle = Subtitle.objects.create(
            video=self.video,
            language="en",
            content="Subtitle content",
            timestamp=[
                {"start": "00:00:01,000", "end": "00:00:03,000", "text": "Hello World"}
            ]
        )

    def test_subtitle_creation(self):
        self.assertEqual(self.subtitle.video, self.video)
        self.assertEqual(self.subtitle.language, "en")
        self.assertEqual(self.subtitle.content, "Subtitle content")
        self.assertIsInstance(self.subtitle.timestamp, list)
        self.assertEqual(len(self.subtitle.timestamp), 1)
        self.assertEqual(self.subtitle.timestamp[0]['text'], "Hello World")
