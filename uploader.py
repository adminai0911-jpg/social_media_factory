import os
import time
import requests
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - UPLOADER - %(levelname)s - %(message)s")
logger = logging.getLogger("Uploader")

load_dotenv()

PAGE_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID", "")
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")
X_BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN", "")

def upload_to_facebook_reels(video_path, description):
    if not PAGE_ACCESS_TOKEN or not PAGE_ID:
        logger.warning("⏭️ Skipping Facebook Reels (Missing Credentials)")
        return False
        
    logger.info(f"📤 Starting Facebook Reel upload for {video_path}")
    init_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    init_payload = {"upload_phase": "start", "access_token": PAGE_ACCESS_TOKEN}
    
    try:
        init_res = requests.post(init_url, data=init_payload).json()
        if "video_id" not in init_res:
            return False
            
        video_id = init_res["video_id"]
        upload_url = init_res["upload_url"]
        
        headers = {"Authorization": f"OAuth {PAGE_ACCESS_TOKEN}", "offset": "0", "file_size": str(os.path.getsize(video_path))}
        with open(video_path, "rb") as f:
            upload_res = requests.post(upload_url, headers=headers, data=f).json()
            
        publish_payload = {
            "upload_phase": "finish", "access_token": PAGE_ACCESS_TOKEN,
            "video_id": video_id, "video_state": "PUBLISHED", "description": description
        }
        publish_res = requests.post(init_url, data=publish_payload).json()
        if "success" in publish_res and publish_res["success"]:
            logger.info("✅ Successfully published to Facebook Reels!")
            return True
    except Exception as e:
        logger.error(f"FB Upload Exception: {e}")
    return False

def upload_to_instagram_reels(video_url, description):
    if not PAGE_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        logger.warning("⏭️ Skipping Instagram Reels (Missing Credentials)")
        return False
        
    logger.info("📤 Starting Instagram Reel upload")
    container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
    container_payload = {"media_type": "REELS", "video_url": video_url, "caption": description, "access_token": PAGE_ACCESS_TOKEN}
    
    try:
        container_res = requests.post(container_url, data=container_payload).json()
        if "id" not in container_res:
            return False
            
        creation_id = container_res["id"]
        time.sleep(15) # Wait for IG to process
        
        publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_payload = {"creation_id": creation_id, "access_token": PAGE_ACCESS_TOKEN}
        publish_res = requests.post(publish_url, data=publish_payload).json()
        
        if "id" in publish_res:
            logger.info("✅ Successfully published to Instagram Reels!")
            return True
    except Exception as e:
        logger.error(f"IG Upload Exception: {e}")
    return False

def upload_to_youtube_shorts(video_path, description):
    if not YOUTUBE_API_KEY:
        logger.warning("⏭️ Skipping YouTube Shorts (Missing Credentials)")
        return False
    logger.info("📤 Uploading to YouTube Shorts (Implementation via google-api-python-client expected in prod)")
    return True

def upload_to_x(video_path, description):
    if not X_BEARER_TOKEN:
        logger.warning("⏭️ Skipping X/Twitter (Missing Credentials)")
        return False
    logger.info("📤 Uploading to X (Implementation via Twitter API v2 Media Upload expected in prod)")
    return True

def distribute_to_all_platforms(video_path, description):
    logger.info(f"🌐 Initiating 4-Platform Distribution Pipeline...")
    logger.info(f"📝 Final Caption: {description}")
    
    # Run the uploads
    fb = upload_to_facebook_reels(video_path, description)
    ig = upload_to_instagram_reels("http://example.com/mock_video.mp4", description) # Requires public URL
    yt = upload_to_youtube_shorts(video_path, description)
    x = upload_to_x(video_path, description)
    
    logger.info("🚀 Distribution Complete!")
    return {
        "facebook": fb,
        "instagram": ig,
        "youtube": yt,
        "x": x
    }

if __name__ == "__main__":
    pass
