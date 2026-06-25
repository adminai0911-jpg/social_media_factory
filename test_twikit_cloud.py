import asyncio
import httpx
from twikit import Client

async def get_ct0(auth_token):
    cookies = {'auth_token': auth_token}
    async with httpx.AsyncClient(cookies=cookies) as client:
        # Just hitting the homepage is enough to get a new ct0 in the set-cookie headers
        res = await client.get("https://x.com")
        ct0 = res.cookies.get("ct0")
        return ct0

async def main():
    auth_token = "5b1db4f0fedd6b43204896fdb2f6c1553d7e0ff9"
    ct0 = await get_ct0(auth_token)
    if not ct0:
        print("❌ Failed to get ct0")
        return
        
    print(f"✅ Got ct0: {ct0[:10]}...")
    
    client = Client('en-US')
    client.set_cookies({
        'auth_token': auth_token,
        'ct0': ct0
    })
    
    import urllib.request
    dummy_video = "dummy_twikit.mp4"
    urllib.request.urlretrieve("https://www.w3schools.com/html/mov_bbb.mp4", dummy_video)
    
    try:
        print("⏳ Uploading MP4 via twikit...")
        media_id = await client.upload_media(
            dummy_video, 
            media_category='tweet_video',
            wait_for_completion=True
        )
        print(f"✅ Video uploaded! Media ID: {media_id}")
        
        print("⏳ Posting tweet...")
        tweet = await client.create_tweet(
            text="Testing Twikit Cloud Upload! 🚀", 
            media_ids=[media_id]
        )
        print("🎉 SUCCESS! Tweet has been posted via twikit.")
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())
