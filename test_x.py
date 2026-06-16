import os
import requests
import time
from requests_oauthlib import OAuth1
from dotenv import load_dotenv

load_dotenv()

TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET", "")

def test_x_upload():
    auth = OAuth1(TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    
    print("Testing v1.1 upload and tweet...")
    # 1. Init
    upload_url = "https://upload.twitter.com/1.1/media/upload.json"
    dummy_file = "dummy_x.mp4"
    with open(dummy_file, "wb") as f:
        f.write(b"dummy") # not a real video, but enough to get an error or media id for text post
        
    # let's just do a text tweet with v1.1 to see if we have access
    print("Trying v1.1 text post...")
    v1_url = "https://api.twitter.com/1.1/statuses/update.json"
    res = requests.post(v1_url, auth=auth, data={"status": "Testing v1.1 API fallback for X posting"})
    print("v1.1 POST status:", res.status_code)
    print("v1.1 POST response:", res.text)
    
    print("\nTrying v2 text post...")
    v2_url = "https://api.twitter.com/2/tweets"
    res2 = requests.post(v2_url, auth=auth, json={"text": "Testing v2 API for X posting"})
    print("v2 POST status:", res2.status_code)
    print("v2 POST response:", res2.text)

if __name__ == "__main__":
    test_x_upload()
