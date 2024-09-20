# from django.shortcuts import render

# # Create your views here.
# from rest_framework import viewsets
# from .models import Video
# from .serializers import VideoSerializer, SubtileSerializer
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from .tasks import extract_subtitles

# class VideoViewSet(viewsets.ModelViewSet):
# 	queryset = Video.objects.all()
# 	serializer_class = VideoSerializer

# 	def perform_create(self, serializer):
# 		#Save the video object
# 		video = serializer.save()

# 		#Trigger the backgroud tasks 
# 		extract_subtitles.delay(video.id)

# 	@action(detail=True, methods=['get'])
# 	def subtitles(self, request, pk=None):
# 		video = self.get_object()
# 		subtitles = video.subtitles.all()
# 		subtitle_serializer = SubtileSerializer(subtitles, many=True)
# 		return Response(subtitle_serializer.data)

# 	@action(detail=True, methods=['get'])
# 	def search_subtitles(self, request, pk=None):
# 		video = self.get_object()
# 		search_query = request.query_params.get('q', None)

# 		if search_query is None:
# 			return Response({"error": "No search query provided"}, status=400)
		
# 		try:
# 			#fetch the subtitles for the video
# 			subtitles = video.subtitles.first()
# 			if not subtitles:
# 				return Response({"error": "no subtitles found"}, status=404)
			
# 			#search through the timestamp entries
# 			matching_entries = []
# 			for entry in subtitles.timestamp:
# 				if search_query.lower() in entry['text'].lower():
# 					matching_entries.append({
# 						'start': entry['start'],
# 						'end': entry['end'],
# 						'text': entry['text']
# 					})
			
# 			if matching_entries:
# 				return Response(matching_entries)
# 			else:
# 				return Response({"error": "No matching subtitles found"}, status=404)

# 		except Exception as e:
# 			return Response({"error": str(e)}, status=500)



from rest_framework import viewsets
from .models import Video
from .serializers import VideoSerializer, SubtileSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from .tasks import extract_subtitles

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def perform_create(self, serializer):
        # Save the video object
        video = serializer.save()

        # Trigger the background task
        extract_subtitles.delay(video.id)

    @action(detail=True, methods=['get'])
    def subtitles(self, request, pk=None):
        video = self.get_object()
        language = request.query_params.get('lang', 'en')  # Default to English if no language is provided
        
        subtitles = video.subtitles.filter(language=language)  # Fetch all subtitles of the requested language
        if not subtitles.exists():
            return Response({"error": "No subtitles found for this language"}, status=404)
        
        subtitle_serializer = SubtileSerializer(subtitles, many=True)
        return Response(subtitle_serializer.data)

    @action(detail=True, methods=['get'])
    def available_languages(self, request, pk=None):
        video = self.get_object()
        subtitles = video.subtitles.all()
        languages = subtitles.values_list('language', flat=True).distinct()
        return Response(languages)
    
    @action(detail=True, methods=['get'])
    def search_subtitles(self, request, pk=None):
        video = self.get_object()
        search_query = request.query_params.get('q', None)
        language = request.query_params.get('language', 'en')  # Allow specifying language

        if search_query is None:
            return Response({"error": "No search query provided"}, status=400)

        try:
            # Fetch subtitles for the specific language
            subtitles = video.subtitles.filter(language=language).first()
            if not subtitles:
                return Response({"error": "No subtitles found for the selected language"}, status=404)

            # Search through the timestamp entries
            matching_entries = []
            for entry in subtitles.timestamp:
                if search_query.lower() in entry['text'].lower():
                    matching_entries.append({
                        'start': entry['start'],
                        'end': entry['end'],
                        'text': entry['text']
                    })

            if matching_entries:
                return Response(matching_entries)
            else:
                return Response({"error": "No matching subtitles found"}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
