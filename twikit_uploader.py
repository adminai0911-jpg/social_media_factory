import os
import asyncio
import time
import random
import httpx
from twikit import Client

async def get_ct0(auth_token):
    print("⚠️ WARNING: Fetching CT0 dynamically. This can flag GitHub IPs as bots!")
    cookies = {'auth_token': auth_token}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    async with httpx.AsyncClient(cookies=cookies, headers=headers, follow_redirects=True) as client:
        res = await client.get("https://x.com")
        return res.cookies.get("ct0")

async def upload_via_twikit_async(auth_token, ct0_env, video_path, caption):
    print("🤖 Launching Stealth Twikit X Uploader...")
    
    # Use explicitly provided CT0 if available (100% immune to IP scraping flags)
    ct0 = ct0_env
    if not ct0:
        ct0 = await get_ct0(auth_token)
        
    if not ct0:
        print("❌ Failed to get CT0 from X.com")
        return False
        
    client = Client('en-US')
    client.set_cookies({
        'auth_token': auth_token,
        'ct0': ct0
    })
    
    try:
        print("⏳ Uploading MP4 via twikit internal API...")
        media_id = await client.upload_media(
            video_path, 
            media_category='tweet_video',
            wait_for_completion=True
        )
        print(f"✅ Video uploaded! Media ID: {media_id}")
        
        # Jitter to simulate human behavior
        sleep_time = random.uniform(3.5, 7.2)
        print(f"😴 Waiting {sleep_time:.1f}s to look human before posting...")
        await asyncio.sleep(sleep_time)
        
        print("⏳ Posting tweet...")
        tweet = await client.create_tweet(
            text=caption, 
            media_ids=[media_id]
        )
        print("🎉 SUCCESS! Tweet has been posted via twikit stealth mode.")
        return True
    except Exception as e:
        print(f"❌ Twikit upload FAILED: {e}")
        return False

def upload_to_x_twikit(video_path, caption):
    from dotenv import load_dotenv
    load_dotenv()
    auth_token = os.environ.get("X_AUTH_TOKEN")
    ct0_env = os.environ.get("X_CT0")
    
    if not auth_token:
        print("⏭️ Skipping X upload: X_AUTH_TOKEN missing in .env")
        return False
    return asyncio.run(upload_via_twikit_async(auth_token, ct0_env, video_path, caption))
