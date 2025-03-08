import json
import os
from urllib.parse import urlparse, parse_qs, urlencode
from urllib.request import urlopen
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    raise ImportError(
        "`youtube_transcript_api` not installed. Please install using `pip install youtube_transcript_api`"
    )

app = FastAPI(
    title="YouTube Tools API",
    description="""
    A comprehensive API for extracting and analyzing YouTube video data by @iniakunhuda
    
    This API provides three main functionalities:
    * Fetching video metadata (title, author, thumbnail, etc.)
    * Extracting video captions/subtitles as plain text
    * Generating timestamps with corresponding caption text
    
    The API supports various YouTube URL formats including regular watch URLs,
    short URLs, embed URLs, and legacy URLs.
    """,
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "iniakunhuda@gmail.com",
    },
    license_info={
        "name": "MIT License",
    },
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class YouTubeRequest(BaseModel):
    url: str = Field(
        ..., 
        description="YouTube video URL. Supports various formats (watch, short, embed)",
        example="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    )
    languages: Optional[List[str]] = Field(
        None, 
        description="Language codes for the captions (e.g., ['en', 'es']). If not provided, defaults to all available languages for captions or English for timestamps.",
        example=["en"]
    )

class VideoMetadata(BaseModel):
    title: str = Field(..., description="Video title")
    author_name: str = Field(..., description="Channel name")
    author_url: str = Field(..., description="Channel URL")
    type: str = Field(..., description="Content type (usually 'video')")
    height: int = Field(..., description="Thumbnail height")
    width: int = Field(..., description="Thumbnail width")
    version: str = Field(..., description="API version")
    provider_name: str = Field(..., description="Service provider (YouTube)")
    provider_url: str = Field(..., description="Service provider URL")
    thumbnail_url: str = Field(..., description="Video thumbnail URL")

class YouTubeTools:
    @staticmethod
    def get_youtube_video_id(url: str) -> Optional[str]:
        """Function to get the video ID from a YouTube URL."""
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname

        if hostname == "youtu.be":
            return parsed_url.path[1:]
        if hostname in ("www.youtube.com", "youtube.com"):
            if parsed_url.path == "/watch":
                query_params = parse_qs(parsed_url.query)
                return query_params.get("v", [None])[0]
            if parsed_url.path.startswith("/embed/"):
                return parsed_url.path.split("/")[2]
            if parsed_url.path.startswith("/v/"):
                return parsed_url.path.split("/")[2]
        return None

    @staticmethod
    def get_video_data(url: str) -> Dict[str, Any]:
        """Function to get video data from a YouTube URL."""
        if not url:
            raise HTTPException(status_code=400, detail="No URL provided")

        try:
            video_id = YouTubeTools.get_youtube_video_id(url)
            if not video_id:
                raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        except Exception:
            raise HTTPException(status_code=400, detail="Error getting video ID from URL")

        try:
            params = {"format": "json", "url": f"https://www.youtube.com/watch?v={video_id}"}
            oembed_url = "https://www.youtube.com/oembed"
            query_string = urlencode(params)
            full_url = oembed_url + "?" + query_string

            with urlopen(full_url) as response:
                response_text = response.read()
                video_data = json.loads(response_text.decode())
                clean_data = {
                    "title": video_data.get("title"),
                    "author_name": video_data.get("author_name"),
                    "author_url": video_data.get("author_url"),
                    "type": video_data.get("type"),
                    "height": video_data.get("height"),
                    "width": video_data.get("width"),
                    "version": video_data.get("version"),
                    "provider_name": video_data.get("provider_name"),
                    "provider_url": video_data.get("provider_url"),
                    "thumbnail_url": video_data.get("thumbnail_url"),
                }
                return clean_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting video data: {str(e)}")

    @staticmethod
    def get_video_captions(url: str, languages: Optional[List[str]] = None) -> str:
        """Get captions from a YouTube video."""
        if not url:
            raise HTTPException(status_code=400, detail="No URL provided")

        try:
            video_id = YouTubeTools.get_youtube_video_id(url)
            if not video_id:
                raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        except Exception:
            raise HTTPException(status_code=400, detail="Error getting video ID from URL")

        try:
            captions = None
            if languages:
                captions = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
            else:
                captions = YouTubeTranscriptApi.get_transcript(video_id)
            
            if captions:
                return " ".join(line["text"] for line in captions)
            return "No captions found for video"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting captions for video: {str(e)}")

    @staticmethod
    def get_video_timestamps(url: str, languages: Optional[List[str]] = None) -> List[str]:
        """Generate timestamps for a YouTube video based on captions."""
        if not url:
            raise HTTPException(status_code=400, detail="No URL provided")

        try:
            video_id = YouTubeTools.get_youtube_video_id(url)
            if not video_id:
                raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        except Exception:
            raise HTTPException(status_code=400, detail="Error getting video ID from URL")

        try:
            captions = YouTubeTranscriptApi.get_transcript(video_id, languages=languages or ["en"])
            timestamps = []
            for line in captions:
                start = int(line["start"])
                minutes, seconds = divmod(start, 60)
                timestamps.append(f"{minutes}:{seconds:02d} - {line['text']}")
            return timestamps
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating timestamps: {str(e)}")

@app.post(
    "/video-data", 
    response_model=VideoMetadata,
    summary="Get YouTube video metadata",
    description="Retrieves basic metadata about a YouTube video including title, author, and thumbnail URL.",
    response_description="Video metadata including title, author, and thumbnail URL",
    tags=["Video Data"]
)
async def get_video_data(request: YouTubeRequest):
    """
    Retrieve metadata about a YouTube video.
    
    This endpoint extracts the following information from a YouTube video:
    - Video title
    - Channel name and URL
    - Thumbnail URL and dimensions
    - Provider information
    
    Parameters:
    - **url**: Full YouTube URL (required)
    - **languages**: Optional list of language codes (not used for this endpoint)
    """
    return YouTubeTools.get_video_data(request.url)

@app.post(
    "/video-captions", 
    response_model=str,
    summary="Get YouTube video captions/subtitles",
    description="Extracts captions/subtitles from a YouTube video and returns them as plain text.",
    response_description="Video captions as plain text",
    tags=["Captions"]
)
async def get_video_captions(request: YouTubeRequest):
    """
    Retrieve captions/subtitles from a YouTube video.
    
    This endpoint extracts all captions from a YouTube video and combines them into a single text string.
    
    Parameters:
    - **url**: Full YouTube URL (required)
    - **languages**: Optional list of language codes (e.g., ['en', 'es']) to specify which language captions to retrieve. 
                    If not provided, defaults to all available languages.
    """
    return YouTubeTools.get_video_captions(request.url, request.languages)

@app.post(
    "/video-timestamps", 
    response_model=List[str],
    summary="Get timestamped captions",
    description="Generates a list of timestamps with corresponding caption text for a YouTube video.",
    response_description="List of timestamped captions",
    tags=["Timestamps"]
)
async def get_video_timestamps(request: YouTubeRequest):
    """
    Generate timestamps with corresponding caption text.
    
    This endpoint creates a list of timestamps in the format "MM:SS - Caption text" for each caption in the video.
    
    Parameters:
    - **url**: Full YouTube URL (required)
    - **languages**: Optional list of language codes (e.g., ['en']). If not provided, defaults to English.
    """
    return YouTubeTools.get_video_timestamps(request.url, request.languages)

@app.get("/", include_in_schema=False)
async def root():
    """Redirect to docs"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    # Use environment variable for port, default to 8000 if not set
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)