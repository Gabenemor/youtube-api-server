# ✅ FULLY UPDATED YOUTUBE TOOLS WITH MONKEY PATCHING

import json
from urllib.parse import urlparse, parse_qs, urlencode
from urllib.request import urlopen
from typing import Optional, List

from fastapi import HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import types

# ✅ Proxy setup
def get_proxy():
    return {
        "http": "http://keyvidai-rotate:MLf8p3R6DEHu7@p.webshare.io:80/",
        "https": "http://keyvidai-rotate:MLf8p3R6DEHu7@p.webshare.io:80/"
    }

# ✅ Monkey patching the internal transcript fetch to use proxy
def patched_get_raw_transcript(self, video_id, proxies=None, cookies=None, params=None):
    url = f"https://www.youtube.com/api/timedtext?{params}"
    response = requests.get(
        url,
        proxies=get_proxy(),
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        },
        timeout=10
    )

    if response.status_code != 200:
        raise Exception(f"Failed to fetch transcript. Status code: {response.status_code}, body: {response.text}")

    return response.text

# ✅ Apply the patch
YouTubeTranscriptApi._get_raw_transcript = types.MethodType(patched_get_raw_transcript, YouTubeTranscriptApi)

# ✅ Create a basic ytt_api instance (no need for WebshareProxyConfig)
ytt_api = YouTubeTranscriptApi()

# ✅ YouTubeTools class
class YouTubeTools:
    @staticmethod
    def get_youtube_video_id(url: str) -> Optional[str]:
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
    def get_video_data(url: str) -> dict:
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
        if not url:
            raise HTTPException(status_code=400, detail="No URL provided")

        try:
            video_id = YouTubeTools.get_youtube_video_id(url)
            if not video_id:
                raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        except Exception:
            raise HTTPException(status_code=400, detail="Error getting video ID from URL")

        try:
            if languages:
                captions = ytt_api.fetch(video_id, languages=languages)
            else:
                captions = ytt_api.fetch(video_id)

            if captions:
                return " ".join(snippet.text for snippet in captions)
            return "No captions found for video"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting captions for video: {str(e)}")

    @staticmethod
    def get_video_timestamps(url: str, languages: Optional[List[str]] = None) -> List[str]:
        if not url:
            raise HTTPException(status_code=400, detail="No URL provided")

        try:
            video_id = YouTubeTools.get_youtube_video_id(url)
            if not video_id:
                raise HTTPException(status_code=400, detail="Invalid YouTube URL")
        except Exception:
            raise HTTPException(status_code=400, detail="Error getting video ID from URL")

        try:
            captions = ytt_api.fetch(video_id, languages=languages or ["en"])
            timestamps = []
            for snippet in captions:
                start = int(snippet.start)
                minutes, seconds = divmod(start, 60)
                timestamps.append(f"{minutes}:{seconds:02d} - {snippet.text}")
            return timestamps
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating timestamps: {str(e)}")
