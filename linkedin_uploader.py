import os
import requests
import json
import logging
import time

logger = logging.getLogger("LinkedInUploader")

def upload_to_linkedin(video_path, caption):
    """
    Uploads a video to LinkedIn using the v2 API (Posts API).
    Requires LINKEDIN_ACCESS_TOKEN and LINKEDIN_AUTHOR_URN (e.g. urn:li:person:12345 or urn:li:organization:67890).
    """
    access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
    author_urn = os.environ.get("LINKEDIN_AUTHOR_URN")
    
    if not access_token or not author_urn:
        logger.error("Missing LINKEDIN_ACCESS_TOKEN or LINKEDIN_AUTHOR_URN")
        return False
        
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202606"
    }
    
    # 1. Initialize Upload
    logger.info("Initializing LinkedIn video upload...")
    init_url = "https://api.linkedin.com/rest/videos?action=initializeUpload"
    init_payload = {
        "initializeUploadRequest": {
            "owner": author_urn,
            "fileSizeBytes": os.path.getsize(video_path),
            "uploadCaptions": False,
            "uploadThumbnail": False
        }
    }
    
    res = requests.post(init_url, headers=headers, json=init_payload, timeout=20)
    if res.status_code != 200:
        logger.error(f"Failed to initialize LinkedIn upload: {res.text}")
        return False
        
    data = res.json()
    upload_url = data["value"]["uploadInstructions"][0]["uploadUrl"]
    video_urn = data["value"]["video"]
    
    # 2. Upload Video
    logger.info(f"Uploading video to LinkedIn ({video_urn})...")
    upload_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream"
    }
    
    with open(video_path, "rb") as f:
        video_data = f.read()
        
    upload_res = requests.put(upload_url, headers=upload_headers, data=video_data, timeout=300)
    
    if upload_res.status_code not in [200, 201]:
        logger.error(f"Failed to upload video bytes to LinkedIn: {upload_res.status_code} {upload_res.text}")
        return False
        
    logger.info("Video uploaded successfully. Creating post...")
    
    # Wait for processing
    time.sleep(5)
    
    # 3. Create Post
    post_url = "https://api.linkedin.com/rest/posts"
    post_payload = {
        "author": author_urn,
        "commentary": caption,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "content": {
            "media": {
                "id": video_urn
            }
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }
    
    post_res = requests.post(post_url, headers=headers, json=post_payload, timeout=20)
    if post_res.status_code == 201:
        post_id = post_res.headers.get("x-linkedin-id", "Unknown")
        logger.info(f"✅ Successfully posted to LinkedIn! Post ID: {post_id}")
        return True
    else:
        logger.error(f"❌ Failed to create LinkedIn post: {post_res.status_code} {post_res.text}")
        return False
