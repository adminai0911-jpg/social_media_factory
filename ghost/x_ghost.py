"""
Ghost Handler — X/Twitter Engine
Fully automated human-like engagement on X.
Uses cookie auth (twikit) — no API key needed.

Actions performed:
- Like posts in your niche (wealth, psychology, AI)
- Reply to mentions and comments
- Follow relevant accounts
- Retweet with added commentary
- Post viral threads
"""
import os
import asyncio
import logging
import random
from ghost.timing import human_delay, micro_pause, post_action_cooldown
from ghost.safety import can_act, record_action

logger = logging.getLogger("XGhost")

NICHE_KEYWORDS = [
    "wealth mindset", "psychology money", "AI tools free", 
    "brain hacks hindi", "financial freedom india",
    "passive income india", "stock market hindi",
    "self improvement hindi", "motivation hindi",
    "rich mindset poor mindset"
]

COMMENT_TEMPLATES = [
    "बिल्कुल सही कहा! यह बात और लोगों को भी पता होनी चाहिए 🔥",
    "यह perspective बदल देने वाला है। Share कर रहा हूँ अभी।",
    "Exactly! 99% लोग यही गलती करते हैं। Great insight 👏",
    "इसे save करके रखा — बहुत valuable है यह 💡",
    "Real talk! यही सोचता था but इतने clearly कभी नहीं समझा था।",
    "Bhai this is gold 🏆 Follow कर लिया — ऐसे ही content chahiye",
    "यह thread/post screenshot लेने वाली है seriously 📸",
    "Mind blown 🤯 इतना simple था but kabhi socha nahi",
]

async def _get_client():
    """Create an authenticated twikit client using cookies."""
    try:
        from twikit import Client
        auth_token = os.environ.get("X_AUTH_TOKEN", "")
        ct0 = os.environ.get("X_CT0", "")
        if not auth_token or not ct0:
            logger.error("❌ X_AUTH_TOKEN or X_CT0 missing!")
            return None
        client = Client("en-US")
        client.set_cookies({"auth_token": auth_token, "ct0": ct0})
        logger.info("✅ X client authenticated via cookies")
        return client
    except Exception as e:
        logger.error(f"❌ X client init failed: {e}")
        return None

async def like_niche_posts(max_likes=None):
    """Find and like posts in your niche — looks completely human."""
    if not can_act("x", "like"):
        return 0
    
    client = await _get_client()
    if not client:
        return 0

    limit = max_likes or random.randint(5, 10)
    liked = 0
    keyword = random.choice(NICHE_KEYWORDS)
    
    try:
        logger.info(f"🔍 Searching X for: '{keyword}'")
        results = await client.search_tweet(keyword, product="Latest", count=20)
        tweets = list(results)
        random.shuffle(tweets)
        
        for tweet in tweets[:limit]:
            if not can_act("x", "like"):
                break
            try:
                # Skip if already liked or if it's our own tweet
                if tweet.favorited:
                    continue
                micro_pause()
                await tweet.favorite()
                record_action("x", "like")
                liked += 1
                logger.info(f"❤️ Liked tweet by @{tweet.user.screen_name}: {tweet.text[:50]}...")
                human_delay(8, 25, "x_like")
            except Exception as e:
                if "rate limit" in str(e).lower() or "429" in str(e):
                    logger.warning("⚠️ X rate limit hit — stopping likes")
                    break
                logger.warning(f"Like failed: {e}")
        
        logger.info(f"✅ Liked {liked} posts on X")
        return liked
    except Exception as e:
        logger.error(f"❌ X like session failed: {e}")
        return liked

async def reply_to_mentions():
    """Find mentions/replies to your account and respond with AI."""
    if not can_act("x", "reply"):
        return 0

    client = await _get_client()
    if not client:
        return 0

    # Import Gemini for AI reply generation
    try:
        from google import genai
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        ai_client = genai.Client(api_key=gemini_key) if gemini_key else None
    except Exception:
        ai_client = None

    replied = 0
    try:
        notifications = await client.get_notifications(type="Mentions")
        
        for notif in list(notifications)[:5]:
            if not can_act("x", "reply"):
                break
            try:
                tweet = notif.tweet
                if not tweet or not tweet.text:
                    continue
                
                # Generate AI reply
                if ai_client:
                    reply_text = await _generate_x_reply(ai_client, tweet.text)
                else:
                    reply_text = random.choice(COMMENT_TEMPLATES)
                
                human_delay(15, 45, "x_reply_think")
                await client.create_tweet(text=reply_text, reply_to=tweet.id)
                record_action("x", "reply")
                replied += 1
                logger.info(f"💬 Replied to @{tweet.user.screen_name}")
                human_delay(20, 60, "x_reply_cooldown")
            except Exception as e:
                logger.warning(f"Reply failed: {e}")
        
        return replied
    except Exception as e:
        logger.error(f"❌ X reply session failed: {e}")
        return replied

async def _generate_x_reply(ai_client, original_tweet):
    """Generate a natural Hindi reply using Gemini."""
    try:
        prompt = f"""You are a friendly Indian social media user who posts about wealth, psychology, and AI.
Generate a SHORT, genuine, engaging Hindi reply to this tweet. 
- Max 2 sentences
- Sound like a real person, not a bot
- Add 1-2 relevant emojis
- No hashtags in replies
- Mix Hindi and English naturally (Hinglish is fine)

Tweet: "{original_tweet}"

Reply:"""
        response = ai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()[:250]
    except Exception:
        return random.choice(COMMENT_TEMPLATES)

async def follow_niche_accounts():
    """Follow relevant accounts in your niche — max 10/day."""
    if not can_act("x", "follow"):
        return 0

    client = await _get_client()
    if not client:
        return 0

    followed = 0
    keyword = random.choice(NICHE_KEYWORDS)
    
    try:
        results = await client.search_tweet(keyword, product="Top", count=15)
        accounts_seen = set()
        
        for tweet in list(results)[:15]:
            if not can_act("x", "follow"):
                break
            if tweet.user and tweet.user.screen_name not in accounts_seen:
                accounts_seen.add(tweet.user.screen_name)
                # Only follow accounts with some credibility
                if tweet.user.followers_count > 100:
                    try:
                        await tweet.user.follow()
                        record_action("x", "follow")
                        followed += 1
                        logger.info(f"➕ Followed @{tweet.user.screen_name} ({tweet.user.followers_count} followers)")
                        human_delay(20, 60, "x_follow")
                    except Exception as e:
                        logger.warning(f"Follow failed: {e}")
        
        return followed
    except Exception as e:
        logger.error(f"❌ X follow session failed: {e}")
        return followed

async def comment_on_viral_posts():
    """Leave genuine comments on viral posts in your niche."""
    if not can_act("x", "reply"):
        return 0

    client = await _get_client()
    if not client:
        return 0

    try:
        from google import genai
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        ai_client = genai.Client(api_key=gemini_key) if gemini_key else None
    except Exception:
        ai_client = None

    commented = 0
    keyword = random.choice(NICHE_KEYWORDS)
    
    try:
        results = await client.search_tweet(keyword, product="Top", count=10)
        
        for tweet in list(results)[:5]:
            if not can_act("x", "reply"):
                break
            # Only comment on posts with decent engagement
            if tweet.favorite_count > 50:
                try:
                    if ai_client:
                        comment = await _generate_x_reply(ai_client, tweet.text)
                    else:
                        comment = random.choice(COMMENT_TEMPLATES)
                    
                    human_delay(30, 90, "x_comment_think")
                    await client.create_tweet(text=comment, reply_to=tweet.id)
                    record_action("x", "reply")
                    commented += 1
                    logger.info(f"💬 Commented on viral tweet by @{tweet.user.screen_name}")
                    human_delay(45, 120, "x_comment_cooldown")
                except Exception as e:
                    logger.warning(f"Comment failed: {e}")
        
        return commented
    except Exception as e:
        logger.error(f"❌ X comment session failed: {e}")
        return commented

async def run_x_engagement_session(session="morning"):
    """
    Run a full X engagement session.
    
    morning:  Like posts + follow accounts
    midday:   Reply to mentions + comment on viral posts
    evening:  Like posts + reply to mentions
    """
    logger.info(f"🤖 Starting X Ghost Session: {session}")
    results = {"liked": 0, "replied": 0, "followed": 0, "commented": 0}
    
    if session == "morning":
        results["liked"] = await like_niche_posts(random.randint(5, 8))
        human_delay(60, 180, "between_x_actions")
        results["followed"] = await follow_niche_accounts()
        
    elif session == "midday":
        results["replied"] = await reply_to_mentions()
        human_delay(120, 300, "between_x_actions")
        results["commented"] = await comment_on_viral_posts()
        
    elif session == "evening":
        results["liked"] = await like_niche_posts(random.randint(8, 12))
        human_delay(60, 180, "between_x_actions")
        results["replied"] = await reply_to_mentions()
    
    logger.info(f"✅ X Session complete: {results}")
    return results

def run(session="morning"):
    """Synchronous entry point for GitHub Actions."""
    return asyncio.run(run_x_engagement_session(session))
