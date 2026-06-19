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
    """Post to X/Twitter using twikit."""
    try:
        from post_x_twikit import upload_video_to_x
        # twikit will read X_AUTH_TOKEN and X_CT0 from environment automatically
        upload_video_to_x(video_path, caption)
        logger.info("✅ X/Twitter: Video posted!")
        return True
    except Exception as e:
        logger.error(f"❌ X/Twitter failed: {e}")
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
# PLATFORM 3 — INSTAGRAM REELS
# ══════════════════════════════════════════════════════════════════════════════

def post_instagram(video_path, caption):
    """Post to Instagram Reels using the Meta Graph API."""
    try:
        # We use Meta Graph API for Business/Creator accounts
        access_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
        ig_user_id   = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")

        if not access_token or not ig_user_id:
            logger.error("Missing Instagram Reels secrets!")
            return False

        # Phase 1: Initialize container
        # Note: Meta Graph API requires public URL for media container.
        # Fallback to direct local posting using instagrapi since we don't have public URLs on GitHub runners
        logger.info("Initializing direct Instagram Reels posting via instagrapi...")
        from instagrapi import Client
        cl = Client()
        
        # Safe login
        ig_username = os.environ.get("INSTAGRAM_USERNAME", "")
        ig_password = os.environ.get("INSTAGRAM_PASSWORD", "")
        ig_session  = os.environ.get("INSTAGRAM_SESSION_JSON", "")
        
        if not ig_username or not ig_password:
            logger.error("Missing Instagram credentials!")
            return False
            
        if ig_session:
            try:
                cl.set_settings(json.loads(ig_session))
                cl.login(ig_username, ig_password)
            except Exception:
                cl.login(ig_username, ig_password)
        else:
            cl.login(ig_username, ig_password)
            
        cl.clip_upload(video_path, caption)
        logger.info("✅ Instagram Reels: Video posted!")
        return True

    except Exception as e:
        logger.error(f"❌ Instagram failed: {e}")
        return False

# ══════════════════════════════════════════════════════════════════════════════
# PLATFORM 4 — FACEBOOK PAGE VIDEO
# ══════════════════════════════════════════════════════════════════════════════

def post_facebook(video_path, caption):
    """Post video to Facebook Page using Facebook Graph API."""
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

    # Post to all platforms
    results = {}
    logger.info("🐦 Posting to X/Twitter...")
    results["Twitter"] = post_twitter(video_path, caption)
    time.sleep(random.randint(5, 15))

    logger.info("📺 Posting to YouTube Shorts...")
    results["YouTube"] = post_youtube(video_path, caption)
    time.sleep(random.randint(5, 15))

    logger.info("📸 Posting to Instagram Reels...")
    results["Instagram"] = post_instagram(video_path, caption)
    time.sleep(random.randint(5, 15))

    logger.info("📘 Posting to Facebook Page...")
    import requests # Ensure requests import for Facebook API
    results["Facebook"] = post_facebook(video_path, caption)

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
