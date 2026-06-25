import os
import sys
import asyncio
from twikit import Client
import urllib.request

async def test_upload():
    print("="*50)
    print("TWITTER NATIVE VIDEO UPLOAD TESTER")
    print("="*50)
    
    auth_token = "5b1db4f0fedd6b43204896fdb2f6c1553d7e0ff9"
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies([{"name": "auth_token", "value": auth_token, "domain": ".x.com", "path": "/"}])
        page = await context.new_page()
        await page.goto("https://x.com")
        cookies = await context.cookies()
        ct0 = next((c['value'] for c in cookies if c['name'] == 'ct0'), None)
        await browser.close()
        
    if not ct0:
        print("❌ Could not get CT0 token.")
        return
        
    print(f"✅ Fetched CT0: {ct0[:10]}...")
    client = Client('en-US')
    client.set_cookies({
        'auth_token': auth_token,
        'ct0': ct0
    })
    
    dummy_video = "dummy_test_video.mp4"
    print("\n⏳ Downloading a tiny 2-second dummy video for the test...")
    urllib.request.urlretrieve("https://www.w3schools.com/html/mov_bbb.mp4", dummy_video)
    
    print("⏳ Uploading MP4 to X (Waiting for Twitter processing)...")
    try:
        media_id = await client.upload_media(
            dummy_video, 
            media_category='tweet_video',
            wait_for_completion=True
        )
        print(f"✅ Video uploaded successfully! Media ID: {media_id}")
        
        print("⏳ Posting tweet...")
        tweet = await client.create_tweet(
            text="Testing the new native video uploader! 🚀", 
            media_ids=[media_id]
        )
        print("✅ SUCCESS! Tweet has been posted successfully.")
        print(f"Check your X timeline!")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        
if __name__ == "__main__":
    asyncio.run(test_upload())
