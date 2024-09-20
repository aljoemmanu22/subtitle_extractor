from django.contrib import admin

# Register your models here.
from .models import Video, Subtitle

admin.site.register(Video)
admin.site.register(Subtitle)