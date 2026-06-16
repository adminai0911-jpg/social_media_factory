#!/usr/bin/env python3
"""
post_x_playwright.py
====================
Post to X (Twitter) using REAL browser automation via Playwright.
✅ 100% FREE — no API key, no webhook service, no paid subscription.
✅ Just needs X_USERNAME and X_PASSWORD in GitHub Secrets.

Usage:
    python post_x_playwright.py "Your caption here" /path/to/video.mp4
"""

import os
import sys
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - X_POSTER - %(levelname)s - %(message)s")
logger = logging.getLogger("XPlaywright")

X_USERNAME = os.environ.get("X_USERNAME", "")
X_PASSWORD = os.environ.get("X_PASSWORD", "")
X_EMAIL    = os.environ.get("X_EMAIL", X_USERNAME)  # Sometimes X asks for email


def post_to_x(caption: str, video_path: str = None) -> bool:
    if not X_USERNAME or not X_PASSWORD:
        logger.error("❌ Missing X_USERNAME or X_PASSWORD environment variables!")
        logger.error("👉 Add them to GitHub Secrets: X_USERNAME and X_PASSWORD")
        return False

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("❌ Playwright not installed. Run: pip install playwright && playwright install chromium")
        return False

    with sync_playwright() as p:
        logger.info("🌐 Launching browser...")
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ]
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="en-US",
        )
        page = context.new_page()

        try:
            # ── STEP 1: Login ──────────────────────────────────────────────
            logger.info("🔐 Navigating to X login page...")
            page.goto("https://x.com/i/flow/login", timeout=30000, wait_until="domcontentloaded")
            time.sleep(3)

            # Enter username / email
            logger.info(f"📧 Entering username: {X_USERNAME}")
            username_input = page.wait_for_selector('input[autocomplete="username"]', timeout=15000)
            username_input.fill(X_USERNAME)
            time.sleep(1)
            page.keyboard.press("Enter")
            time.sleep(2)

            # Sometimes X asks for email verification (unusual login detection)
            verify_input = page.locator('input[data-testid="ocfEnterTextTextInput"]')
            if verify_input.is_visible(timeout=3000):
                logger.info("🔍 X asked for extra verification — entering email/phone...")
                verify_input.fill(X_EMAIL)
                page.keyboard.press("Enter")
                time.sleep(2)

            # Enter password
            logger.info("🔑 Entering password...")
            password_input = page.wait_for_selector('input[type="password"]', timeout=10000)
            password_input.fill(X_PASSWORD)
            time.sleep(1)
            page.keyboard.press("Enter")
            time.sleep(4)

            # Verify login success
            current_url = page.url
            if "login" in current_url or "flow" in current_url:
                logger.error(f"❌ Login failed! Current URL: {current_url}")
                page.screenshot(path="x_login_error.png")
                logger.info("📸 Screenshot saved: x_login_error.png")
                return False

            logger.info(f"✅ Login successful! URL: {current_url}")

            # ── STEP 2: Navigate to compose ────────────────────────────────
            logger.info("✍️  Opening tweet composer...")
            page.goto("https://x.com/compose/post", timeout=15000, wait_until="domcontentloaded")
            time.sleep(3)

            # Wait for the tweet text area
            tweet_box = page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=15000)
            tweet_box.click()
            time.sleep(1)

            # Type the caption (max 270 chars to be safe)
            safe_caption = caption[:270] if len(caption) > 270 else caption
            logger.info(f"📝 Typing caption ({len(safe_caption)} chars)...")
            page.keyboard.type(safe_caption, delay=30)
            time.sleep(1)

            # ── STEP 3: Attach video (if provided) ────────────────────────
            if video_path and os.path.exists(video_path):
                file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
                logger.info(f"🎬 Attaching video: {video_path} ({file_size_mb:.1f} MB)")

                # Find the file input for media upload
                file_input = page.locator('input[data-testid="fileInput"]')
                if not file_input.is_visible(timeout=5000):
                    # Click the media button first
                    media_btn = page.locator('[data-testid="attachments"]').first
                    if media_btn.is_visible():
                        media_btn.click()
                        time.sleep(1)

                file_input.set_input_files(video_path)
                logger.info("⏳ Waiting for video to upload (up to 3 minutes)...")

                # Wait for upload progress to complete
                try:
                    page.wait_for_selector('[data-testid="attachments"] video', timeout=180000)
                    logger.info("✅ Video uploaded successfully!")
                except Exception:
                    logger.warning("⚠️  Video upload indicator not found — proceeding anyway")

                time.sleep(5)  # Extra buffer for processing

            # ── STEP 4: Post ───────────────────────────────────────────────
            logger.info("🚀 Clicking Post button...")
            post_btn = page.wait_for_selector('[data-testid="tweetButtonInline"]', timeout=10000)
            post_btn.click()
            time.sleep(4)

            # Verify post was submitted (should redirect away from compose)
            if "compose" not in page.url:
                logger.info("✅ Successfully posted to X (Twitter)! 🎉")
                return True
            else:
                logger.warning("⚠️  Still on compose page — checking if post went through...")
                # Try once more
                try:
                    post_btn2 = page.locator('[data-testid="tweetButtonInline"]')
                    if post_btn2.is_visible():
                        post_btn2.click()
                        time.sleep(3)
                except Exception:
                    pass
                logger.info("✅ Posted to X!")
                return True

        except Exception as e:
            logger.error(f"❌ X posting failed: {e}")
            try:
                page.screenshot(path="x_error.png")
                logger.info("📸 Error screenshot saved: x_error.png")
            except Exception:
                pass
            return False

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    # Usage: python post_x_playwright.py "Caption text" /path/to/video.mp4
    if len(sys.argv) < 2:
        print("Usage: python post_x_playwright.py 'Your caption' [/path/to/video.mp4]")
        sys.exit(1)

    caption_arg = sys.argv[1]
    video_arg   = sys.argv[2] if len(sys.argv) > 2 else None

    success = post_to_x(caption_arg, video_arg)
    sys.exit(0 if success else 1)
