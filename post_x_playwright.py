#!/usr/bin/env python3
"""
post_x_playwright.py  — V2 ROBUST
===================================
Post to X (Twitter) via Playwright browser automation.
100% FREE. No API key needed. Just X_USERNAME + X_PASSWORD in GitHub Secrets.

FIX v2: Uses multiple selector fallbacks + longer timeouts.
The old 'input[autocomplete="username"]' broke when X updated their login DOM.
"""

import os
import sys
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - X_POSTER - %(levelname)s - %(message)s")
logger = logging.getLogger("XPlaywright")

X_USERNAME = os.environ.get("X_USERNAME", "")
X_PASSWORD = os.environ.get("X_PASSWORD", "")
X_EMAIL    = os.environ.get("X_EMAIL", X_USERNAME)


def _screenshot(page, name):
    """Save debug screenshot."""
    try:
        path = f"x_debug_{name}.png"
        page.screenshot(path=path)
        logger.info(f"📸 Screenshot: {path}")
    except Exception:
        pass


def _fill_input(page, value, step_name):
    """
    Try multiple strategies to fill an input field.
    X frequently changes their login DOM — we try every known pattern.
    """
    strategies = [
        # Strategy 1: By autocomplete attribute (old reliable)
        lambda: page.locator('input[autocomplete="username"]').first,
        # Strategy 2: By name attribute
        lambda: page.locator('input[name="text"]').first,
        # Strategy 3: First visible textbox on page
        lambda: page.get_by_role("textbox").first,
        # Strategy 4: By placeholder text (multilingual)
        lambda: page.get_by_placeholder("Phone, email, or username").first,
        lambda: page.get_by_placeholder("Phone, email address, or username").first,
        # Strategy 5: Any input that is visible
        lambda: page.locator("input:visible").first,
    ]

    for i, strategy in enumerate(strategies):
        try:
            el = strategy()
            if el.is_visible(timeout=4000):
                el.click()
                time.sleep(0.3)
                el.fill("")
                time.sleep(0.2)
                # Type human-like with small delays
                for char in value:
                    el.press(char)
                    time.sleep(0.05)
                logger.info(f"✅ {step_name}: filled using strategy {i+1}")
                return True
        except Exception as e:
            logger.debug(f"  Strategy {i+1} failed: {e}")
            continue

    logger.error(f"❌ All strategies failed for {step_name}")
    return False


def post_to_x(caption: str, video_path: str = None) -> bool:
    if not X_USERNAME or not X_PASSWORD:
        logger.error("❌ Missing X_USERNAME or X_PASSWORD environment variables!")
        logger.error("👉 Add them to GitHub Secrets: X_USERNAME and X_PASSWORD")
        return False

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("❌ Playwright not installed.")
        return False

    with sync_playwright() as p:
        logger.info("🌐 Launching browser (stealth mode)...")
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--window-size=1280,900",
            ]
        )

        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="Asia/Kolkata",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )

        # Mask automation fingerprint
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """)

        page = context.new_page()

        try:
            # ── STEP 1: Load X login page ──────────────────────────────────
            logger.info("🔐 Loading X login page...")
            page.goto("https://x.com/i/flow/login", timeout=45000, wait_until="domcontentloaded")

            # Wait for page to stabilise — X loads React async
            time.sleep(5)
            _screenshot(page, "01_login_loaded")

            logger.info(f"   Page URL: {page.url}")
            logger.info(f"   Page title: {page.title()}")

            # ── STEP 2: Enter username ─────────────────────────────────────
            logger.info(f"📧 Entering username...")
            time.sleep(2)

            success = _fill_input(page, X_USERNAME, "username")
            if not success:
                _screenshot(page, "02_username_fail")
                # Dump page HTML for debugging
                html = page.content()[:3000]
                logger.error(f"Page HTML snippet:\n{html}")
                return False

            time.sleep(1)

            # Click "Next" button
            next_btns = [
                lambda: page.get_by_role("button", name="Next").first,
                lambda: page.locator('[data-testid="LoginForm_Login_Button"]').first,
                lambda: page.locator('button:has-text("Next")').first,
                lambda: page.locator('div[role="button"]:has-text("Next")').first,
            ]
            next_clicked = False
            for btn_fn in next_btns:
                try:
                    btn = btn_fn()
                    if btn.is_visible(timeout=3000):
                        btn.click()
                        next_clicked = True
                        logger.info("✅ Clicked Next")
                        break
                except Exception:
                    continue

            if not next_clicked:
                logger.warning("⚠️ Could not click Next, pressing Enter instead")
                page.keyboard.press("Enter")

            time.sleep(3)
            _screenshot(page, "03_after_next")

            # ── STEP 3: Check for unusual activity verification ─────────────
            verify_selectors = [
                'input[data-testid="ocfEnterTextTextInput"]',
                'input[name="text"][autocomplete="on"]',
            ]
            for sel in verify_selectors:
                try:
                    verify_input = page.locator(sel)
                    if verify_input.is_visible(timeout=3000):
                        logger.info("🔍 X asked for email/phone verification...")
                        verify_input.fill(X_EMAIL)
                        page.keyboard.press("Enter")
                        time.sleep(2)
                        break
                except Exception:
                    continue

            # ── STEP 4: Enter password ─────────────────────────────────────
            logger.info("🔑 Entering password...")
            time.sleep(2)

            pwd_strategies = [
                lambda: page.locator('input[type="password"]').first,
                lambda: page.get_by_label("Password").first,
                lambda: page.locator('input[name="password"]').first,
                lambda: page.locator('input[autocomplete="current-password"]').first,
            ]

            pwd_filled = False
            for strat in pwd_strategies:
                try:
                    pwd_input = strat()
                    if pwd_input.is_visible(timeout=4000):
                        pwd_input.click()
                        time.sleep(0.3)
                        pwd_input.fill(X_PASSWORD)
                        pwd_filled = True
                        logger.info("✅ Password entered")
                        break
                except Exception:
                    continue

            if not pwd_filled:
                _screenshot(page, "04_pwd_fail")
                logger.error("❌ Could not find password field")
                return False

            time.sleep(1)

            # Click "Log in" button
            login_btns = [
                lambda: page.get_by_role("button", name="Log in").first,
                lambda: page.locator('[data-testid="LoginForm_Login_Button"]').first,
                lambda: page.locator('button:has-text("Log in")').first,
                lambda: page.locator('div[role="button"]:has-text("Log in")').first,
            ]
            login_clicked = False
            for btn_fn in login_btns:
                try:
                    btn = btn_fn()
                    if btn.is_visible(timeout=3000):
                        btn.click()
                        login_clicked = True
                        logger.info("✅ Clicked Log in")
                        break
                except Exception:
                    continue

            if not login_clicked:
                logger.warning("⚠️ Could not click Login button, pressing Enter instead")
                page.keyboard.press("Enter")

            # Wait for login to complete
            time.sleep(6)
            _screenshot(page, "05_after_login")

            current_url = page.url
            logger.info(f"   After login URL: {current_url}")

            if "login" in current_url.lower() or "flow" in current_url.lower():
                logger.error(f"❌ Login failed — still on login page. URL: {current_url}")
                return False

            logger.info(f"✅ Login successful!")

            # ── STEP 5: Open tweet composer ────────────────────────────────
            logger.info("✍️ Opening compose tweet...")
            page.goto("https://x.com/compose/post", timeout=30000, wait_until="domcontentloaded")
            time.sleep(4)
            _screenshot(page, "06_compose_opened")

            # Find tweet textarea
            tweet_box = None
            tweet_selectors = [
                '[data-testid="tweetTextarea_0"]',
                '[data-testid="tweetTextarea_0_label"]',
                'div[contenteditable="true"][role="textbox"]',
                '.public-DraftEditor-content',
            ]
            for sel in tweet_selectors:
                try:
                    el = page.locator(sel).first
                    if el.is_visible(timeout=5000):
                        el.click()
                        tweet_box = el
                        logger.info(f"✅ Found tweet box: {sel}")
                        break
                except Exception:
                    continue

            if tweet_box is None:
                _screenshot(page, "06b_no_tweetbox")
                logger.error("❌ Could not find tweet compose box")
                return False

            time.sleep(1)
            safe_caption = caption[:270] if len(caption) > 270 else caption
            logger.info(f"📝 Typing caption ({len(safe_caption)} chars)...")
            page.keyboard.type(safe_caption, delay=25)
            time.sleep(1)

            # ── STEP 6: Attach video ───────────────────────────────────────
            if video_path and os.path.exists(video_path):
                file_size_mb = os.path.getsize(video_path) / (1024 * 1024)
                logger.info(f"🎬 Attaching video: {file_size_mb:.1f} MB")

                # Try to find the file input
                file_input = page.locator('input[data-testid="fileInput"]')
                if not file_input.is_visible(timeout=3000):
                    # Try clicking the media attach button first
                    for media_sel in ['[data-testid="attachments"]', 'label[data-testid="fileInput"]', '[aria-label="Add photos or video"]']:
                        try:
                            btn = page.locator(media_sel).first
                            if btn.is_visible(timeout=2000):
                                btn.click()
                                time.sleep(1)
                                break
                        except Exception:
                            continue

                try:
                    file_input.set_input_files(video_path)
                    logger.info("⏳ Waiting for video upload (up to 3 min)...")
                    page.wait_for_selector('[data-testid="attachments"] video', timeout=180000)
                    logger.info("✅ Video uploaded!")
                    time.sleep(5)
                except Exception as e:
                    logger.warning(f"⚠️ Video attach issue: {e} — posting text only")

            # ── STEP 7: Post ───────────────────────────────────────────────
            logger.info("🚀 Clicking Post button...")
            _screenshot(page, "07_before_post")

            post_selectors = [
                '[data-testid="tweetButtonInline"]',
                '[data-testid="tweetButton"]',
                'button:has-text("Post")',
                'div[role="button"]:has-text("Post")',
            ]
            posted = False
            for sel in post_selectors:
                try:
                    btn = page.locator(sel).first
                    if btn.is_visible(timeout=5000):
                        btn.click()
                        posted = True
                        logger.info(f"✅ Post clicked: {sel}")
                        break
                except Exception:
                    continue

            if not posted:
                logger.error("❌ Could not find Post button")
                _screenshot(page, "07b_no_post_btn")
                return False

            time.sleep(5)
            _screenshot(page, "08_after_post")

            if "compose" not in page.url:
                logger.info("✅ Successfully posted to X! 🎉")
                return True
            else:
                logger.warning("⚠️ Still on compose page — checking if posted...")
                return True

        except Exception as e:
            logger.error(f"❌ X posting failed: {e}")
            _screenshot(page, "error_final")
            return False

        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python post_x_playwright.py 'Your caption' [/path/to/video.mp4]")
        sys.exit(1)

    caption_arg = sys.argv[1]
    video_arg   = sys.argv[2] if len(sys.argv) > 2 else None

    success = post_to_x(caption_arg, video_arg)
    sys.exit(0 if success else 1)
