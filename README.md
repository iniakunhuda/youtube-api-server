# YouTube Tools API Server

A FastAPI-based server that provides convenient endpoints for extracting information from YouTube videos, including video metadata, captions, and timestamped transcripts.

## Features

- **Video Metadata**: Retrieve title, author, thumbnails, and other video information
- **Captions/Transcripts**: Extract complete video captions in plain text format
- **Timestamped Transcripts**: Generate timestamps with corresponding caption text
- **Multi-language Support**: Extract captions in different languages
- **Interactive Documentation**: Built-in Swagger UI for easy API testing
- **Robust Error Handling**: Comprehensive error messages for troubleshooting

## Prerequisites

- Python 3.7+
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/iniakunhuda/youtube-api-server.git
cd youtube-api-server
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the server using:

```bash
python main.py
```

By default, the server runs on:
- Host: 0.0.0.0
- Port: 8000

You can customize these using environment variables:
```bash
export PORT=8080
export HOST=127.0.0.1
python main.py
```

Once running, the API documentation is available at:
```
http://localhost:8000/docs
```

## API Endpoints

### 1. Get Video Metadata
Retrieves detailed information about a YouTube video.

```http
POST /video-data
```

**Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Response Example:**
```json
{
    "title": "Video Title",
    "author_name": "Channel Name",
    "author_url": "https://www.youtube.com/channel/...",
    "type": "video",
    "height": 113,
    "width": 200,
    "version": "1.0",
    "provider_name": "YouTube",
    "provider_url": "https://www.youtube.com/",
    "thumbnail_url": "https://i.ytimg.com/vi/..."
}
```

### 2. Get Video Captions
Extracts and concatenates all captions from a YouTube video.

```http
POST /video-captions
```

**Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "languages": ["en", "es"]  // Optional
}
```

**Response Example:**
```
"This is the caption text for the video. It contains all the spoken content in plain text format."
```

### 3. Get Video Timestamps
Generates a list of timestamps with corresponding caption text.

```http
POST /video-timestamps
```

**Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "languages": ["en"]  // Optional, defaults to English
}
```

**Response Example:**
```json
[
    "0:00 - Welcome to this video",
    "0:15 - Today we'll be discussing...",
    "1:30 - Our first topic is...",
    "2:45 - Moving on to the second point..."
]
```

## Supported URL Formats

The API supports various YouTube URL formats:
- Standard watch URLs: `https://www.youtube.com/watch?v=VIDEO_ID`
- Short URLs: `https://youtu.be/VIDEO_ID`
- Embed URLs: `https://www.youtube.com/embed/VIDEO_ID`
- Legacy URLs: `https://www.youtube.com/v/VIDEO_ID`

## Example Usage

### Using curl:

```bash
# Get video metadata
curl -X POST "http://localhost:8000/video-data" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'

# Get video captions
curl -X POST "http://localhost:8000/video-captions" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "languages": ["en"]}'
```

### Using Python requests:

```python
import requests
import json

api_url = "http://localhost:8000/video-data"
data = {
    "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}

response = requests.post(api_url, json=data)
print(json.dumps(response.json(), indent=4))
```

## Error Handling

The API includes comprehensive error handling with specific HTTP status codes:

- `400 Bad Request`: Invalid YouTube URL or missing required parameters
- `500 Internal Server Error`: Server-side issues (network errors, unavailable captions)

Error responses include detailed messages to help with troubleshooting:

```json
{
    "detail": "Error getting video ID from URL"
}
```

## Deployment

### Docker

A Dockerfile is included for easy containerization:

```bash
# Build the Docker image
docker build -t youtube-tools-api .

# Run the container
docker run -p 8000:8000 youtube-tools-api
```

### Cloud Deployment

The API can be deployed to various cloud platforms:

- **Heroku**: Use the included Procfile
- **AWS/GCP/Azure**: Deploy as a container or serverless function

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) for caption extraction
- All contributors who help improve this project