import os
import time
import json
import requests
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - UPLOADER - %(levelname)s - %(message)s")
logger = logging.getLogger("Uploader")

load_dotenv()

# Meta credentials
PAGE_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID", "")
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")

# YouTube credentials
YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")

# Twitter/X credentials
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET", "")

# Telegram credentials
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")

def get_facebook_page_token(user_token, page_id):
    if not user_token or not page_id:
        return user_token
    # Try to exchange User Access Token for Page Access Token dynamically
    url = f"https://graph.facebook.com/v19.0/{page_id}"
    params = {"fields": "access_token", "access_token": user_token}
    try:
        res = requests.get(url, params=params).json()
        if "access_token" in res:
            logger.info("Successfully obtained Page Access Token dynamically.")
            return res["access_token"]
        else:
            logger.warning(f"Facebook Page Token exchange response: {res}. Using original token.")
    except Exception as e:
        logger.error(f"Error exchanging token: {e}. Using original token.")
    return user_token

def upload_to_tmpfiles(file_path):
    logger.info("Uploading video to tmpfiles.org to get a public URL for Instagram...")
    try:
        url = "https://tmpfiles.org/api/v1/upload"
        with open(file_path, "rb") as f:
            files = {"file": f}
            res = requests.post(url, files=files)
            if res.status_code == 200:
                data = res.json()
                file_url = data["data"]["url"]
                # Convert the view URL to direct download URL
                direct_url = file_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
                logger.info(f"Public URL generated for Instagram: {direct_url}")
                return direct_url
            else:
                logger.error(f"Failed to upload to tmpfiles.org: {res.status_code} - {res.text}")
    except Exception as e:
        logger.error(f"Error uploading to tmpfiles.org: {e}")
    return None

def upload_to_facebook_reels(video_path, description):
    if not PAGE_ACCESS_TOKEN or not PAGE_ID:
        logger.warning("⏭️ Skipping Facebook Reels (Missing Credentials)")
        return False
        
    page_token = get_facebook_page_token(PAGE_ACCESS_TOKEN, PAGE_ID)
    
    logger.info(f"📤 Starting Facebook Reel upload for {video_path}")
    init_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    init_payload = {"upload_phase": "start", "access_token": page_token}
    
    try:
        init_res = requests.post(init_url, data=init_payload).json()
        if "video_id" not in init_res:
            logger.error(f"Failed to initialize FB upload: {init_res}")
            return False
            
        video_id = init_res["video_id"]
        upload_url = init_res["upload_url"]
        
        headers = {"Authorization": f"OAuth {page_token}", "offset": "0", "file_size": str(os.path.getsize(video_path))}
        with open(video_path, "rb") as f:
            upload_res = requests.post(upload_url, headers=headers, data=f).json()
            
        publish_payload = {
            "upload_phase": "finish", "access_token": page_token,
            "video_id": video_id, "video_state": "PUBLISHED", "description": description
        }
        publish_res = requests.post(init_url, data=publish_payload).json()
        if "success" in publish_res and publish_res["success"]:
            logger.info("✅ Successfully published to Facebook Reels!")
            return True
        else:
            logger.error(f"Failed to publish FB Reel: {publish_res}")
    except Exception as e:
        logger.error(f"FB Upload Exception: {e}")
    return False

def upload_to_instagram_reels(video_path, description):
    if not PAGE_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        logger.warning("⏭️ Skipping Instagram Reels (Missing Credentials)")
        return False
        
    page_token = get_facebook_page_token(PAGE_ACCESS_TOKEN, PAGE_ID)
    
    # Upload video to tmpfiles.org to get a direct public URL
    video_url = upload_to_tmpfiles(video_path)
    if not video_url:
        logger.error("❌ Failed to get a public URL for Instagram Reel. Skipping IG upload.")
        return False

    logger.info(f"📤 Starting Instagram Reel upload with URL: {video_url}")
    container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
    container_payload = {"media_type": "REELS", "video_url": video_url, "caption": description, "access_token": page_token}
    
    try:
        container_res = requests.post(container_url, data=container_payload).json()
        if "id" not in container_res:
            logger.error(f"Failed to create IG Media Container: {container_res}")
            return False
            
        creation_id = container_res["id"]
        
        # Poll container status until it is FINISHED or fails
        status_url = f"https://graph.facebook.com/v19.0/{creation_id}"
        status_params = {"fields": "status_code,status", "access_token": page_token}
        
        max_attempts = 30
        seconds_between_attempts = 10
        is_ready = False
        
        logger.info("Waiting for Instagram to process the video...")
        for attempt in range(max_attempts):
            time.sleep(seconds_between_attempts)
            try:
                status_res = requests.get(status_url, params=status_params).json()
                status_code = status_res.get("status_code", "")
                logger.info(f"Instagram container status (attempt {attempt+1}/{max_attempts}): {status_code}")
                if status_code == "FINISHED":
                    is_ready = True
                    break
                elif status_code in ["ERROR", "EXPIRED"]:
                    logger.error(f"Instagram video processing failed: {status_res}")
                    break
            except Exception as e:
                logger.error(f"Error checking Instagram container status: {e}")
                
        if not is_ready:
            logger.error("Instagram Reels container did not become ready in time. Publishing skipped.")
            return False
            
        publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_payload = {"creation_id": creation_id, "access_token": page_token}
        publish_res = requests.post(publish_url, data=publish_payload).json()
        
        if "id" in publish_res:
            logger.info("✅ Successfully published to Instagram Reels!")
            return True
        else:
            logger.error(f"Failed to publish IG Reel: {publish_res}")
    except Exception as e:
        logger.error(f"IG Upload Exception: {e}")
    return False

def upload_to_youtube_shorts(video_path, description):
    if not YOUTUBE_CLIENT_ID or not YOUTUBE_CLIENT_SECRET or not YOUTUBE_REFRESH_TOKEN:
        logger.warning("⏭️ Skipping YouTube Shorts (Missing Credentials)")
        return False
        
    logger.info("📤 Starting YouTube Shorts upload...")
    try:
        # Step 1: Refresh Access Token
        token_url = "https://oauth2.googleapis.com/token"
        token_payload = {
            "client_id": YOUTUBE_CLIENT_ID,
            "client_secret": YOUTUBE_CLIENT_SECRET,
            "refresh_token": YOUTUBE_REFRESH_TOKEN,
            "grant_type": "refresh_token"
        }
        token_res = requests.post(token_url, data=token_payload).json()
        access_token = token_res.get("access_token")
        if not access_token:
            logger.error(f"Failed to refresh YouTube access token: {token_res}")
            return False
            
        # Step 2: Initialize Resumable Upload Session
        upload_init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Length": str(os.path.getsize(video_path)),
            "X-Upload-Content-Type": "video/mp4"
        }
        
        # Clean up title (limit to 70 chars, remove hashtags)
        clean_title = description.split("#")[0].strip()
        if not clean_title:
            clean_title = "Viral Short"
        if len(clean_title) > 70:
            clean_title = clean_title[:67] + "..."
            
        metadata = {
            "snippet": {
                "title": clean_title,
                "description": description,
                "categoryId": "22"  # People & Blogs
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        init_res = requests.post(upload_init_url, headers=headers, json=metadata)
        if init_res.status_code != 200:
            logger.error(f"Failed to initialize YouTube upload: {init_res.status_code} - {init_res.text}")
            return False
            
        upload_url = init_res.headers.get("Location")
        if not upload_url:
            logger.error("No Location header returned from YouTube upload initialization.")
            return False
            
        # Step 3: Upload Video File
        file_size = os.path.getsize(video_path)
        put_headers = {
            "Content-Length": str(file_size),
            "Content-Type": "video/mp4"
        }
        
        with open(video_path, "rb") as f:
            put_res = requests.put(upload_url, headers=put_headers, data=f)
            
        if put_res.status_code in [200, 201]:
            logger.info("✅ Successfully published to YouTube Shorts!")
            return True
        else:
            logger.error(f"YouTube file upload failed: {put_res.status_code} - {put_res.text}")
    except Exception as e:
        logger.error(f"YouTube Upload Exception: {e}")
    return False

def upload_to_x_via_make(video_path, description):
    MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL", "")
    if not MAKE_WEBHOOK_URL:
        logger.warning("⏭️ Skipping X/Twitter via Make.com (Missing MAKE_WEBHOOK_URL)")
        return False

    logger.info("📤 Starting X/Twitter upload via Make.com Webhook...")
    try:
        # We need a public URL for Make.com to download and post the video.
        video_url = upload_to_tmpfiles(video_path)
        if not video_url:
            logger.error("❌ Failed to get public URL for X/Twitter Webhook. Skipping.")
            return False

        # Clean up tweet text (X limits to 280 chars)
        tweet_text = description
        if len(tweet_text) > 270:
            tweet_text = tweet_text[:267] + "..."

        payload = {
            "video_url": video_url,
            "caption": tweet_text
        }

        res = requests.post(MAKE_WEBHOOK_URL, json=payload)
        
        if res.status_code in [200, 202, 204] or res.text == "Accepted":
            logger.info("✅ Successfully sent payload to Make.com for X/Twitter!")
            return True
        else:
            logger.error(f"❌ Failed to trigger Make.com webhook: {res.status_code} - {res.text}")
            return False
            
    except Exception as e:
        logger.error(f"X Upload via Make.com Exception: {e}")
    return False

def distribute_to_all_platforms(video_path, description):
    logger.info("🌐 Initiating 4-Platform Distribution Pipeline...")
    logger.info(f"📝 Final Caption: {description}")
    
    send_telegram_alert("🚀 <b>V32 Factory Wakeup</b>\nStarting generation and distribution process...")
    
    # Run the uploads
    fb = upload_to_facebook_reels(video_path, description)
    ig = upload_to_instagram_reels(video_path, description)
    yt = upload_to_youtube_shorts(video_path, description)
    x = upload_to_x_via_make(video_path, description)
    
    logger.info("🚀 Distribution Complete!")
    
    status_msg = f"""
✅ <b>V32 Factory Complete</b>
<i>Successfully distributed payload.</i>

<b>Platforms:</b>
🟦 Facebook: {'✅' if fb else '❌'}
🟪 Instagram: {'✅' if ig else '❌'}
🟥 YouTube: {'✅' if yt else '❌'}
⬛ X/Twitter: {'✅' if x else '❌'}

<b>Caption Used:</b>
{description}
"""
    send_telegram_alert(status_msg)
    
    return {
        "facebook": fb,
        "instagram": ig,
        "youtube": yt,
        "x": x
    }

if __name__ == "__main__":
    video_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "FINAL_V35_HD.mp4"))
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "remotion-studio", "public", "v32_script.json"))
    
    if not os.path.exists(video_path):
        logger.error(f"Rendered video not found at {video_path}")
        # Stop execution so we don't upload a dummy file that breaks IG/X and silently fails on FB/YT
        raise FileNotFoundError(f"Video file missing: {video_path}")
        
    caption = "आज ही शुरुआत करें। #wealth #mindset #money #success #hindi"
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                caption = data["script"]["caption"]
        except Exception as e:
            logger.error(f"Failed to read caption from JSON: {e}")
            
    distribute_to_all_platforms(video_path, caption)
