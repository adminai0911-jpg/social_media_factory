"""
post_video.py — Pure Cloud-Based On-Demand Poster
===================================================
Runs on GitHub cloud (ubuntu-latest).
Dynamically generates, renders, and posts a fresh video on every run.
No buffer queue, no releases, no local downloads.
"""

import os
import sys
import json
import time
import random
import logging
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - POSTER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ── Environment ────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")
JITTER_SECONDS     = random.randint(60, 3600)  # 1 to 60 minutes human jitter

# ── Helpers ───────────────────────────────────────────────────────────────────

def send_telegram(message):
    try:
        from ghost.notifications import broadcast_alert
        broadcast_alert(message)
    except Exception as e:
        logger.error(f"Failed to broadcast notification: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# PLATFORM 1 — X / TWITTER
# ══════════════════════════════════════════════════════════════════════════════

def post_twitter(video_path, caption):
    """Post to X/Twitter (Permanently Disabled by User Request)"""
    logger.info("⏭️ Skipping X/Twitter posting (Permanently Disabled)")
    return False


# ══════════════════════════════════════════════════════════════════════════════
# PLATFORM 2 — YOUTUBE SHORTS
# ══════════════════════════════════════════════════════════════════════════════

def post_youtube(video_path, caption):
    """Post to YouTube Shorts using official Google APIs Client Library."""
    try:
        from googleapiclient.discovery import build
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.oauth2.credentials import Credentials
        from googleapiclient.http import MediaFileUpload
        
        # Read from environment refresh token
        refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
        client_id = os.environ.get("YOUTUBE_CLIENT_ID", "")
        client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
        
        if not refresh_token or not client_id or not client_secret:
            logger.error("Missing YouTube OAuth secrets!")
            return False

        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret
        )

        youtube = build("youtube", "v3", credentials=creds)

        body = {
            "snippet": {
                "title": caption[:100],  # Title limited to 100 chars
                "description": caption,
                "categoryId": "22",  # People & Blogs
                "tags": ["shorts", "wealth", "mindset", "viral"]
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(
            video_path,
            mimetype="video/mp4",
            resumable=True
        )

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"Uploading Shorts... {int(status.progress() * 100)}%")

        logger.info(f"✅ YouTube Shorts: Video posted! ID: {response['id']}")
        return True

    except Exception as e:
        logger.error(f"❌ YouTube Shorts failed: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
# PUBLIC URL HELPER (CATBOX)
# ══════════════════════════════════════════════════════════════════════════════

def upload_to_catbox(file_path):
    import requests
    try:
        logger.info("Uploading video to temporary public host (catbox.moe)...")
        with open(file_path, 'rb') as f:
            files = {'reqtype': (None, 'fileupload'), 'fileToUpload': f}
            response = requests.post('https://catbox.moe/user/api.php', files=files, timeout=300)
            if response.status_code == 200 and response.text.startswith("http"):
                logger.info(f"✅ Video uploaded to public URL: {response.text}")
                return response.text
            else:
                logger.error(f"Catbox upload failed: {response.status_code} {response.text}")
                return None
    except Exception as e:
        logger.error(f"Failed to upload to catbox: {e}")
        return None

def wait_for_ig_media_ready(creation_id, access_token):
    import requests
    import time
    url = f"https://graph.facebook.com/v19.0/{creation_id}?fields=status_code&access_token={access_token}"
    for _ in range(12):
        res = requests.get(url).json()
        status = res.get("status_code", "ERROR")
        if status == "FINISHED":
            return True
        elif status == "ERROR":
            return False
        time.sleep(10)
    return False

# ══════════════════════════════════════════════════════════════════════════════
# PLATFORM 3 — INSTAGRAM REELS & STORIES
# ══════════════════════════════════════════════════════════════════════════════

def post_instagram(video_url, caption):
    """Post to Instagram Reels using official Meta Graph API."""
    import requests
    try:
        access_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
        ig_user_id   = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")

        if not access_token or not ig_user_id:
            logger.error("Missing Instagram Reels secrets!")
            return False

        logger.info("Initializing official Instagram Reels posting via Graph API...")
        
        # Step 1: Create media container
        url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": access_token
        }
        res = requests.post(url, data=payload).json()
        creation_id = res.get("id")
        
        if not creation_id:
            logger.error(f"❌ Failed to create IG media container: {res}")
            return False
            
        logger.info(f"Container created ({creation_id}). Waiting for Meta to process video...")
        
        # Step 2: Wait for processing
        if not wait_for_ig_media_ready(creation_id, access_token):
            logger.error("❌ Instagram video processing failed or timed out.")
            return False
            
        # Step 3: Publish
        pub_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
        pub_payload = {"creation_id": creation_id, "access_token": access_token}
        pub_res = requests.post(pub_url, data=pub_payload).json()
        
        if "id" in pub_res:
            logger.info(f"✅ Instagram Reels: Video posted! ID: {pub_res['id']}")
            return True
        else:
            logger.error(f"❌ Failed to publish IG Reel: {pub_res}")
            return False

    except Exception as e:
        logger.error(f"❌ Instagram failed: {e}")
        return False

def post_instagram_story(video_url):
    """Post to Instagram Stories using official Meta Graph API."""
    import requests
    try:
        access_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
        ig_user_id   = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")

        if not access_token or not ig_user_id: return False

        logger.info("Posting Instagram Story via Graph API...")
        
        url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
        payload = {
            "media_type": "STORIES",
            "video_url": video_url,
            "access_token": access_token
        }
        res = requests.post(url, data=payload).json()
        creation_id = res.get("id")
        
        if not creation_id:
            logger.error(f"❌ Failed to create IG story container: {res}")
            return False
            
        if not wait_for_ig_media_ready(creation_id, access_token):
            logger.error("❌ Instagram story processing failed or timed out.")
            return False
            
        pub_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
        pub_payload = {"creation_id": creation_id, "access_token": access_token}
        pub_res = requests.post(pub_url, data=pub_payload).json()
        
        if "id" in pub_res:
            logger.info(f"✅ Instagram Story: Video posted! ID: {pub_res['id']}")
            return True
        else:
            logger.error(f"❌ Failed to publish IG Story: {pub_res}")
            return False

    except Exception as e:
        logger.error(f"❌ Instagram Story failed: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
# PLATFORM 4 — FACEBOOK PAGE VIDEO & STORY
# ══════════════════════════════════════════════════════════════════════════════

def post_facebook(video_path, caption):
    """Post video to Facebook Page using Facebook Graph API."""
    import requests
    try:
        page_id      = os.environ.get("FACEBOOK_PAGE_ID", "")
        access_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")

        if not page_id or not access_token:
            logger.error("Missing Facebook Page credentials!")
            return False

        url = f"https://graph-video.facebook.com/v18.0/{page_id}/videos"
        
        files = {
            "source": open(video_path, "rb")
        }
        payload = {
            "description": caption,
            "access_token": access_token
        }

        logger.info("Uploading video to Facebook Graph API...")
        response = requests.post(url, files=files, data=payload, timeout=300)
        result = response.json()

        if "id" in result:
            logger.info(f"✅ Facebook: Video posted! ID: {result['id']}")
            return True
        else:
            logger.error(f"❌ Facebook API error: {result}")
            return False

    except Exception as e:
        logger.error(f"❌ Facebook failed: {e}")
        return False

def post_facebook_story(video_url):
    """Post to Facebook Stories using Graph API."""
    import requests
    try:
        page_id      = os.environ.get("FACEBOOK_PAGE_ID", "")
        access_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")

        if not page_id or not access_token: return False

        url = f"https://graph.facebook.com/v19.0/{page_id}/video_stories"
        payload = {
            "video_url": video_url,
            "access_token": access_token
        }

        logger.info("Posting Facebook Story...")
        response = requests.post(url, data=payload, timeout=300)
        result = response.json()

        if "id" in result or "video_id" in result or "post_id" in result:
            logger.info(f"✅ Facebook Story: Video posted!")
            return True
        else:
            logger.error(f"❌ Facebook Story API error: {result}")
            return False

    except Exception as e:
        logger.error(f"❌ Facebook Story failed: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    logger.info("=" * 60)
    logger.info("MULTI-PLATFORM ONDEMAND GENERATOR & POSTER")
    logger.info("=" * 60)

    # ── Jitter ────────────────────────────────────────────────────────────────
    logger.info(f"⏱️ Jitter: waiting {JITTER_SECONDS}s before starting run...")
    time.sleep(JITTER_SECONDS)

    logger.info("⚠️ Generating fresh video dynamically on GitHub Actions...")
    send_telegram("⚠️ <b>Poster Starting</b>\nGenerating fresh viral video dynamically on GitHub Actions...")
    
    # Run v32_dopamine_engine.py
    try:
        engine_path = os.path.join(os.path.dirname(__file__), "v32_dopamine_engine.py")
        subprocess.run([sys.executable, engine_path], check=True, timeout=1200)
    except Exception as e:
        logger.error(f"❌ Dynamic video generation failed: {e}")
        send_telegram(f"❌ <b>Generation Failed!</b>\nCould not generate video dynamically: {e}")
        sys.exit(1)
        
    # Verify video exists
    video_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "FINAL_V35_HD.mp4"))
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio", "public", "v32_script.json"))
    
    if not os.path.exists(video_path):
        logger.error(f"Rendered video not found at {video_path}")
        send_telegram("❌ <b>Render Failed!</b>\nRendered video file is missing. Aborting post.")
        sys.exit(1)
        
    caption = "अपना जीवन बदलो। #motivation #success #hindi #viral #shorts"
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                caption = data["script"]["caption"]
        except Exception as e:
            logger.error(f"Failed to read caption from JSON: {e}")

    # Generate Public URL for Meta API
    public_video_url = upload_to_catbox(video_path)

    # Post to all platforms
    results = {}
    
    logger.info("📺 Posting to YouTube Shorts...")
    results["YouTube"] = post_youtube(video_path, caption)
    time.sleep(random.randint(5, 15))

    logger.info("📘 Posting to Facebook Page...")
    results["Facebook"] = post_facebook(video_path, caption)
    time.sleep(random.randint(5, 15))

    if public_video_url:
        logger.info("📸 Posting to Instagram Reels...")
        results["Instagram"] = post_instagram(public_video_url, caption)
        time.sleep(random.randint(5, 15))

        logger.info("📸 Posting to Instagram Story...")
        results["IG Story"] = post_instagram_story(public_video_url)
        time.sleep(random.randint(5, 15))

        logger.info("📘 Posting to Facebook Story...")
        results["FB Story"] = post_facebook_story(public_video_url)
    else:
        logger.error("❌ Skipping IG/FB Story and IG Reel because Catbox upload failed.")
        results["Instagram"] = False
        results["IG Story"] = False
        results["FB Story"] = False

    # ── Report results ────────────────────────────────────────────────────────
    success_list = [p for p, ok in results.items() if ok]
    failed_list  = [p for p, ok in results.items() if not ok]

    logger.info(f"Results: {results}")

    if success_list:
        status_lines = "\n".join(
            [f"✅ {p}" for p in success_list] +
            [f"❌ {p} (failed)" for p in failed_list]
        )
        send_telegram(
            f"📤 <b>Cloud Video Posted!</b>\n"
            f"{status_lines}\n\n"
            f"Caption: {caption[:80]}..."
        )
    else:
        logger.error("❌ ALL platforms failed.")
        send_telegram("❌ <b>All Platforms Failed!</b>\nVideo posting failed for all accounts.")
        sys.exit(1)

if __name__ == "__main__":
    main()
