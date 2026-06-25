import asyncio
import os
from playwright.async_api import async_playwright

async def post_to_x(auth_token, video_path, caption="Just testing my video upload! 🎥"):
    print("🚀 Launching invisible Ghost Browser (Chromium)...")
    async with async_playwright() as p:
        # Launch headless browser
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Inject the authentication cookie
        await context.add_cookies([{
            "name": "auth_token",
            "value": auth_token,
            "domain": ".x.com",
            "path": "/"
        }, {
            "name": "auth_token",
            "value": auth_token,
            "domain": ".twitter.com",
            "path": "/"
        }])

        page = await context.new_page()
        
        print("🌐 Navigating to X.com...")
        await page.goto("https://x.com/compose/tweet", wait_until="domcontentloaded", timeout=60000)
        
        # Wait for the page to fully render the compose window
        await asyncio.sleep(5)
        
        # Check if we are logged in
        if "/login" in page.url:
            print("❌ FAILED: Invalid auth_token. Browser redirected to login.")
            await browser.close()
            return
            
        print("✅ Logged in successfully!")

        print("⏳ Uploading video file...")
        try:
            # Wait for compose window to be ready
            file_input = page.locator("input[data-testid='fileInput']").first
            await file_input.wait_for(state="attached", timeout=15000)
            await file_input.set_input_files(video_path)
            
            # Wait for video to process (X takes a moment to upload the mp4)
            print("⏳ Waiting for X to process the video (20 seconds)...")
            await asyncio.sleep(20)  

            print("✍️ Typing caption...")
            # Type the tweet text
            await page.locator("div[data-testid='tweetTextarea_0']").first.fill(caption)
            
            print("📨 Clicking Post button...")
            # Click the Post button
            post_button = page.locator("button[data-testid='tweetButton']")
            await post_button.wait_for(state="visible", timeout=15000)
            await post_button.click(force=True)
            
            # Wait for the post to send
            await asyncio.sleep(5)
            print("🎉 SUCCESS! Video posted to X like a real human.")
            
        except Exception as e:
            print("📸 Taking screenshot of what the browser sees...")
            await page.screenshot(path="C:\\Users\\drsau\\.gemini\\antigravity\\brain\\5dfd51bc-3fc9-462b-aa07-48e0b52453f1\\ghost_browser.png")
            html = await page.content()
            with open("C:\\Users\\drsau\\.gemini\\antigravity\\brain\\5dfd51bc-3fc9-462b-aa07-48e0b52453f1\\twitter_dom.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"❌ FAILED: {str(e)}")
            raise e

        await browser.close()

def upload_to_x_sync(video_path, caption):
    from dotenv import load_dotenv
    load_dotenv()
    auth_token = os.environ.get("X_AUTH_TOKEN")
    if not auth_token:
        print("⏭️ Skipping X (Twitter) upload: X_AUTH_TOKEN not found in .env")
        return False
    try:
        asyncio.run(post_to_x(auth_token, video_path, caption))
        return True
    except Exception as e:
        print(f"❌ X Upload failed: {e}")
        return False

if __name__ == "__main__":
    import urllib.request
    
    print("=" * 50)
    print("GHOST BROWSER X UPLOADER")
    print("=" * 50)
    auth_token = "5b1db4f0fedd6b43204896fdb2f6c1553d7e0ff9"
    
    if not os.path.exists("dummy_video.mp4"):
        print("⏳ Downloading tiny test video...")
        urllib.request.urlretrieve("https://www.w3schools.com/html/mov_bbb.mp4", "dummy_video.mp4")
        
    caption = "Just testing my video upload! 🎥"
    
    asyncio.run(post_to_x(auth_token, "dummy_video.mp4", caption))
