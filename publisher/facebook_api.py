#!/usr/bin/env python3
"""
Facebook Reels API Publisher
Publishes the generated 4K video to a Facebook Page using the Meta Graph API.
Uses the same META_USER_ACCESS_TOKEN if it has page permissions.
"""

import os
import time
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("FacebookAPI")

def publish_to_facebook(video_path, caption):
    logger.info("Initializing Facebook Reels Publisher...")
    
    access_token = os.environ.get("META_USER_ACCESS_TOKEN")
    page_id = os.environ.get("FACEBOOK_PAGE_ID")
    
    if not access_token or not page_id:
        logger.warning("Missing FACEBOOK_PAGE_ID or META_USER_ACCESS_TOKEN. Skipping Facebook publishing.")
        return False
        
    try:
        # Step 1: Initialize the upload session for Facebook Reels
        logger.info(f"Initializing upload session for Facebook Page: {page_id}")
        init_url = f"https://graph.facebook.com/v19.0/{page_id}/video_reels"
        init_payload = {
            "upload_phase": "start",
            "access_token": access_token
        }
        init_res = requests.post(init_url, data=init_payload).json()
        
        if "video_id" not in init_res:
            logger.error(f"Failed to start FB upload: {init_res}")
            return False
            
        video_id = init_res["video_id"]
        
        # Step 2: Upload the video data
        logger.info(f"Uploading 4K video payload to Facebook (Video ID: {video_id})...")
        upload_url = f"https://rupload.facebook.com/video-upload/v19.0/{video_id}"
        headers = {
            "Authorization": f"OAuth {access_token}",
            "offset": "0",
            "file_size": str(os.path.getsize(video_path))
        }
        
        with open(video_path, "rb") as f:
            upload_res = requests.post(upload_url, headers=headers, data=f)
            
        if upload_res.status_code != 200:
            logger.error(f"Failed to upload video to FB: {upload_res.text}")
            return False
            
        # Step 3: Publish the Reel
        logger.info("Publishing Reel to Facebook feed...")
        publish_payload = {
            "upload_phase": "finish",
            "access_token": access_token,
            "video_id": video_id,
            "description": caption,
            "video_state": "PUBLISHED"
        }
        pub_res = requests.post(init_url, data=publish_payload).json()
        
        if "success" in pub_res and pub_res["success"]:
            logger.info("✅ Successfully published 4K Reel to Facebook!")
            return True
        else:
            logger.error(f"Failed to finish FB publish: {pub_res}")
            return False
            
    except Exception as e:
        logger.error(f"Facebook Publisher Error: {e}")
        return False

if __name__ == "__main__":
    publish_to_facebook("final_reel.mp4", "Test FB Caption #Reels")
