# Fatmug Django Assignment

## Description
This is a Django-based web application that allows users to upload videos, process them using FFmpeg for subtitle extraction, and display subtitles as closed captions. Users can search for phrases within the subtitles, and clicking on the result will jump to the respective timestamp.

## Features
- Upload videos and extract subtitles using FFmpeg.
- Supports multiple subtitle languages.
- Search for phrases within subtitles and jump to the corresponding timestamp.
- List view of all uploaded videos.

## Tech Stack
- **Backend**: Django
- **Database**: PostgreSQL
- **Subtitle Extraction**: FFmpeg
- **Task Queue**: Celery + Redis
- **Containerization**: Docker

## Installation and Setup

To run this project locally, ensure Docker is installed. Then run the following command:

```bash
docker-compose up --build
