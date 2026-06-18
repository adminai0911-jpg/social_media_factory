"""
post_video.py — Multi-Platform Buffer Consumer v2
===================================================
Runs on GitHub cloud (ubuntu-latest) in under 3 minutes.

Posts to ALL 4 platforms with jitter:
  1. X / Twitter    (twikit)
  2. YouTube Shorts (google-api-python-client)
  3. Instagram Reels (instagrapi)
  4. Facebook Page   (Graph API)

Logic:
  - Fetches the OLDEST .mp4 + .txt from the 'buffer_queue' GitHub Release
  - Posts to all 4 platforms (failures on individual platforms are logged but don't stop others)
  - Deletes the assets from the release ONLY after all platforms attempted
  - Reports results to Telegram

Schedule: 8:00 AM / 12:00 PM / 8:00 PM IST (with 0-5 min random jitter)
"""

import os
import sys
import json
import time
import random
import logging
import subprocess
import tempfile
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - POSTER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ── Environment ────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")
REPO               = os.environ.get("GITHUB_REPOSITORY", "")
RELEASE_TAG        = "buffer_queue"
BUFFER_WARN        = 3      # Telegram alert if buffer drops below this
JITTER_SECONDS     = random.randint(30, 300)  # 30s – 5 min jitter

# ── Helpers ───────────────────────────────────────────────────────────────────

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"},
            timeout=10
        )
    except Exception as e:
        logger.warning(f"Telegram failed: {e}")


def get_buffer_assets():
    """List all assets in the buffer_queue release, sorted by name (oldest first)."""
    result = subprocess.run(
        ["gh", "release", "view", RELEASE_TAG, "--json", "assets"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return []
    data = json.loads(result.stdout)
    assets = data.get("assets", [])
    return sorted(assets, key=lambda x: x["name"])


def get_mp4_count():
    try:
        return len([a for a in get_buffer_assets() if a["name"].endswith(".mp4")])
    except Exception:
        return 0


def download_asset(asset_name, dest_dir):
    subprocess.run(
        ["gh", "release", "download", RELEASE_TAG,
         "--pattern", asset_name, "--dir", dest_dir],
        check=True
    )


def delete_asset(asset_name):
    try:
        subprocess.run(
            ["gh", "release", "delete-asset", RELEASE_TAG, asset_name, "--yes"],
            check=True
        )
    except Exception as e:
        logger.warning(f"Could not delete {asset_name}: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# PLATFORM 1 — X / TWITTER
# ══════════════════════════════════════════════════════════════════════════════

def post_twitter(video_path, caption):
    """Post to X/Twitter using twikit."""
    import asyncio

    try:
        import twikit
    except ImportError:
        logger.error("twikit not installed")
        return False

    username   = os.environ.get("TWITTER_USERNAME")
    email      = os.environ.get("TWITTER_EMAIL")
    password   = os.environ.get("TWITTER_PASSWORD")
    cookies_j  = os.environ.get("TWITTER_COOKIES_JSON", "")

    if not username:
        logger.warning("Twitter: TWITTER_USERNAME not set — skipping.")
        return False

    async def _run():
        client = twikit.Client("en-US")
        cookie_path = "/tmp/tw_cookies.json"
        if cookies_j:
            with open(cookie_path, "w") as f:
                f.write(cookies_j)
            client.load_cookies(cookie_path)
        else:
            await client.login(
                auth_info_1=username,
                auth_info_2=email,
                password=password
            )
            client.save_cookies(cookie_path)

        media_id = await client.upload_media(video_path, media_type="video/mp4")
        await client.create_tweet(text=caption[:280], media_ids=[media_id])
        logger.info("✅ Twitter: Posted!")
        return True

    try:
        return asyncio.run(_run())
    except Exception as e:
        logger.error(f"❌ Twitter failed: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# PLATFORM 2 — YOUTUBE SHORTS
# ══════════════════════════════════════════════════════════════════════════════

def post_youtube(video_path, caption):
    """Upload to YouTube Shorts via YouTube Data API v3."""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
    except ImportError:
        logger.error("google-api-python-client not installed")
        return False

    creds_json = os.environ.get("YOUTUBE_CREDENTIALS_JSON", "")
    if not creds_json:
        logger.warning("YouTube: YOUTUBE_CREDENTIALS_JSON not set — skipping.")
        return False

    try:
        creds_data = json.loads(creds_json)
        creds = Credentials(
            token=creds_data.get("access_token"),
            refresh_token=creds_data.get("refresh_token"),
            client_id=creds_data.get("client_id"),
            client_secret=creds_data.get("client_secret"),
            token_uri="https://oauth2.googleapis.com/token",
            scopes=["https://www.googleapis.com/auth/youtube.upload"]
        )

        youtube = build("youtube", "v3", credentials=creds)

        # Title: first 100 chars of caption, body: full caption
        title = caption[:97] + "..." if len(caption) > 100 else caption
        # Append #Shorts so YouTube processes it as a Short
        description = caption + "\n\n#Shorts"

        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": ["shorts", "motivation", "hindi", "viral", "trending"],
                    "categoryId": "22",  # People & Blogs
                    "defaultLanguage": "hi",
                },
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False,
                    "madeForKids": False,
                }
            },
            media_body=MediaFileUpload(
                video_path,
                mimetype="video/mp4",
                resumable=True,
                chunksize=1024*1024*5  # 5 MB chunks
            )
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info(f"YouTube upload: {int(status.progress() * 100)}%")

        video_id = response.get("id")
        logger.info(f"✅ YouTube: Posted! https://youtube.com/shorts/{video_id}")
        return True

    except Exception as e:
        logger.error(f"❌ YouTube failed: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# PLATFORM 3 — INSTAGRAM REELS
# ══════════════════════════════════════════════════════════════════════════════

def post_instagram(video_path, caption):
    """Upload to Instagram as a Reel using instagrapi."""
    try:
        from instagrapi import Client as IgClient
    except ImportError:
        logger.error("instagrapi not installed")
        return False

    username = os.environ.get("INSTAGRAM_USERNAME")
    password = os.environ.get("INSTAGRAM_PASSWORD")
    session_json = os.environ.get("INSTAGRAM_SESSION_JSON", "")

    if not username:
        logger.warning("Instagram: INSTAGRAM_USERNAME not set — skipping.")
        return False

    try:
        cl = IgClient()
        cl.delay_range = [1, 3]

        session_path = "/tmp/ig_session.json"
        if session_json:
            with open(session_path, "w") as f:
                f.write(session_json)
            cl.load_settings(session_path)
            cl.login(username, password)
        else:
            cl.login(username, password)
            cl.dump_settings(session_path)

        # Upload as Reel (vertical video)
        media = cl.clip_upload(
            video_path,
            caption=caption
        )
        logger.info(f"✅ Instagram: Reel posted! ID: {media.pk}")
        return True

    except Exception as e:
        logger.error(f"❌ Instagram failed: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# PLATFORM 4 — FACEBOOK PAGE
# ══════════════════════════════════════════════════════════════════════════════

def post_facebook(video_path, caption):
    """Upload a video to a Facebook Page using the Graph API."""
    page_id    = os.environ.get("FACEBOOK_PAGE_ID")
    page_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")

    if not page_id or not page_token:
        logger.warning("Facebook: FACEBOOK_PAGE_ID or FACEBOOK_PAGE_ACCESS_TOKEN not set — skipping.")
        return False

    try:
        url = f"https://graph-video.facebook.com/v19.0/{page_id}/videos"

        with open(video_path, "rb") as video_file:
            response = requests.post(
                url,
                data={
                    "description": caption,
                    "published": "true",
                    "access_token": page_token
                },
                files={"source": ("video.mp4", video_file, "video/mp4")},
                timeout=300
            )

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
    logger.info("MULTI-PLATFORM BUFFER POSTER v2 STARTING")
    logger.info("=" * 60)

    # ── Check buffer ──────────────────────────────────────────────────────────
    buffer_count = get_mp4_count()
    logger.info(f"📦 Buffer: {buffer_count} video(s) ready.")
    send_telegram(f"📦 <b>Poster Starting</b>\nBuffer: {buffer_count} videos ready.\nPosting to 4 platforms...")

    if buffer_count == 0:
        logger.warning("⚠️ Buffer is EMPTY — nothing to post.")
        send_telegram(
            "⚠️ <b>Buffer EMPTY!</b>\nNo video posted today.\n"
            "Please turn on your PC to generate more videos!"
        )
        sys.exit(0)

    if buffer_count <= BUFFER_WARN:
        send_telegram(
            f"🔶 <b>Low Buffer!</b>\nOnly {buffer_count} video(s) left.\n"
            "Please turn on your PC to generate more."
        )

    # ── Jitter ────────────────────────────────────────────────────────────────
    logger.info(f"⏱️ Jitter: waiting {JITTER_SECONDS}s before posting...")
    time.sleep(JITTER_SECONDS)

    # ── Get oldest video from buffer ──────────────────────────────────────────
    assets   = get_buffer_assets()
    mp4_list = [a for a in assets if a["name"].endswith(".mp4")]
    oldest   = mp4_list[0]
    mp4_name = oldest["name"]
    txt_name = mp4_name.replace(".mp4", ".txt")

    logger.info(f"📥 Downloading: {mp4_name}")

    with tempfile.TemporaryDirectory() as tmpdir:
        mp4_path = os.path.join(tmpdir, mp4_name)
        txt_path = os.path.join(tmpdir, txt_name)

        download_asset(mp4_name, tmpdir)

        caption = "अपना जीवन बदलो। #motivation #success #hindi #viral #shorts"
        try:
            download_asset(txt_name, tmpdir)
            with open(txt_path, "r", encoding="utf-8") as f:
                caption = f.read().strip()
        except Exception:
            logger.warning("Caption .txt not found — using default caption.")

        logger.info(f"📝 Caption: {caption}")

        # ── Post to all 4 platforms ───────────────────────────────────────────
        results = {}

        logger.info("🐦 Posting to X/Twitter...")
        results["Twitter"] = post_twitter(mp4_path, caption)
        time.sleep(random.randint(5, 15))  # small gap between platforms

        logger.info("📺 Posting to YouTube Shorts...")
        results["YouTube"] = post_youtube(mp4_path, caption)
        time.sleep(random.randint(5, 15))

        logger.info("📸 Posting to Instagram Reels...")
        results["Instagram"] = post_instagram(mp4_path, caption)
        time.sleep(random.randint(5, 15))

        logger.info("📘 Posting to Facebook Page...")
        results["Facebook"] = post_facebook(mp4_path, caption)

    # ── Report results ────────────────────────────────────────────────────────
    success_list = [p for p, ok in results.items() if ok]
    failed_list  = [p for p, ok in results.items() if not ok]

    logger.info(f"Results: {results}")

    # ── Delete from buffer if at least one platform succeeded ─────────────────
    if success_list:
        logger.info(f"🗑️ Deleting {mp4_name} from buffer...")
        delete_asset(mp4_name)
        delete_asset(txt_name)

        status_lines = "\n".join(
            [f"✅ {p}" for p in success_list] +
            [f"❌ {p} (failed)" for p in failed_list]
        )
        send_telegram(
            f"📤 <b>Posted!</b>\n"
            f"{status_lines}\n\n"
            f"Buffer remaining: {buffer_count - 1} videos\n"
            f"Caption: {caption[:80]}..."
        )
    else:
        # ALL platforms failed — keep video in buffer for retry
        logger.error("❌ ALL platforms failed. Video kept in buffer for next run.")
        send_telegram(
            "❌ <b>All Platforms Failed!</b>\n"
            "Video kept in buffer — will retry at next scheduled time."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
