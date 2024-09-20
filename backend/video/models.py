from django.db import models

# Create your models here.
class Video(models.Model):
	title = models.CharField(max_length=255)
	video_file = models.FileField(upload_to='videos/')
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title

class Subtitle(models.Model):
	video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='subtitles')
	language = models.CharField(max_length=50)
	content = models.TextField() #stores Raw subtitles data
	timestamp = models.JSONField(null=True, blank=True)  # Allow null timestamps

	def __str__(self):
		return f"{self.language} - {self.video.title}"