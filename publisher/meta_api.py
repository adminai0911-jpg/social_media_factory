#!/usr/bin/env python3
"""
Meta Instagram Publisher (Cloudinary Edition)
Handles uploading of compiled 'final_reel.mp4' to Cloudinary (free video hosting).
Secures a temporary public URL for Meta servers to digest.
Orchestrates official Meta Content Publishing API:
1. Container Creation (POST .../media)
2. Asynchronous Status Polling (GET .../container_id)
3. Publishing Event (POST .../media_publish)
"""

import os
import json
import time
import logging
import requests
import cloudinary
import cloudinary.uploader
import cloudinary.api

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MetaPublisher")

SCRIPT_INPUT = "script_output.json"
FINAL_REEL = "final_reel.mp4"

def upload_to_cloudinary(source_file_name):
    """
    Uploads a file to Cloudinary and returns its secure URL and public_id.
    """
    logger.info(f"Uploading '{source_file_name}' to Cloudinary...")
    
    try:
        # Configured automatically via CLOUDINARY_URL env var
        cloudinary.config(secure=True)
        
        upload_result = cloudinary.uploader.upload(
            source_file_name,
            resource_type="video",
            folder="social_media_factory"
        )
        
        secure_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")
        
        logger.info(f"Cloudinary Upload completed successfully. Public ID: {public_id}")
        return secure_url, public_id
            
    except Exception as e:
        logger.error(f"Cloudinary upload error: {e}")
        # Local development dry-run mockup URL bypass
        mock_url = os.environ.get("MOCK_PUBLIC_VIDEO_URL")
        if mock_url:
            logger.warning(f"Local Dry Run Bypass: Using MOCK_PUBLIC_VIDEO_URL = '{mock_url}'")
            return mock_url, None
        raise e

def delete_from_cloudinary(public_id):
    """
    Deletes temporary media file from Cloudinary to clean up resources.
    """
    if not public_id:
        return
        
    try:
        cloudinary.uploader.destroy(public_id, resource_type="video")
        logger.info(f"Cleaned up temporary file '{public_id}' from Cloudinary.")
    except Exception as e:
        logger.warning(f"Failed to delete '{public_id}' from Cloudinary: {e}")

def retry_request(method, url, max_retries=4, backoff_factor=1.5, **kwargs):
    for attempt in range(max_retries):
        try:
            if method.lower() == 'post':
                response = requests.post(url, **kwargs)
            else:
                response = requests.get(url, **kwargs)
            
            # Raise for 500s or 429s to trigger retry
            if response.status_code >= 500 or response.status_code == 429:
                response.raise_for_status()
                
            return response
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                logger.error(f"Meta Network request failed after {max_retries} attempts: {e}")
                raise e
            wait_time = backoff_factor ** attempt * 10
            logger.warning(f"Meta API unstable (Status {getattr(e.response, 'status_code', 'Network Error')}). Retrying in {wait_time:.1f}s... (Attempt {attempt+1}/{max_retries})")
            time.sleep(wait_time)

def publish_to_instagram(video_url, caption, hashtags):
    """
    Orchestrates the Meta Graph API Reels publishing sequence.
    """
    ig_account_id = os.environ.get("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    access_token = os.environ.get("META_USER_ACCESS_TOKEN")
    
    if not ig_account_id or not access_token:
        logger.error("Missing Instagram Account ID or Meta Access Token. Cannot publish.")
        raise ValueError("Missing Instagram Publishing Credentials.")

    full_caption = f"{caption}\n\n{hashtags}"
    
    # 1. Create the IG Media Container
    logger.info("Initializing Reels Media Container on Meta Servers...")
    container_url = f"https://graph.facebook.com/v19.0/{ig_account_id}/media"
    
    payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": full_caption,
        "access_token": access_token
    }
    
    try:
        response = retry_request("post", container_url, data=payload, timeout=20)
        res_data = response.json()
        
        if "id" not in res_data:
            logger.error(f"Failed to create IG Media Container. Meta API Response: {res_data}")
            response.raise_for_status()
            
        container_id = res_data["id"]
        logger.info(f"Reels Media Container created successfully! Container ID: {container_id}")
        
    except Exception as e:
        logger.error(f"Network error during media container creation: {e}")
        raise e

    # 2. Poll Media Container Status
    status_url = f"https://graph.facebook.com/v19.0/{container_id}"
    params = {
        "fields": "status_code",
        "access_token": access_token
    }
    
    max_retries = 20
    poll_interval_seconds = 15
    published = False
    
    logger.info("Polling Meta server status until video processing is completed...")
    
    for attempt in range(max_retries):
        time.sleep(poll_interval_seconds)
        
        try:
            status_resp = retry_request("get", status_url, params=params, timeout=15)
            status_data = status_resp.json()
            logger.info(f"Raw Status Data: {status_data}")
            
            status_code = status_data.get("status_code")
            logger.info(f"Polling Attempt {attempt + 1}/{max_retries} | Status Code: {status_code}")
            
            if status_code == "FINISHED":
                logger.info("Reel video parsing finished. Proceeding to publish event!")
                published = True
                break
            elif status_code == "ERROR":
                reason = status_data.get("failure_reason", "Unknown Meta Error")
                logger.error(f"Meta video processing failed with error status: {reason}")
                raise RuntimeError(f"Meta Transcoding Error: {reason}")
                
        except Exception as e:
            logger.warning(f"Error checking container status: {e}. Retrying polling loop...")
            
    if not published:
        logger.error("Meta API container polling timed out. Process aborted.")
        raise TimeoutError("Meta Video Transcoding Polling Timed Out.")

    # 3. Publish the completed Reel
    logger.info("Triggering final Reels publish event...")
    publish_url = f"https://graph.facebook.com/v19.0/{ig_account_id}/media_publish"
    
    publish_payload = {
        "creation_id": container_id,
        "access_token": access_token
    }
    
    try:
        pub_response = retry_request("post", publish_url, data=publish_payload, timeout=20)
        pub_data = pub_response.json()
        
        if "id" in pub_data:
            post_id = pub_data["id"]
            logger.info(f"SUCCESS! Reel posted live to Instagram. Post ID: {post_id}")
            return post_id
        else:
            logger.error(f"Failed to trigger publication event. Response: {pub_data}")
            pub_response.raise_for_status()
            
    except Exception as e:
        logger.error(f"Publish execution error: {e}")
        raise e

def run():
    # Make sure compiled reel exists
    if not os.path.exists(FINAL_REEL):
        logger.error("No final_reel.mp4 found in local directory. Skipping publisher.")
        raise FileNotFoundError(f"Missing {FINAL_REEL}")
        
    if not os.path.exists(SCRIPT_INPUT):
        logger.error("Missing script metadata for captions.")
        raise FileNotFoundError(f"Missing {SCRIPT_INPUT}")
        
    with open(SCRIPT_INPUT, "r", encoding="utf-8") as f:
        meta_data = json.load(f)
        
    cloudinary_url = os.environ.get("CLOUDINARY_URL")
    if not cloudinary_url:
        logger.error("CLOUDINARY_URL environment variable is not configured.")
        raise ValueError("Missing Cloudinary Configuration.")
    
    # 1. Upload to Cloudinary
    public_video_url, public_id = upload_to_cloudinary(FINAL_REEL)
    
    # Extract safely since schema changed to seo_caption_matrix
    caption = meta_data.get("seo_caption_matrix", meta_data.get("instagram_caption", "Amazing Video! 🔥"))
    hashtags_data = meta_data.get("instagram_hashtags", ["#viral", "#trending", "#wealth"])
    hashtags = " ".join(hashtags_data) if isinstance(hashtags_data, list) else hashtags_data
    
    # 2. Publish to Instagram
    try:
        publish_to_instagram(
            video_url=public_video_url,
            caption=caption,
            hashtags=hashtags
        )
    finally:
        # 3. Clean up the public Cloudinary object immediately after publish trigger
        delete_from_cloudinary(public_id)

if __name__ == "__main__":
    run()
