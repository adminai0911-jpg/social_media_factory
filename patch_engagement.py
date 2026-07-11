import sys

with open('engagement_bot.py', 'r', encoding='utf-8') as f:
    code = f.read()

# We will completely replace engagement_bot.py with an Omni-Channel version.
omni_code = """import os
import requests
import json
import logging
import time
from dotenv import load_dotenv
from google import genai

logging.basicConfig(level=logging.INFO, format='%(asctime)s - OMNI_ENGAGEMENT_BOT - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

FB_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID")
IG_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID")
META_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")

GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

def generate_reply(comment_text, platform):
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        prompt = f'''
        You are a highly successful Indian financial influencer.
        A fan just left this comment on your latest {platform} video about wealth building:
        "{comment_text}"
        
        Write a short, friendly, and appreciative reply (under 150 characters).
        Keep it conversational and natural. Do NOT sound like a robot.
        If appropriate, kindly mention: "Don't forget to follow for more daily value!"
        
        System prompt:
        You are Wealth Matrix AI. Reply to this comment in a helpful, friendly, and engaging way. Keep it under 2 sentences. Include an emoji.
        '''
        response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini reply generation failed: {e}")
        return "Thanks for watching! 🙌 Don't forget to follow for more daily value!"

# ==========================================
# YOUTUBE
# ==========================================
def get_yt_access_token():
    res = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": YOUTUBE_CLIENT_ID,
        "client_secret": YOUTUBE_CLIENT_SECRET,
        "refresh_token": YOUTUBE_REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }, timeout=10).json()
    return res.get("access_token")

def run_youtube_bot():
    if not all([YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN]):
        logger.warning("Missing YouTube credentials. Skipping YT.")
        return
    access_token = get_yt_access_token()
    if not access_token: return
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    
    channel_res = requests.get("https://www.googleapis.com/youtube/v3/channels?part=contentDetails,id&mine=true", headers=headers, timeout=10).json()
    channel_id = channel_res["items"][0]["id"]
    uploads_list_id = channel_res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    playlist_res = requests.get(f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_list_id}&maxResults=1", headers=headers, timeout=10).json()
    if not playlist_res.get("items"): return
    latest_video_id = playlist_res["items"][0]["snippet"]["resourceId"]["videoId"]
    
    comments_url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId={latest_video_id}&maxResults=20"
    comments_res = requests.get(comments_url, headers=headers, timeout=10).json()
    if "items" not in comments_res: return
        
    replied_count = 0
    for item in comments_res["items"]:
        if replied_count >= 3: break
        top_comment = item["snippet"]["topLevelComment"]["snippet"]
        comment_id = item["snippet"]["topLevelComment"]["id"]
        author_channel_id = top_comment.get("authorChannelId", {}).get("value", "")
        comment_text = top_comment.get("textOriginal", "")
        if author_channel_id == channel_id: continue
            
        already_replied = False
        if item["snippet"]["totalReplyCount"] > 0 and "replies" in item:
            for reply in item["replies"]["comments"]:
                if reply["snippet"].get("authorChannelId", {}).get("value", "") == channel_id:
                    already_replied = True
                    break
        if already_replied: continue
            
        reply_text = generate_reply(comment_text, "YouTube Shorts")
        reply_payload = {"snippet": {"parentId": comment_id, "textOriginal": reply_text}}
        post_url = "https://www.googleapis.com/youtube/v3/comments?part=snippet"
        post_res = requests.post(post_url, headers=headers, json=reply_payload, timeout=10)
        if post_res.status_code in [200, 201]:
            logger.info(f"✅ YT Reply posted to '{comment_text[:20]}'")
            replied_count += 1
            time.sleep(2)

# ==========================================
# FACEBOOK
# ==========================================
def run_facebook_bot():
    if not all([FB_PAGE_ID, META_ACCESS_TOKEN]):
        logger.warning("Missing Facebook credentials. Skipping FB.")
        return
    url = f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/published_posts?fields=id,comments{{id,message,from,comments}}&limit=1&access_token={META_ACCESS_TOKEN}"
    res = requests.get(url, timeout=10).json()
    if "data" not in res or not res["data"]: return
    
    post = res["data"][0]
    comments = post.get("comments", {}).get("data", [])
    replied_count = 0
    for comment in comments:
        if replied_count >= 3: break
        if comment.get("from", {}).get("id") == FB_PAGE_ID: continue # own comment
        
        # Check if already replied
        already_replied = False
        if "comments" in comment:
            for sub in comment["comments"]["data"]:
                if sub.get("from", {}).get("id") == FB_PAGE_ID:
                    already_replied = True
                    break
        if already_replied: continue
        
        reply_text = generate_reply(comment.get("message", ""), "Facebook Reels")
        post_url = f"https://graph.facebook.com/v19.0/{comment['id']}/comments"
        post_res = requests.post(post_url, data={"message": reply_text, "access_token": META_ACCESS_TOKEN}, timeout=10)
        if post_res.status_code == 200:
            logger.info(f"✅ FB Reply posted to '{comment.get('message', '')[:20]}'")
            replied_count += 1
            time.sleep(2)

# ==========================================
# INSTAGRAM
# ==========================================
def run_instagram_bot():
    if not all([IG_ACCOUNT_ID, META_ACCESS_TOKEN]):
        logger.warning("Missing Instagram credentials. Skipping IG.")
        return
    url = f"https://graph.facebook.com/v19.0/{IG_ACCOUNT_ID}/media?fields=id,comments{{id,text,username,replies}}&limit=1&access_token={META_ACCESS_TOKEN}"
    res = requests.get(url, timeout=10).json()
    if "data" not in res or not res["data"]: return
    
    media = res["data"][0]
    comments = media.get("comments", {}).get("data", [])
    replied_count = 0
    for comment in comments:
        if replied_count >= 3: break
        # Note: 'username' is the person who commented. Can't easily check our own ID here without an extra call,
        # but replies are nested under 'replies'.
        already_replied = False
        if "replies" in comment:
            # If there's any reply, assume we replied (simplification to avoid self-reply loop if we can't get our own username)
            if len(comment["replies"]["data"]) > 0:
                already_replied = True
        if already_replied: continue
        
        reply_text = generate_reply(comment.get("text", ""), "Instagram Reels")
        post_url = f"https://graph.facebook.com/v19.0/{comment['id']}/replies"
        post_res = requests.post(post_url, data={"message": reply_text, "access_token": META_ACCESS_TOKEN}, timeout=10)
        if post_res.status_code == 200:
            logger.info(f"✅ IG Reply posted to '{comment.get('text', '')[:20]}'")
            replied_count += 1
            time.sleep(2)

if __name__ == "__main__":
    logger.info("Starting OMNI-CHANNEL Engagement Bot...")
    if not GEMINI_KEY:
        logger.error("Missing GEMINI_API_KEY. Exiting.")
        exit(1)
        
    try:
        run_youtube_bot()
    except Exception as e: logger.error(f"YT error: {e}")
    
    try:
        run_facebook_bot()
    except Exception as e: logger.error(f"FB error: {e}")
    
    try:
        run_instagram_bot()
    except Exception as e: logger.error(f"IG error: {e}")
    
    logger.info("Engagement Bot run complete.")
"""

with open('engagement_bot.py', 'w', encoding='utf-8') as f:
    f.write(omni_code)
print("Omni-Channel Engagement Bot written successfully.")
