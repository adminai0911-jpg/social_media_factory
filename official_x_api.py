import os
import time
import requests
from requests_oauthlib import OAuth1
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("X_API_KEY")
API_SECRET = os.environ.get("X_API_SECRET")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("X_ACCESS_SECRET")

def upload_video_to_x(video_path, caption):
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
        print("❌ Missing Official X API Keys in .env! Cannot upload.")
        return False
        
    print("📤 Starting Official X API Video Upload...")
    
    # 1. Setup OAuth1 Authentication
    auth = OAuth1(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
    
    total_bytes = os.path.getsize(video_path)
    
    # 2. INIT step
    print("⏳ INIT uploading session...")
    init_url = "https://upload.twitter.com/1.1/media/upload.json"
    init_data = {
        "command": "INIT",
        "total_bytes": total_bytes,
        "media_type": "video/mp4",
        "media_category": "tweet_video"
    }
    init_res = requests.post(init_url, data=init_data, auth=auth)
    if init_res.status_code not in (200, 202):
        print(f"❌ INIT failed: {init_res.text}")
        return False
        
    media_id = init_res.json()["media_id_string"]
    
    # 3. APPEND step (Upload chunks)
    print(f"⏳ APPEND uploading video chunks for media_id {media_id}...")
    chunk_size = 4 * 1024 * 1024 # 4MB
    segment_index = 0
    with open(video_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            append_data = {
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": segment_index
            }
            files = {"media": chunk}
            append_res = requests.post(init_url, data=append_data, files=files, auth=auth)
            if append_res.status_code not in (200, 202, 204):
                print(f"❌ APPEND failed on segment {segment_index}: {append_res.text}")
                return False
            segment_index += 1
            
    # 4. FINALIZE step
    print("⏳ FINALIZE uploading session...")
    finalize_data = {
        "command": "FINALIZE",
        "media_id": media_id
    }
    finalize_res = requests.post(init_url, data=finalize_data, auth=auth)
    if finalize_res.status_code not in (200, 201, 202):
        print(f"❌ FINALIZE failed: {finalize_res.text}")
        return False
        
    # Wait for processing
    print("⏳ Waiting for Twitter to process the video on their servers...")
    processing_info = finalize_res.json().get("processing_info", {})
    state = processing_info.get("state", "succeeded")
    
    while state in ["pending", "in_progress"]:
        sleep_secs = processing_info.get("check_after_secs", 5)
        print(f"   Video processing... checking again in {sleep_secs}s")
        time.sleep(sleep_secs)
        
        status_data = {
            "command": "STATUS",
            "media_id": media_id
        }
        status_res = requests.get(init_url, params=status_data, auth=auth)
        processing_info = status_res.json().get("processing_info", {})
        state = processing_info.get("state", "succeeded")
        if state == "failed":
            print(f"❌ Twitter processing failed: {status_res.text}")
            return False
            
    print("✅ Video processed successfully!")
    
    # 5. POST TWEET via V2 API
    print("⏳ Posting tweet with attached video...")
    tweet_url = "https://api.twitter.com/2/tweets"
    tweet_payload = {
        "text": caption,
        "media": {
            "media_ids": [media_id]
        }
    }
    tweet_res = requests.post(tweet_url, json=tweet_payload, auth=auth)
    
    if tweet_res.status_code in (200, 201):
        print("🎉 SUCCESS! Video posted to X using the Official API.")
        return True
    else:
        print(f"❌ TWEET failed: {tweet_res.text}")
        return False

if __name__ == "__main__":
    # Test script
    print("Ensure you have set X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET in your .env")
    upload_video_to_x("dummy_video.mp4", "Testing Official X API Video Upload 🚀")
