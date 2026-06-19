#!/usr/bin/env python3
"""
X/Twitter poster using browser cookie authentication.
✅ 100% FREE — no API key, no paid plan needed.
✅ PERMANENT FIX — cookies are far more stable than password login.

Required GitHub Secrets:
  X_AUTH_TOKEN  →  value of 'auth_token' cookie from x.com
  X_CT0         →  value of 'ct0' cookie from x.com

How to get cookies (one-time setup, lasts months):
  1. Log into x.com in Chrome/Firefox
  2. Press F12 → Application tab → Cookies → https://x.com
  3. Copy 'auth_token' value → add to GitHub Secret as X_AUTH_TOKEN
  4. Copy 'ct0' value       → add to GitHub Secret as X_CT0
"""
import os
import sys
import asyncio
import logging
from twikit import Client

logging.basicConfig(level=logging.INFO, format="%(asctime)s - X_API_POSTER - %(levelname)s - %(message)s")
logger = logging.getLogger("XApiPoster")

X_AUTH_TOKEN = os.environ.get("X_AUTH_TOKEN", "")
X_CT0        = os.environ.get("X_CT0", "")


async def post_to_x_api(caption: str, video_path: str = None) -> bool:
    # ── Validate credentials ──────────────────────────────────────────────────
    if not X_AUTH_TOKEN or not X_CT0:
        logger.error("❌ Missing X_AUTH_TOKEN or X_CT0 in environment!")
        logger.error("👉 Fix: Add X_AUTH_TOKEN and X_CT0 to GitHub Secrets.")
        logger.error("   Get them from: x.com → F12 → Application → Cookies → https://x.com")
        return False

    # ── Inject cookies directly — no login() call needed ─────────────────────
    client = Client('en-US')
    try:
        logger.info("🍪 Authenticating via browser cookies (no password needed)...")
        client.set_cookies({
            "auth_token": X_AUTH_TOKEN,
            "ct0":        X_CT0,
        })
        logger.info("✅ Cookie auth set successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to set cookies: {e}")
        return False

    # ── Upload video (if provided) ────────────────────────────────────────────
    media_ids = None
    if video_path and os.path.exists(video_path):
        file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
        logger.info(f"🎬 Uploading video: {file_size_mb:.1f} MB (may take a minute)...")
        try:
            media_id = await client.upload_media(video_path, media_category='tweet_video')
            media_ids = [media_id]
            logger.info(f"✅ Video uploaded! Media ID: {media_id}")
        except Exception as e:
            logger.error(f"❌ Video upload failed: {e}")
            logger.warning("⚠️ Posting text-only tweet instead...")
            media_ids = None
    elif video_path:
        logger.warning(f"⚠️ Video file not found: {video_path} — posting text only")

    # ── Post tweet ────────────────────────────────────────────────────────────
    try:
        logger.info("🚀 Publishing tweet...")
        await client.create_tweet(
            text=caption,
            media_ids=media_ids
        )
        logger.info("✅ Successfully posted to X! 🎉")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to publish tweet: {e}")
        # Provide helpful cookie refresh guidance
        if "32" in str(e) or "401" in str(e) or "authenticate" in str(e).lower():
            logger.error("🔑 Cookies may have expired — refresh them:")
            logger.error("   1. Log into x.com in browser")
            logger.error("   2. F12 → Application → Cookies → https://x.com")
            logger.error("   3. Update X_AUTH_TOKEN and X_CT0 in GitHub Secrets")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post_x_twikit.py 'Your caption' [/path/to/video.mp4]")
        sys.exit(1)

    caption_arg = sys.argv[1]
    video_arg   = sys.argv[2] if len(sys.argv) > 2 else None

    success = asyncio.run(post_to_x_api(caption_arg, video_arg))
    sys.exit(0 if success else 1)
