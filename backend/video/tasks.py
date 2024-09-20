# from celery import shared_task
# import subprocess
# from .models import Video, Subtitle
# import os
# from django.conf import settings
# import re

# @shared_task
# def extract_subtitles(video_id):
#     try:
#         video = Video.objects.get(id=video_id)
#         video_path = os.path.join(settings.MEDIA_ROOT, video.video_file.name)
        
#         # Subtitle file path (save it to the same location as the video)
#         subtitle_output_path = os.path.join(settings.MEDIA_ROOT, 'subtitles', f'{video.id}.srt')
        
#         # Make sure the subtitles directory exists
#         os.makedirs(os.path.dirname(subtitle_output_path), exist_ok=True)
        
#         # Use FFmpeg to extract subtitles
#         ffmpeg_command = f"ffmpeg -i {video_path} -map 0:s:0 {subtitle_output_path}"
#         subprocess.run(ffmpeg_command, shell=True, check=True)
        
#         # Parse the .srt file to extract subtitles and timestamps
#         subtitles = []
#         with open(subtitle_output_path, 'r') as subtitle_file:
#             content = subtitle_file.read()
#             subtitle_blocks = content.split('\n\n')
            
#             for block in subtitle_blocks:
#                 if block.strip() == '':
#                     continue

#                 lines = block.split('\n')
#                 if len(lines) >= 3:
#                     subtitle_index = lines[0]
#                     timestamp_line = lines[1]
#                     subtitle_text = ' '.join(lines[2:])
                    
#                     # Regex to extract timestamps (e.g., 00:00:00,000 --> 00:00:01,000)
#                     timestamp_pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')
#                     match = timestamp_pattern.match(timestamp_line)
                    
#                     if match:
#                         start_time = match.group(1)
#                         end_time = match.group(2)
                        
#                         subtitles.append({
#                             'start': start_time,
#                             'end': end_time,
#                             'text': subtitle_text
#                         })

#         # Save subtitles and timestamps in the database
#         Subtitle.objects.create(
#             video=video,
#             language='en',  # Assuming English for now
#             content=content,  # Save raw content of the subtitle
#             timestamp=subtitles  # Save parsed timestamps and text
#         )
        
#         return "Subtitles extracted and timestamps parsed successfully!"
#     except Video.DoesNotExist:
#         return "Video not found"
#     except Exception as e:
#         return f"An error occurred: {str(e)}"


from celery import shared_task
import subprocess
from .models import Video, Subtitle
import os
from django.conf import settings
import re

@shared_task
def extract_subtitles(video_id):
    try:
        video = Video.objects.get(id=video_id)
        video_path = os.path.join(settings.MEDIA_ROOT, video.video_file.name)

        # Create the subtitles directory if not exists
        subtitles_dir = os.path.join(settings.MEDIA_ROOT, 'subtitles', f'{video.id}')
        os.makedirs(subtitles_dir, exist_ok=True)

        # Extract available subtitle languages using FFmpeg
        ffmpeg_command = f"ffmpeg -i {video_path} 2>&1"
        output = subprocess.run(ffmpeg_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subtitle_streams = re.findall(r'Stream #\d+:\d+\[.*?\]: Subtitle:.*\((.*?)\)', output.stderr.decode())
        
        if not subtitle_streams:
            return "No subtitles found in the video."

        # Extract subtitles for each language
        for idx, language in enumerate(subtitle_streams):
            subtitle_output_path = os.path.join(subtitles_dir, f'{video.id}_{language}.srt')
            ffmpeg_command = f"ffmpeg -i {video_path} -map 0:s:{idx} {subtitle_output_path}"
            subprocess.run(ffmpeg_command, shell=True, check=True)

            # Parse and save subtitles for the current language
            subtitles = []
            with open(subtitle_output_path, 'r') as subtitle_file:
                content = subtitle_file.read()
                subtitle_blocks = content.split('\n\n')

                for block in subtitle_blocks:
                    if block.strip() == '':
                        continue

                    lines = block.split('\n')
                    if len(lines) >= 3:
                        timestamp_line = lines[1]
                        subtitle_text = ' '.join(lines[2:])

                        # Extract timestamps
                        timestamp_pattern = re.compile(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})')
                        match = timestamp_pattern.match(timestamp_line)

                        if match:
                            start_time = match.group(1)
                            end_time = match.group(2)

                            subtitles.append({
                                'start': start_time,
                                'end': end_time,
                                'text': subtitle_text
                            })

            # Save subtitle content and timestamps for the current language
            Subtitle.objects.create(
                video=video,
                language=language,  # Save language code (e.g., 'en', 'es')
                content=content,  # Save raw content of the subtitle
                timestamp=subtitles  # Save parsed timestamps and text
            )

        return "Subtitles extracted for all available languages."
    
    except Video.DoesNotExist:
        return "Video not found"
    except Exception as e:
        return f"An error occurred: {str(e)}"
