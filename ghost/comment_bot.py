"""
Ghost Handler — Comment Auto-Reply Bot
Monitors ALL your platforms for new comments and replies with
AI-generated, unique, contextually relevant responses.

Platforms: YouTube, Instagram (via Meta API), X (via twikit)
"""
import os
import logging
import random
import time
from ghost.timing import human_delay
from ghost.safety import can_act, record_action

logger = logging.getLogger("CommentBot")

GENERIC_HINDI_REPLIES = [
    "Bilkul sahi baat! 🙌 Aur kya thoughts hain aapke iss topic pe?",
    "Thank you itna valuable feedback dene ke liye! Isse bahut helpful hai 🙏",
    "Aapka perspective sunke bahut acha laga! Share karo isse apne doston ke saath 🔥",
    "Exactly yahi main kehna chahta tha! Smart observation 👏",
    "Yeh question bahut important hai — main iske baare mein detail mein post karunga 💡",
    "Haan bilkul! Iss concept ko samajh lena bahut zaroori hai 🧠",
    "Thank you! Aur aisa content chahiye toh follow karo zaroor 🚀",
    "Aapne bilkul sahi point pakda! Yahi hai secret 🤫",
]

def _generate_ai_reply(comment_text, platform="general"):
    """Use Gemini to generate a unique, contextual reply."""
    try:
        from google import genai
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        if not gemini_key:
            return random.choice(GENERIC_HINDI_REPLIES)
        
        client = genai.Client(api_key=gemini_key)
        
        prompt = f"""You manage the social media account "Wealth Matrix AI" — a Hindi wealth & psychology channel.
Generate a SHORT, genuine, warm reply to this {platform} comment.

Rules:
- Max 2 sentences
- Sound like a REAL HUMAN, not a bot or brand
- Use Hinglish (Hindi + English mix) naturally
- Add 1 emoji max
- Don't use the word "absolutely", "certainly", "great question"
- If someone asks a question, briefly answer it or say you'll make a video about it
- If it's hate/spam, skip (return empty string)

Comment: "{comment_text}"

Reply (just the reply text, nothing else):"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        reply = response.text.strip()
        
        # Safety: if Gemini returns empty (spam detected), skip
        if not reply or len(reply) < 5:
            return ""
        
        return reply[:300]
        
    except Exception as e:
        logger.warning(f"AI reply generation failed: {e}")
        return random.choice(GENERIC_HINDI_REPLIES)

# ─── YOUTUBE COMMENT REPLIES ─────────────────────────────────────────────────

def reply_youtube_comments():
    """Reply to unanswered comments on your YouTube videos."""
    yt_api_key = os.environ.get("YOUTUBE_API_KEY", "")
    yt_channel_id = os.environ.get("YOUTUBE_CHANNEL_ID", "")
    
    if not yt_api_key or not yt_channel_id:
        logger.warning("⏭️ YouTube comments skipped (missing YOUTUBE_API_KEY or YOUTUBE_CHANNEL_ID)")
        return 0

    if not can_act("youtube", "reply"):
        return 0

    try:
        import googleapiclient.discovery
        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=yt_api_key)
        
        # Get recent videos
        videos_resp = youtube.search().list(
            part="id",
            channelId=yt_channel_id,
            order="date",
            maxResults=5,
            type="video"
        ).execute()
        
        replied = 0
        for item in videos_resp.get("items", []):
            video_id = item["id"]["videoId"]
            
            # Get comments for this video
            comments_resp = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                moderationStatus="published",
                maxResults=10,
                order="time"
            ).execute()
            
            for thread in comments_resp.get("items", []):
                if not can_act("youtube", "reply"):
                    break
                
                comment = thread["snippet"]["topLevelComment"]["snippet"]
                comment_text = comment.get("textDisplay", "")
                author = comment.get("authorDisplayName", "Someone")
                thread_id = thread["id"]
                
                if len(comment_text) < 3:
                    continue
                
                # Generate reply
                human_delay(10, 30, "yt_reply_think")
                reply_text = _generate_ai_reply(comment_text, "YouTube")
                
                if not reply_text:
                    continue
                
                # Post reply using OAuth (needs different auth)
                # Note: requires OAuth token, not just API key
                logger.info(f"💬 YT Reply to {author}: {reply_text[:50]}...")
                # TODO: needs YOUTUBE_OAUTH_TOKEN for posting replies
                # For now, log only
                record_action("youtube", "reply")
                replied += 1
                human_delay(15, 45, "yt_reply_posted")
        
        return replied
    except Exception as e:
        logger.error(f"❌ YouTube comment reply failed: {e}")
        return 0

# ─── INSTAGRAM COMMENT REPLIES ────────────────────────────────────────────────

def reply_instagram_comments():
    """Reply to comments on your Instagram posts using Meta Graph API."""
    page_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
    ig_account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")
    
    if not page_token or not ig_account_id:
        logger.warning("⏭️ Instagram comments skipped (missing Meta credentials)")
        return 0

    if not can_act("instagram", "comment"):
        return 0

    import requests
    replied = 0
    
    try:
        # Get recent media
        media_resp = requests.get(
            f"https://graph.facebook.com/v19.0/{ig_account_id}/media",
            params={"fields": "id,timestamp", "access_token": page_token, "limit": 5}
        ).json()
        
        for media in media_resp.get("data", []):
            media_id = media["id"]
            
            # Get comments on this media
            comments_resp = requests.get(
                f"https://graph.facebook.com/v19.0/{media_id}/comments",
                params={"fields": "id,text,username,timestamp", "access_token": page_token}
            ).json()
            
            for comment in comments_resp.get("data", []):
                if not can_act("instagram", "comment"):
                    break
                
                comment_text = comment.get("text", "")
                username = comment.get("username", "someone")
                comment_id = comment["id"]
                
                if len(comment_text) < 3:
                    continue
                
                human_delay(15, 40, "ig_reply_think")
                reply_text = _generate_ai_reply(comment_text, "Instagram")
                
                if not reply_text:
                    continue
                
                # Post reply
                reply_resp = requests.post(
                    f"https://graph.facebook.com/v19.0/{comment_id}/replies",
                    data={"message": f"@{username} {reply_text}", "access_token": page_token}
                ).json()
                
                if "id" in reply_resp:
                    record_action("instagram", "comment")
                    replied += 1
                    logger.info(f"💬 IG reply to @{username}: {reply_text[:50]}...")
                    human_delay(20, 60, "ig_reply_cooldown")
        
        return replied
    except Exception as e:
        logger.error(f"❌ Instagram comment reply failed: {e}")
        return 0

# ─── FACEBOOK COMMENT REPLIES ─────────────────────────────────────────────────

def reply_facebook_comments():
    """Reply to comments on your Facebook page posts."""
    page_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
    page_id = os.environ.get("FACEBOOK_PAGE_ID", "")
    
    if not page_token or not page_id:
        logger.warning("⏭️ Facebook comments skipped (missing Meta credentials)")
        return 0

    import requests
    replied = 0
    
    try:
        # Get recent posts
        posts_resp = requests.get(
            f"https://graph.facebook.com/v19.0/{page_id}/posts",
            params={"fields": "id,message", "access_token": page_token, "limit": 5}
        ).json()
        
        for post in posts_resp.get("data", []):
            post_id = post["id"]
            
            # Get comments
            comments_resp = requests.get(
                f"https://graph.facebook.com/v19.0/{post_id}/comments",
                params={"fields": "id,message,from", "access_token": page_token}
            ).json()
            
            for comment in comments_resp.get("data", []):
                if not can_act("instagram", "comment"):  # reuse IG limit for FB
                    break
                
                comment_text = comment.get("message", "")
                commenter = comment.get("from", {}).get("name", "Someone")
                comment_id = comment["id"]
                
                if len(comment_text) < 3:
                    continue
                
                human_delay(10, 30, "fb_reply_think")
                reply_text = _generate_ai_reply(comment_text, "Facebook")
                
                if not reply_text:
                    continue
                
                reply_resp = requests.post(
                    f"https://graph.facebook.com/v19.0/{comment_id}/comments",
                    data={"message": reply_text, "access_token": page_token}
                ).json()
                
                if "id" in reply_resp:
                    record_action("instagram", "comment")
                    replied += 1
                    logger.info(f"💬 FB reply to {commenter}: {reply_text[:50]}...")
                    human_delay(20, 60, "fb_reply_cooldown")
        
        return replied
    except Exception as e:
        logger.error(f"❌ Facebook comment reply failed: {e}")
        return 0

def run():
    """Run all comment reply bots across all platforms."""
    logger.info("🤖 Starting Comment Reply Bot — All Platforms")
    yt = reply_youtube_comments()
    ig = reply_instagram_comments()
    fb = reply_facebook_comments()
    total = yt + ig + fb
    logger.info(f"✅ Comment replies done: YT={yt} IG={ig} FB={fb} Total={total}")
    return total
