import os
import time
import requests
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - UPLOADER - %(levelname)s - %(message)s")
logger = logging.getLogger("Uploader")

load_dotenv()

# The critical Page Token fix from Team A's failure
PAGE_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID", "")
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")

def upload_to_facebook_reels(video_path, description):
    if not PAGE_ACCESS_TOKEN or not PAGE_ID:
        logger.error("❌ Missing FACEBOOK_PAGE_ACCESS_TOKEN or FACEBOOK_PAGE_ID. Cannot upload.")
        return False
        
    logger.info(f"📤 Starting Facebook Reel upload for {video_path}")
    
    # Phase 1: Initialize upload session
    init_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    init_payload = {
        "upload_phase": "start",
        "access_token": PAGE_ACCESS_TOKEN
    }
    
    try:
        init_res = requests.post(init_url, data=init_payload).json()
        if "video_id" not in init_res:
            logger.error(f"Failed to initialize FB upload: {init_res}")
            return False
            
        video_id = init_res["video_id"]
        upload_url = init_res["upload_url"]
        
        # Phase 2: Upload file
        headers = {"Authorization": f"OAuth {PAGE_ACCESS_TOKEN}", "offset": "0", "file_size": str(os.path.getsize(video_path))}
        with open(video_path, "rb") as f:
            upload_res = requests.post(upload_url, headers=headers, data=f).json()
            
        # Phase 3: Publish
        publish_payload = {
            "upload_phase": "finish",
            "access_token": PAGE_ACCESS_TOKEN,
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": description
        }
        publish_res = requests.post(init_url, data=publish_payload).json()
        if "success" in publish_res and publish_res["success"]:
            logger.info("✅ Successfully published to Facebook Reels!")
            return True
        else:
            logger.error(f"Failed to publish FB Reel: {publish_res}")
            return False
            
    except Exception as e:
        logger.error(f"Exception during FB Upload: {e}")
        return False

def upload_to_instagram_reels(video_url, description):
    if not PAGE_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        logger.error("❌ Missing PAGE_ACCESS_TOKEN or INSTAGRAM_ACCOUNT_ID. Cannot upload to IG.")
        return False
        
    logger.info("📤 Starting Instagram Reel upload")
    
    # Phase 1: Create Media Container
    container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
    container_payload = {
        "media_type": "REELS",
        "video_url": video_url, # IG requires a public URL, so we assume GitHub Pages or an S3 bucket URL here
        "caption": description,
        "access_token": PAGE_ACCESS_TOKEN
    }
    
    try:
        container_res = requests.post(container_url, data=container_payload).json()
        if "id" not in container_res:
            logger.error(f"Failed to create IG Media Container: {container_res}")
            return False
            
        creation_id = container_res["id"]
        
        # Wait for IG to process the video
        logger.info("Waiting for IG processing...")
        time.sleep(30)
        
        # Phase 2: Publish
        publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": PAGE_ACCESS_TOKEN
        }
        publish_res = requests.post(publish_url, data=publish_payload).json()
        
        if "id" in publish_res:
            logger.info("✅ Successfully published to Instagram Reels!")
            return True
        else:
            logger.error(f"Failed to publish IG Reel: {publish_res}")
            return False
            
    except Exception as e:
        logger.error(f"Exception during IG Upload: {e}")
        return False

if __name__ == "__main__":
    # Test block
    pass
