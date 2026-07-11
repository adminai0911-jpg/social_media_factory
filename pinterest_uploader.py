import os
import requests
import json
import logging
import time

logger = logging.getLogger("PinterestUploader")

def upload_to_pinterest(video_path, caption):
    """
    Uploads a video to Pinterest using the v5 API.
    Requires PINTEREST_ACCESS_TOKEN and PINTEREST_BOARD_ID.
    """
    access_token = os.environ.get("PINTEREST_ACCESS_TOKEN")
    board_id = os.environ.get("PINTEREST_BOARD_ID")
    
    if not access_token or not board_id:
        logger.error("Missing PINTEREST_ACCESS_TOKEN or PINTEREST_BOARD_ID")
        return False
        
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 1. Register Media
    logger.info("Initializing Pinterest media registration...")
    media_url = "https://api.pinterest.com/v5/media"
    media_payload = {
        "media_type": "video"
    }
    
    res = requests.post(media_url, headers=headers, json=media_payload, timeout=20)
    if res.status_code != 201:
        logger.error(f"Failed to register media with Pinterest: {res.text}")
        return False
        
    data = res.json()
    media_id = data["media_id"]
    upload_url = data["upload_url"]
    upload_parameters = data["upload_parameters"]
    
    # 2. Upload File (Multipart Form)
    logger.info(f"Uploading video to Pinterest S3 bucket (media_id: {media_id})...")
    
    files = {'file': open(video_path, 'rb')}
    upload_res = requests.post(upload_url, data=upload_parameters, files=files, timeout=300)
    
    if upload_res.status_code not in [200, 204]:
        logger.error(f"Failed to upload video to Pinterest S3: {upload_res.status_code} {upload_res.text}")
        return False
        
    # 3. Wait for processing
    logger.info("Waiting for Pinterest to process video (can take up to 30s)...")
    status_url = f"https://api.pinterest.com/v5/media/{media_id}"
    processed = False
    
    for _ in range(10):
        time.sleep(5)
        status_res = requests.get(status_url, headers=headers, timeout=10).json()
        status = status_res.get("status")
        if status == "succeeded":
            processed = True
            break
        elif status == "failed":
            logger.error("Pinterest video processing failed.")
            return False
            
    if not processed:
        logger.error("Pinterest video processing timed out.")
        return False
        
    # 4. Create Pin
    logger.info("Video processed. Creating Pin...")
    pin_url = "https://api.pinterest.com/v5/pins"
    
    # Extract title from caption (first sentence)
    title = caption.split('.')[0] if '.' in caption else caption[:100]
    if len(title) > 100: title = title[:97] + "..."
    
    pin_payload = {
        "board_id": board_id,
        "media_source": {
            "source_type": "video_id",
            "cover_image_url": "",
            "media_id": media_id
        },
        "title": title,
        "description": caption
    }
    
    pin_res = requests.post(pin_url, headers=headers, json=pin_payload, timeout=20)
    if pin_res.status_code == 201:
        pin_id = pin_res.json().get("id")
        logger.info(f"✅ Successfully posted to Pinterest! Pin ID: {pin_id}")
        return True
    else:
        logger.error(f"❌ Failed to create Pinterest Pin: {pin_res.status_code} {pin_res.text}")
        return False
