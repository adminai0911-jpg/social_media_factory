#!/usr/bin/env python3
"""
YouTube Shorts API Publisher
Publishes the generated 4K video to YouTube Shorts.
Requires YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, and YOUTUBE_REFRESH_TOKEN in the environment.
"""

import os
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("YouTubeAPI")

def get_youtube_access_token():
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, refresh_token]):
        return None
        
    logger.info("Refreshing YouTube Access Token...")
    url = "https://oauth2.googleapis.com/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    
    res = requests.post(url, data=payload).json()
    return res.get("access_token")

def publish_to_youtube(video_path, title, description, tags):
    logger.info("Initializing YouTube Shorts Publisher...")
    
    access_token = get_youtube_access_token()
    if not access_token:
        logger.warning("Missing YouTube API Tokens. Skipping YouTube Shorts publishing.")
        return False
        
    try:
        # Prepare metadata
        metadata = {
            "snippet": {
                "title": title[:100],  # YT Title limit is 100 chars
                "description": description + "\n#shorts",
                "tags": tags,
                "categoryId": "22" # People & Blogs
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        logger.info("Uploading 4K video to YouTube Shorts...")
        # Since this is a simple stateless script, we use a single POST request for smaller videos.
        # For a robust 4K upload, a resumable upload protocol should be used in production.
        files = {
            'metadata': (None, str(metadata), 'application/json'),
            'file': (video_path, open(video_path, 'rb'), 'video/mp4')
        }
        
        upload_url = "https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status"
        res = requests.post(upload_url, headers=headers, files=files)
        
        if res.status_code in [200, 201]:
            logger.info("✅ Successfully published 4K video to YouTube Shorts!")
            return True
        else:
            logger.error(f"Failed to publish to YouTube: {res.text}")
            return False
            
    except Exception as e:
        logger.error(f"YouTube Publisher Error: {e}")
        return False

if __name__ == "__main__":
    publish_to_youtube("final_reel.mp4", "Epic AI Video", "Check out this video!", ["ai", "tech"])
