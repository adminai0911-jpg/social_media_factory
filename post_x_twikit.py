#!/usr/bin/env python3
import os
import sys
import asyncio
import logging
from twikit import Client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - X_API_POSTER - %(levelname)s - %(message)s")
logger = logging.getLogger("XApiPoster")

X_USERNAME = os.environ.get("X_USERNAME", "")
X_PASSWORD = os.environ.get("X_PASSWORD", "")
X_EMAIL    = os.environ.get("X_EMAIL", X_USERNAME)

async def post_to_x_api(caption: str, video_path: str = None) -> bool:
    if not X_USERNAME or not X_PASSWORD:
        logger.error("❌ Missing X_USERNAME or X_PASSWORD environment variables!")
        return False

    client = Client('en-US')
    
    # Try to load existing cookies to avoid repeated logins
    cookies_path = "x_cookies.json"
    if os.path.exists(cookies_path):
        try:
            client.load_cookies(cookies_path)
            logger.info("🍪 Loaded existing cookies!")
        except Exception:
            pass

    try:
        logger.info("🔐 Logging into X via Internal API...")
        await client.login(
            auth_info_1=X_USERNAME,
            auth_info_2=X_EMAIL,
            password=X_PASSWORD
        )
        logger.info("✅ Login successful!")
        client.save_cookies(cookies_path)
    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        return False

    media_ids = None
    if video_path and os.path.exists(video_path):
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        logger.info(f"🎬 Uploading video: {file_size_mb:.1f} MB (This may take a minute)...")
        try:
            # Twikit handles chunked uploads automatically
            media_id = await client.upload_media(video_path, media_category='tweet_video')
            media_ids = [media_id]
            logger.info(f"✅ Video uploaded successfully! Media ID: {media_id}")
        except Exception as e:
            logger.error(f"❌ Video upload failed: {e}")
            logger.warning("⚠️ Proceeding to post text-only...")
            media_ids = None

    try:
        logger.info("🚀 Publishing Tweet...")
        await client.create_tweet(
            text=caption,
            media_ids=media_ids
        )
        logger.info("✅ Successfully posted to X! 🎉")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to publish tweet: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post_x_twikit.py 'Your caption' [/path/to/video.mp4]")
        sys.exit(1)

    caption_arg = sys.argv[1]
    video_arg   = sys.argv[2] if len(sys.argv) > 2 else None

    success = asyncio.run(post_to_x_api(caption_arg, video_arg))
    sys.exit(0 if success else 1)
