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

# Telegram credentials
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")

def get_facebook_page_token(user_token, page_id):
    if not user_token or not page_id:
        return user_token
    url = f"https://graph.facebook.com/v19.0/{page_id}"
    params = {"fields": "access_token", "access_token": user_token}
    try:
        res = requests.get(url, params=params, timeout=10).json()
        if "access_token" in res:
            logger.info("Successfully obtained Page Access Token dynamically.")
            return res["access_token"]
        else:
            logger.warning(f"Facebook Page Token exchange response: {res}. Using original token.")
    except Exception as e:
        logger.error(f"Error exchanging token: {e}. Using original token.")
    return user_token

def upload_to_temp_host(file_path):
    logger.info("Uploading video to temporary public host (0x0.st)...")
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post('https://0x0.st', files=files, timeout=300)
            if response.status_code == 200 and response.text.startswith("http"):
                url = response.text.strip()
                logger.info(f"✅ Video uploaded to public URL: {url}")
                return url
            else:
                logger.error(f"0x0.st upload failed: {response.status_code} {response.text}")
                return None
    except Exception as e:
        logger.error(f"Failed to upload to temp host: {e}")
        return None

def wait_for_ig_media_ready(creation_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{creation_id}?fields=status_code&access_token={access_token}"
    for _ in range(12):
        res = requests.get(url).json()
        status = res.get("status_code", "ERROR")
        if status == "FINISHED":
            return True
        elif status == "ERROR" or status == "EXPIRED":
            logger.error(f"IG container failed: {status}")
            return False
        time.sleep(10)
    return False

def upload_to_facebook_reels(video_path, description):
    if not PAGE_ACCESS_TOKEN or not PAGE_ID:
        logger.warning("⏭️ Skipping Facebook Reels (Missing Credentials)")
        return False
        
    page_token = get_facebook_page_token(PAGE_ACCESS_TOKEN, PAGE_ID)
    
    logger.info(f"📤 Starting Facebook Reel upload for {video_path}")
    init_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    init_payload = {"upload_phase": "start", "access_token": page_token}
    
    try:
        init_res = requests.post(init_url, data=init_payload, timeout=30).json()
        if "video_id" not in init_res:
            logger.error(f"Failed to initialize FB upload: {init_res}")
            return False
            
        video_id = init_res["video_id"]
        upload_url = init_res["upload_url"]
        
        headers = {"Authorization": f"OAuth {page_token}", "offset": "0", "file_size": str(os.path.getsize(video_path))}
        with open(video_path, "rb") as f:
            requests.post(upload_url, headers=headers, data=f, timeout=60).json()
            
        publish_payload = {
            "upload_phase": "finish", "access_token": page_token,
            "video_id": video_id, "video_state": "PUBLISHED", "description": description
        }
        publish_res = requests.post(init_url, data=publish_payload, timeout=30).json()
        if "success" in publish_res and publish_res["success"]:
            logger.info("✅ Successfully published to Facebook Reels!")
            return True
        else:
            logger.error(f"Failed to publish FB Reel: {publish_res}")
    except Exception as e:
        logger.error(f"FB Upload Exception: {e}")
    return False

def upload_to_facebook_story(video_url):
    if not PAGE_ACCESS_TOKEN or not PAGE_ID: return False
    page_token = get_facebook_page_token(PAGE_ACCESS_TOKEN, PAGE_ID)
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_stories"
    payload = {"video_url": video_url, "access_token": page_token}
    try:
        logger.info("Posting Facebook Story...")
        result = requests.post(url, data=payload, timeout=300).json()
        if "id" in result or "video_id" in result or "post_id" in result:
            logger.info(f"✅ Facebook Story posted!")
            return True
        else:
            logger.error(f"❌ Facebook Story API error: {result}")
    except Exception as e:
        logger.error(f"❌ Facebook Story failed: {e}")
    return False

def upload_to_instagram_reels(video_url, description):
    if not PAGE_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID or not PAGE_ID:
        logger.warning("⏭️ Skipping Instagram Reels (Missing Credentials)")
        return False
    
    page_token = get_facebook_page_token(PAGE_ACCESS_TOKEN, PAGE_ID)
    logger.info(f"📤 Starting Instagram Reel upload with URL")
    
    container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
    container_payload = {"media_type": "REELS", "video_url": video_url, "caption": description, "access_token": page_token}
    
    try:
        container_res = requests.post(container_url, data=container_payload, timeout=30).json()
        if "id" not in container_res:
            logger.error(f"Failed to create IG Media Container: {container_res}")
            return False
            
        creation_id = container_res["id"]
        logger.info(f"✅ Created IG container: {creation_id}")
        
        if not wait_for_ig_media_ready(creation_id, page_token):
            return False
            
        publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_payload = {"creation_id": creation_id, "access_token": page_token}
        publish_res = requests.post(publish_url, data=publish_payload, timeout=30).json()
        
        if "id" in publish_res:
            logger.info("✅ Successfully published to Instagram Reels!")
            return True
        else:
            logger.error(f"Failed to publish IG Reel: {publish_res}")
    except Exception as e:
        logger.error(f"IG Upload Exception: {e}")
    return False

def upload_to_instagram_story(video_url):
    if not PAGE_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID or not PAGE_ID: return False
    page_token = get_facebook_page_token(PAGE_ACCESS_TOKEN, PAGE_ID)
    logger.info("Posting Instagram Story...")
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {"media_type": "STORIES", "video_url": video_url, "access_token": page_token}
    try:
        res = requests.post(url, data=payload).json()
        creation_id = res.get("id")
        if not creation_id:
            logger.error(f"❌ Failed to create IG story container: {res}")
            return False
        if not wait_for_ig_media_ready(creation_id, page_token):
            return False
        pub_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        pub_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": page_token}).json()
        if "id" in pub_res:
            logger.info("✅ Instagram Story posted!")
            return True
        else:
            logger.error(f"❌ Failed to publish IG Story: {pub_res}")
    except Exception as e:
        logger.error(f"❌ Instagram Story failed: {e}")
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
        token_res = requests.post(token_url, data=token_payload, timeout=30).json()
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
        
        init_res = requests.post(upload_init_url, headers=headers, json=metadata, timeout=30)
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
            put_res = requests.put(upload_url, headers=put_headers, data=f, timeout=120)
            
        if put_res.status_code in [200, 201]:
            logger.info("✅ Successfully published to YouTube Shorts!")
            return True
        else:
            logger.error(f"YouTube file upload failed: {put_res.status_code} - {put_res.text}")
    except Exception as e:
        logger.error(f"YouTube Upload Exception: {e}")
    return False

def distribute_to_all_platforms(video_path, description):
    logger.info("🌐 Initiating Multi-Platform Distribution Pipeline...")
    logger.info(f"📝 Final Caption: {description}")
    
    send_telegram_alert("🚀 <b>V32 Factory Wakeup</b>\nStarting generation and distribution process...")
    
    # Run the uploads
    yt = upload_to_youtube_shorts(video_path, description)
    time.sleep(5)
    fb = upload_to_facebook_reels(video_path, description)
    time.sleep(5)
    
    video_url = upload_to_temp_host(video_path)
    ig, ig_story, fb_story = False, False, False
    
    if video_url:
        ig = upload_to_instagram_reels(video_url, description)
        time.sleep(5)
        ig_story = upload_to_instagram_story(video_url)
        time.sleep(5)
        fb_story = upload_to_facebook_story(video_url)
    else:
        logger.error("❌ Skipping Instagram Reels/Stories because public video URL generation failed.")
        
    logger.info("🚀 Distribution Complete!")
    
    status_msg = f"""
✅ <b>V32 Factory Complete</b>
<i>Successfully distributed payload.</i>

<b>Platforms:</b>
🟥 YouTube Shorts: {'✅' if yt else '❌'}
🟦 Facebook Reels: {'✅' if fb else '❌'}
🟪 Instagram Reels: {'✅' if ig else '❌'}
📘 Facebook Story: {'✅' if fb_story else '❌'}
📸 Instagram Story: {'✅' if ig_story else '❌'}

<b>Caption Used:</b>
{description}
"""
    send_telegram_alert(status_msg)
    
    return {
        "facebook": fb,
        "instagram": ig,
        "youtube": yt,
        "fb_story": fb_story,
        "ig_story": ig_story
    }

if __name__ == "__main__":
    video_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "FINAL_V35_HD.mp4"))
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "remotion-studio", "public", "v32_script.json"))
    
    if not os.path.exists(video_path):
        logger.error(f"Rendered video not found at {video_path}")
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
