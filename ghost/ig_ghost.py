"""
Ghost Handler — Instagram Proactive Engine
Uses instagrapi to proactively like, follow, and comment on niche hashtags to drive traffic.
VERY strict limits are placed to avoid Meta bans.
"""
import os
import logging
import random
from ghost.timing import human_delay, micro_pause
from ghost.safety import can_act, record_action

logger = logging.getLogger("IGGhost")

NICHE_HASHTAGS = [
    "wealthmindset", "stockmarketindia", "financialfreedom",
    "businesshindi", "startupindia", "motivationhindi",
    "psychologyfacts", "investingindia"
]

def _get_client():
    """Authenticate with instagrapi using username and password."""
    try:
        from instagrapi import Client
        username = os.environ.get("IG_USERNAME", "")
        password = os.environ.get("IG_PASSWORD", "")
        
        if not username or not password:
            logger.warning("❌ IG_USERNAME or IG_PASSWORD missing! Cannot run proactive IG engine.")
            return None
            
        cl = Client()
        human_delay(5, 10, "ig_pre_login")
        cl.login(username, password)
        logger.info("✅ Instagram Client Authenticated (instagrapi)")
        return cl
    except Exception as e:
        logger.error(f"❌ IG Login Failed: {e}")
        return None

def _generate_ig_hook(caption_text):
    """Generate an AI hook comment for an Instagram Reel/Post."""
    try:
        from google import genai
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        if not gemini_key:
            return "Bahut khoob! 🔥"
            
        client = genai.Client(api_key=gemini_key)
        prompt = f"""You are 'Wealth Matrix AI', an Indian social media page.
Write a SHORT, valuable, insightful comment for this Instagram post/reel.
Goal: Make other users see your comment, think you are smart, and click your profile.
- 1 or 2 sentences max.
- Use Hinglish (Hindi + English).
- Do not sound like a bot. Sound like an expert adding value to the video.
- 1 emoji max.

Post Caption: "{caption_text}"

Comment (just the text):"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        reply = response.text.strip()
        if len(reply) < 3 or "{" in reply:
            return "Bilkul sahi baat! 🔥"
        return reply[:150]
    except Exception as e:
        logger.warning(f"AI IG comment failed: {e}")
        return "Great insights! 📈"

def run_ig_proactive_session(session="morning"):
    """
    Run proactive engagement on Instagram.
    Extremely limited actions to avoid bans.
    """
    logger.info(f"🤖 Starting IG Proactive Ghost Session: {session}")
    results = {"liked": [], "commented": [], "followed": []}
    
    if not can_act("instagram", "like"):
        logger.info("⏭️ IG daily limit reached. Skipping proactive session.")
        return results

    cl = _get_client()
    if not cl:
        return results

    try:
        hashtag = random.choice(NICHE_HASHTAGS)
        logger.info(f"🔍 IG Hunting under hashtag: #{hashtag}")
        
        medias = cl.hashtag_medias_top(hashtag, amount=10)
        random.shuffle(medias)
        
        likes_done = 0
        comments_done = 0
        
        for media in medias:
            if not can_act("instagram", "like") or likes_done >= 3:
                break
                
            try:
                human_delay(8, 20, "ig_read_post")
                cl.media_like(media.id)
                record_action("instagram", "like")
                likes_done += 1
                detail = f"#{hashtag} post by @{media.user.username}"
                results["liked"].append(detail)
                logger.info(f"❤️ IG Liked: {detail}")
                human_delay(15, 35, "ig_after_like")
                
                if comments_done < 1 and media.like_count > 100 and can_act("instagram", "comment"):
                    human_delay(30, 60, "ig_think_comment")
                    comment_text = _generate_ig_hook(media.caption_text)
                    cl.media_comment(media.id, comment_text)
                    record_action("instagram", "comment")
                    comments_done += 1
                    results["commented"].append(f"@{media.user.username}: \"{comment_text[:40]}...\"")
                    logger.info(f"💬 IG Commented on @{media.user.username}")
                    human_delay(40, 80, "ig_after_comment")
                    
            except Exception as e:
                logger.warning(f"IG engagement failed on media {media.id}: {e}")
                if "feedback_required" in str(e).lower() or "challenge" in str(e).lower():
                    logger.error("🛑 IG Action Blocked (Spam filter hit). Aborting IG session.")
                    break
                    
        logger.info(f"✅ IG Proactive Session complete: {results}")
        return results
        
    except Exception as e:
        logger.error(f"❌ IG Proactive Session crashed: {e}")
        return results
