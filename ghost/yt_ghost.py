"""
Ghost Handler — YouTube Proactive Engine
Uses YouTube Data API (with OAuth) to proactively comment on niche videos.
"""
import os
import logging
import random
from ghost.timing import human_delay
from ghost.safety import can_act, record_action

logger = logging.getLogger("YTGhost")

NICHE_KEYWORDS = [
    "wealth mindset hindi", "stock market tips india", "financial freedom india",
    "startup motivation hindi", "psychology facts hindi", "investing basics hindi"
]

def _get_youtube_oauth():
    """Authenticate with YouTube Data API using OAuth Refresh Token."""
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    
    if not client_id or not refresh_token:
        logger.warning("❌ YouTube OAuth missing! Cannot run proactive YT engine.")
        return None
        
    try:
        import googleapiclient.discovery
        from google.oauth2.credentials import Credentials
        
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            token_uri="https://oauth2.googleapis.com/token"
        )
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
        return youtube
    except Exception as e:
        logger.error(f"❌ YouTube OAuth init failed: {e}")
        return None

def _generate_yt_hook(video_title):
    """Generate an AI hook comment for a YouTube video."""
    try:
        from google import genai
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        if not gemini_key:
            return "Bahut valuable video hai, thanks for sharing! 🔥"
            
        client = genai.Client(api_key=gemini_key)
        prompt = f"""You are 'Wealth Matrix AI', an Indian YouTube channel about wealth & psychology.
Write a SHORT, highly valuable, engaging comment for this YouTube video.
Goal: Add an insightful perspective so other viewers like your comment and check out your channel.
- 1 to 3 sentences max.
- Use Hinglish (Hindi + English).
- Do not sound like a spam bot ("sub to me", "great video"). Be specific to the topic.
- 1 emoji max.

Video Title: "{video_title}"

Comment (just the text):"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        reply = response.text.strip()
        if len(reply) < 3 or "{" in reply:
            return "Mind blowing perspective! 🙌"
        return reply[:250]
    except Exception as e:
        logger.warning(f"AI YT comment failed: {e}")
        return "Bahut achi video! 📈"

def run_yt_proactive_session(session="morning"):
    """
    Run proactive commenting on YouTube.
    Finds recent niche videos and leaves a high-value comment.
    """
    logger.info(f"🤖 Starting YT Proactive Ghost Session: {session}")
    results = {"commented": []}
    
    if not can_act("youtube", "comment"):
        logger.info("⏭️ YT daily limit reached. Skipping proactive session.")
        return results

    youtube = _get_youtube_oauth()
    if not youtube:
        return results

    try:
        keyword = random.choice(NICHE_KEYWORDS)
        logger.info(f"🔍 YT Hunting for videos: '{keyword}'")
        
        search_response = youtube.search().list(
            q=keyword,
            part="id,snippet",
            maxResults=20,
            order="date", # Get recent ones
            type="video"
        ).execute()
        
        videos = search_response.get("items", [])
        random.shuffle(videos)
        
        comments_done = 0
        
        for video in videos:
            if not can_act("youtube", "comment") or comments_done >= 5:
                break
                
            video_id = video["id"]["videoId"]
            title = video["snippet"]["title"]
            channel_title = video["snippet"]["channelTitle"]
            
            try:
                human_delay(15, 30, "yt_watch_video")
                comment_text = _generate_yt_hook(title)
                
                # Insert top-level comment
                request = youtube.commentThreads().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "videoId": video_id,
                            "topLevelComment": {
                                "snippet": {
                                    "textOriginal": comment_text
                                }
                            }
                        }
                    }
                )
                request.execute()
                
                record_action("youtube", "comment")
                comments_done += 1
                detail = f"On '{title[:30]}...' (by {channel_title}): \"{comment_text[:40]}...\""
                results["commented"].append(detail)
                logger.info(f"💬 YT Commented: {detail}")
                human_delay(40, 80, "yt_after_comment")
                
            except Exception as e:
                logger.warning(f"YT comment failed on video {video_id}: {e}")
                
        logger.info(f"✅ YT Proactive Session complete: {results}")
        return results
        
    except Exception as e:
        logger.error(f"❌ YT Proactive Session crashed: {e}")
        return results
