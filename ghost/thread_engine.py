"""
Ghost Handler — X Viral Thread Engine
Generates and posts full viral text threads to X daily.
Text threads get 3x more organic reach than video on X right now.

Thread formats proven to go viral in wealth/psychology niche:
- "N things rich people do that nobody talks about 🧵"
- "Brain hacks for instant focus 🧵"
- "I lost ₹1 lakh because of this one mistake 🧵"
"""
import os
import asyncio
import logging
import random
import json
from ghost.timing import human_delay, post_action_cooldown
from ghost.safety import can_act, record_action

logger = logging.getLogger("ThreadEngine")

THREAD_FORMATS = [
    {
        "title_template": "{topic} के {count} राज़ जो अमीर लोग कभी नहीं बताते 🧵",
        "style": "secrets",
        "count_range": (5, 9)
    },
    {
        "title_template": "Brain की {count} Cheatcodes जो आपको instantly smarter बनाएंगी 🧵",
        "style": "brain_hacks",
        "count_range": (5, 7)
    },
    {
        "title_template": "मैंने यह गलती की और ₹{amount} गंवाए — सीखो इससे 🧵",
        "style": "confession",
        "count_range": (4, 6)
    },
    {
        "title_template": "{topic} में success पाने के {count} proven steps 🧵",
        "style": "howto",
        "count_range": (5, 8)
    },
    {
        "title_template": "अगर मुझे {age} की उम्र में यह पता होता... 🧵",
        "style": "regret",
        "count_range": (5, 7)
    }
]

TOPICS = [
    "पैसे", "wealth", "mindset", "psychology", "AI tools",
    "investing", "side hustle", "productivity", "success",
    "self discipline", "morning routine", "financial freedom"
]

async def _generate_thread_with_gemini(thread_format, topic, count):
    """Use Gemini to generate a complete viral thread."""
    try:
        from google import genai
        gemini_key = os.environ.get("GEMINI_API_KEY", "")
        if not gemini_key:
            return None
        
        client = genai.Client(api_key=gemini_key)
        
        prompt = f"""You are a viral Hindi social media content creator specializing in wealth and psychology.
Generate a viral Twitter/X thread about "{topic}" with exactly {count} numbered points.

Format requirements:
- Tweet 1 (Hook): A powerful opening statement that creates curiosity. End with "🧵👇"
- Tweets 2-{count} (Body): Each tweet is ONE insight. Start with the number. Max 250 chars each. Mix Hindi+English naturally.
- Tweet {count+1} (CTA): End with "Follow @WealthMatrixAI for daily wealth psychology. Save this thread 📌"

Style: Shocking truths, counter-intuitive insights, specific numbers when possible.
Language: Mix Hindi and English naturally (Hinglish). Use emojis strategically.

Return ONLY a JSON array of tweet strings, nothing else.
Example: ["Tweet 1 text", "Tweet 2 text", ...]
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        tweets = json.loads(text.strip())
        if isinstance(tweets, list) and len(tweets) >= 3:
            return tweets
        return None
    except Exception as e:
        logger.error(f"Gemini thread generation failed: {e}")
        return None

def _get_offline_thread():
    """Fallback thread if Gemini fails."""
    return [
        "अमीर लोग वो नहीं करते जो आप सोचते हैं 🧵👇",
        "1/ वो ज़्यादा काम नहीं करते — वो सही काम करते हैं। Time को money से ज़्यादा value करते हैं।",
        "2/ वो कभी अपनी salary पर depend नहीं करते। Multiple income streams — यही उनका real secret है।",
        "3/ वो failure से नहीं डरते। हर successful person के पीछे कम से कम 5 बड़े failures हैं।",
        "4/ वो हमेशा सीखते रहते हैं। Average person Netflix देखता है, successful person books/courses लेता है।",
        "5/ वो अपनी net worth track करते हैं — income नहीं। Income कमाना नहीं, wealth build करना goal है।",
        "6/ वो 'No' कहना जानते हैं। हर opportunity को yes करने से आप कहीं नहीं पहुँचते।",
        "इस thread को Save करो 📌\nFollow करो @WealthMatrixAI — रोज़ एक नई wealth psychology insight।\n\nRetweet करो अगर यह valuable लगी 🔁"
    ]

async def post_viral_thread():
    """Generate and post a complete viral thread to X."""
    if not can_act("x", "tweet"):
        logger.warning("X tweet limit reached for today")
        return False

    try:
        from twikit import Client
        auth_token = os.environ.get("X_AUTH_TOKEN", "")
        ct0 = os.environ.get("X_CT0", "")
        if not auth_token or not ct0:
            logger.error("❌ X cookies missing")
            return False
        
        client = Client("en-US")
        client.set_cookies({"auth_token": auth_token, "ct0": ct0})
    except Exception as e:
        logger.error(f"❌ X client init failed: {e}")
        return False

    # Pick random thread format and topic
    fmt = random.choice(THREAD_FORMATS)
    topic = random.choice(TOPICS)
    count = random.randint(*fmt["count_range"])
    
    logger.info(f"🧵 Generating thread: {count} tweets about '{topic}'")
    
    # Generate tweets
    tweets = await _generate_thread_with_gemini(fmt, topic, count)
    if not tweets:
        logger.warning("⚠️ Using offline thread template")
        tweets = _get_offline_thread()

    logger.info(f"📝 Thread ready: {len(tweets)} tweets")
    
    # Post the thread
    previous_tweet_id = None
    posted = 0
    
    for i, tweet_text in enumerate(tweets):
        if not can_act("x", "tweet"):
            logger.warning("Tweet limit reached mid-thread")
            break
        
        try:
            # Truncate to 280 chars if needed
            if len(tweet_text) > 280:
                tweet_text = tweet_text[:277] + "..."
            
            logger.info(f"📤 Posting tweet {i+1}/{len(tweets)}: {tweet_text[:60]}...")
            
            if previous_tweet_id:
                # Reply to previous tweet (makes it a thread)
                result = await client.create_tweet(
                    text=tweet_text,
                    reply_to=previous_tweet_id
                )
            else:
                # First tweet of thread
                result = await client.create_tweet(text=tweet_text)
            
            previous_tweet_id = result.id
            record_action("x", "tweet")
            posted += 1
            
            # Human-like pause between tweets (45-90 seconds)
            if i < len(tweets) - 1:
                human_delay(45, 90, f"thread_tweet_{i+1}")
                
        except Exception as e:
            logger.error(f"❌ Failed to post tweet {i+1}: {e}")
            if "rate" in str(e).lower():
                break
    
    logger.info(f"✅ Thread posted: {posted}/{len(tweets)} tweets")
    return posted > 0

def run():
    """Synchronous entry point."""
    return asyncio.run(post_viral_thread())
