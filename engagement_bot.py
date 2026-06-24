import os
import requests
import json
import logging
from dotenv import load_dotenv
from google import genai

logging.basicConfig(level=logging.INFO, format='%(asctime)s - ENGAGEMENT_BOT - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# Configuration
CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

AFFILIATE_LINK = os.environ.get("AFFILIATE_LINK", "https://groww.in")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, GEMINI_KEY]):
    logger.error("Missing required environment variables for Engagement Bot.")
    exit(1)

def get_access_token():
    token_url = "https://oauth2.googleapis.com/token"
    res = requests.post(token_url, data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    }, timeout=10).json()
    return res.get("access_token")

def generate_reply(comment_text):
    """Use Gemini to generate an engaging, contextual reply."""
    try:
        client = genai.Client(api_key=GEMINI_KEY)
        prompt = f"""
        You are a highly successful Indian financial influencer.
        A fan just left this comment on your latest YouTube Shorts video about wealth building:
        "{comment_text}"
        
        Write a short, friendly, and appreciative reply (under 150 characters).
        Keep it conversational and natural. Do NOT sound like a robot.
        If appropriate, kindly mention: "Check out the free Demat link in the bio to get started!"
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Gemini reply generation failed: {e}")
        return "Thanks for watching! 🙌 Check out the link in the bio to start your wealth journey."

def run_bot():
    access_token = get_access_token()
    if not access_token:
        logger.error("Could not obtain YouTube access token.")
        return
        
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    # 1. Get Channel ID
    channel_res = requests.get("https://www.googleapis.com/youtube/v3/channels?part=contentDetails,id&mine=true", headers=headers, timeout=10).json()
    channel_id = channel_res["items"][0]["id"]
    uploads_list_id = channel_res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    
    # 2. Get latest video
    playlist_res = requests.get(f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_list_id}&maxResults=1", headers=headers, timeout=10).json()
    if not playlist_res.get("items"):
        logger.info("No videos found on channel.")
        return
        
    latest_video_id = playlist_res["items"][0]["snippet"]["resourceId"]["videoId"]
    logger.info(f"Targeting Latest Video ID: {latest_video_id}")
    
    # 3. Get comments
    comments_url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet,replies&videoId={latest_video_id}&maxResults=20"
    comments_res = requests.get(comments_url, headers=headers, timeout=10).json()
    
    if "items" not in comments_res:
        logger.info("No comments found on the latest video.")
        return
        
    replied_count = 0
    for item in comments_res["items"]:
        if replied_count >= 5:  # Only reply to max 5 comments per run to look natural
            break
            
        top_comment = item["snippet"]["topLevelComment"]["snippet"]
        comment_id = item["snippet"]["topLevelComment"]["id"]
        author_channel_id = top_comment.get("authorChannelId", {}).get("value", "")
        comment_text = top_comment.get("textOriginal", "")
        
        # Skip our own comments
        if author_channel_id == channel_id:
            continue
            
        # Check if we already replied
        total_reply_count = item["snippet"]["totalReplyCount"]
        already_replied = False
        if total_reply_count > 0 and "replies" in item:
            for reply in item["replies"]["comments"]:
                if reply["snippet"].get("authorChannelId", {}).get("value", "") == channel_id:
                    already_replied = True
                    break
                    
        if already_replied:
            continue
            
        # Generate and post reply
        logger.info(f"Found new comment: '{comment_text}'")
        reply_text = generate_reply(comment_text)
        logger.info(f"Generated reply: '{reply_text}'")
        
        reply_payload = {
            "snippet": {
                "parentId": comment_id,
                "textOriginal": reply_text
            }
        }
        
        post_url = "https://www.googleapis.com/youtube/v3/comments?part=snippet"
        post_res = requests.post(post_url, headers=headers, json=reply_payload, timeout=10)
        
        if post_res.status_code in [200, 201]:
            logger.info("✅ Reply posted successfully.")
            replied_count += 1
        else:
            logger.error(f"❌ Failed to post reply: {post_res.status_code} - {post_res.text}")

if __name__ == "__main__":
    logger.info("Starting YouTube Engagement Bot...")
    run_bot()
    logger.info("Engagement Bot run complete.")
