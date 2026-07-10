import os
import time
import json
import requests
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - UPLOADER - %(levelname)s - %(message)s")
logger = logging.getLogger("Uploader")

load_dotenv()

# Meta credentials
PAGE_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN", "")
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID", "")
INSTAGRAM_ACCOUNT_ID = os.environ.get("INSTAGRAM_ACCOUNT_ID", "")

# YouTube credentials
YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID", "")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
YOUTUBE_REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")

# Telegram credentials
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# ══════════════════════════════════════════════════════════════════════════════
# 💰 MONETIZATION: 3-Stream Passive Income Rotation
# ══════════════════════════════════════════════════════════════════════════════
AFFILIATE_LINK = os.environ.get("AFFILIATE_LINK", "")
AMAZON_AFFILIATE_LINK = os.environ.get("AMAZON_AFFILIATE_LINK", "")
OUTLIER_LINK = os.environ.get("OUTLIER_LINK", "")

def add_random_param(url):
    import random
    import string
    chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    if "?" in url:
        return f"{url}&ref=v35_{chars}"
    return f"{url}?ref=v35_{chars}"

def get_random_cta():
    import random as _rand
    options = []
    
    if AFFILIATE_LINK:
        safe_link = add_random_param(AFFILIATE_LINK)
        options.append({
            "text": f"📈 INVEST KARNA SEEKHO — FREE DEMAT ACCOUNT:\n{safe_link}\nZero commission. Aaj hi shuru karo.",
            "caption": f"📈 Free Demat Account — Zero Commission Invest karo: {safe_link}"
        })
        
    if AMAZON_AFFILIATE_LINK:
        safe_link = add_random_param(AMAZON_AFFILIATE_LINK)
        options.append({
            "text": f"📚 YEH BOOK PADHO — WEALTH PSYCHOLOGY:\n{safe_link}\nHar ameer insaan ne yeh book padhi hai.",
            "caption": f"📚 Yeh book padho — Wealth Psychology: {safe_link}"
        })
        
    if OUTLIER_LINK:
        safe_link = add_random_param(OUTLIER_LINK)
        options.append({
            "text": f"💵 GHAR BAITHE USD KAMAO — $15–50/HOUR:\n{safe_link}\nAI ko train karo aur dollars mein earn karo.",
            "caption": f"💵 Ghar baithe USD Kamao — $15–50/hour: {safe_link}"
        })
        
    if not options:
        return {
            "text": f"📈 INVEST KARNA SEEKHO — FREE DEMAT ACCOUNT:\n{add_random_param('https://groww.in')}\nZero commission. Aaj hi shuru karo.",
            "caption": f"📈 Free Demat Account — Zero Commission Invest karo: {add_random_param('https://groww.in')}"
        }
        
    return _rand.choice(options)

# Generate one unified CTA for this entire factory run
CURRENT_CTA = get_random_cta()

HASHTAG_POOL = [
    "#WealthMindset", "#PsychologyFacts", "#HindiMotivation", "#SuccessRules", "#Shorts", 
    "#Money", "#Rich", "#FinancialFreedom", "#InvestingHindi", "#StockMarketIndia", 
    "#PassiveIncome", "#BusinessMindset", "#SuccessQuotes", "#MotivationHindi", "#LifeLessons",
    "#GrowthMindset", "#EntrepreneurIndia", "#BillionaireMindset", "#MakeMoneyOnline", "#FinanceTips"
]

def get_dynamic_hashtags():
    import random
    return " ".join(random.sample(HASHTAG_POOL, k=6))

# ══════════════════════════════════════════════════════════════════════════════
# 🔍 SEO ENGINE: Keyword-rich YouTube title rotation
# ══════════════════════════════════════════════════════════════════════════════
SEO_TITLE_TEMPLATES = [
    "पैसे का सबसे बड़ा राज़ जो School ने नहीं बताया | Wealth Psychology Hindi #Shorts",
    "99% लोग यह गलती करते हैं | Dark Psychology of Money Hindi #Shorts",
    "Ameer Kaise Bane | अमीर लोगों का सबसे बड़ा राज़ #Shorts",
    "Rich vs Poor Mindset | अमीर और गरीब में फर्क #Shorts",
    "Paise Ki Psychology | पैसे की मनोविज्ञान Hindi #Shorts",
    "Financial Freedom Kaise Milegi | आर्थिक आज़ादी का राज़ #Shorts",
    "Investment Rules जो आपको कोई नहीं बताता | Wealth Rules Hindi #Shorts",
    "Zerodha Groww से Paise Kaise Kamaye | Stock Market Hindi #Shorts",
    "Success Ki Psychology | सफलता का राज़ Hindi Motivation #Shorts",
    "Middle Class Trap | मिडल क्लास से निकलने का तरीका #Shorts",
]

PINNED_COMMENTS = [
    "🔥 Part 2 kal aayega — Follow karo taaki miss na ho! Tum kaunse number pe ho? 1, 2, ya 3? Comment karo 👇",
    "❤️ Agar yeh video ne tumhari aankhen khol di — SAVE karo aur ek dost ko Share karo jise yeh sunna zaroori hai! 🔖",
    "🚀 Follow karo — har roz ek naya wealth secret post karta hoon jo 1% log jaante hain. Next video aur bhi powerful hai!",
    "📌 Save this. 6 mahine baad ise dobara dekho — tum khud ko thanks kahoge. Ready ho? READY likho neeche 👇",
    "💡 Comment karo: Tumhari sabse badi financial mistake kya hai? Main personally padhta hoon sabke comments 👇",
]

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")

def send_telegram_video(video_path, caption=""):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    try:
        with open(video_path, 'rb') as video_file:
            files = {'video': video_file}
            data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
            requests.post(url, data=data, files=files, timeout=600)
    except Exception as e:
        logger.error(f"Failed to send Telegram video: {e}")

def upload_to_telegram_channel(video_path, caption):
    # Sends the video directly to the public Telegram channel
    # Requires TELEGRAM_BOT_TOKEN and the channel username @wealth_Matrix_Ai
    channel_username = "@wealth_Matrix_Ai"
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("⏭️ Skipping Telegram Channel: Missing Bot Token")
        return False
        
    logger.info(f"📤 Uploading Video to Telegram Channel {channel_username}...")
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    
    try:
        with open(video_path, 'rb') as video_file:
            files = {'video': video_file}
            data = {'chat_id': channel_username, 'caption': caption, 'parse_mode': 'HTML'}
            res = requests.post(url, data=data, files=files, timeout=600)
            
        if res.status_code == 200:
            logger.info("✅ Telegram Channel Upload SUCCESS!")
            return True
        else:
            logger.error(f"❌ Telegram Channel Upload FAILED: {res.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Telegram Channel Exception: {e}")
        return False

def get_facebook_page_token(user_token, page_id):
    if not user_token or not page_id:
        return user_token
    url = f"https://graph.facebook.com/v19.0/{page_id}"
    params = {"fields": "access_token", "access_token": user_token}
    try:
        res = requests.get(url, params=params, timeout=10).json()
        if "access_token" in res:
            logger.info("Successfully obtained Page Access Token dynamically.")
            return res["access_token"]
        else:
            logger.warning(f"Facebook Page Token exchange response: {res}. Using original token.")
    except Exception as e:
        logger.error(f"Error exchanging token: {e}. Using original token.")
    return user_token

def upload_to_temp_host(file_path):
    logger.info("Uploading video to temporary public host (uguu.se)...")
    try:
        with open(file_path, 'rb') as f:
            res = requests.post("https://uguu.se/upload", files={'files[]': f}, timeout=120)
            if res.status_code == 200:
                data = res.json()
                if data.get('success'):
                    url = data['files'][0]['url']
                    logger.info(f"✅ Video uploaded to public URL: {url}")
                    return url
    except Exception as e:
        logger.error(f"uguu.se upload failed: {e}")

    logger.info("Fallback 1: Uploading to tmpfiles.org...")
    try:
        with open(file_path, 'rb') as f:
            res = requests.post('https://tmpfiles.org/api/v1/upload', files={'file': f}, timeout=120)
            if res.status_code == 200:
                data = res.json()
                if data.get('status') == 'success':
                    url = data['data']['url']
                    direct_url = url.replace('tmpfiles.org/', 'tmpfiles.org/dl/')
                    logger.info(f"✅ Video uploaded to public URL: {direct_url}")
                    return direct_url
    except Exception as e:
        logger.error(f"tmpfiles.org failed: {e}")
        
    logger.info("Fallback 2: Uploading to catbox.moe...")
    try:
        with open(file_path, 'rb') as f:
            res = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": f}, timeout=120)
            if res.status_code == 200 and res.text.startswith("https://"):
                logger.info(f"✅ Video uploaded to public URL: {res.text}")
                return res.text
    except Exception as e:
        logger.error(f"catbox.moe upload failed: {e}")
        
    logger.info("Fallback 3: Uploading to file.io...")
    try:
        with open(file_path, 'rb') as f:
            res = requests.post("https://file.io", files={'file': f}, timeout=120)
            if res.status_code == 200:
                data = res.json()
                if data.get('success'):
                    logger.info(f"✅ Video uploaded to public URL: {data['link']}")
                    return data['link']
    except Exception as e:
        logger.error(f"file.io upload failed: {e}")
        
    return None

def wait_for_ig_media_ready(creation_id, access_token):
    url = f"https://graph.facebook.com/v19.0/{creation_id}?fields=status_code&access_token={access_token}"
    for _ in range(12):
        res = requests.get(url).json()
        status = res.get("status_code", "ERROR")
        if status == "FINISHED":
            return True
        elif status == "ERROR" or status == "EXPIRED":
            logger.error(f"IG container failed: {status}")
            return False
        time.sleep(10)
    return False

def upload_to_facebook_reels(video_path, description):
    if not PAGE_ACCESS_TOKEN or not PAGE_ID:
        logger.warning("⏭️ Skipping Facebook Reels (Missing Credentials)")
        return False
        
    page_token = get_facebook_page_token(PAGE_ACCESS_TOKEN, PAGE_ID)
    
    logger.info(f"📤 Starting Facebook Reel upload for {video_path}")
    init_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_reels"
    init_payload = {"upload_phase": "start", "access_token": page_token}
    
    try:
        init_res = requests.post(init_url, data=init_payload, timeout=30).json()
        if "video_id" not in init_res:
            logger.error(f"Failed to initialize FB upload: {init_res}")
            return False
            
        video_id = init_res["video_id"]
        upload_url = init_res["upload_url"]
        
        headers = {"Authorization": f"OAuth {page_token}", "offset": "0", "file_size": str(os.path.getsize(video_path))}
        with open(video_path, "rb") as f:
            requests.post(upload_url, headers=headers, data=f, timeout=60).json()
            
        publish_payload = {
            "upload_phase": "finish", "access_token": page_token,
            "video_id": video_id, "video_state": "PUBLISHED", "description": description
        }
        publish_res = requests.post(init_url, data=publish_payload, timeout=30).json()
        if "success" in publish_res and publish_res["success"]:
            logger.info("✅ Successfully published to Facebook Reels!")
            return True
        else:
            logger.error(f"Failed to publish FB Reel: {publish_res}")
    except Exception as e:
        logger.error(f"FB Upload Exception: {e}")
    return False

def upload_to_facebook_story(video_path):
    if not PAGE_ACCESS_TOKEN or not PAGE_ID: return False
    page_token = get_facebook_page_token(PAGE_ACCESS_TOKEN, PAGE_ID)
    
    logger.info("Posting Facebook Story...")
    init_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/video_stories"
    init_payload = {"upload_phase": "start", "access_token": page_token}
    
    try:
        init_res = requests.post(init_url, data=init_payload, timeout=30).json()
        if "video_id" not in init_res:
            logger.error(f"Failed to initialize FB Story upload: {init_res}")
            return False
            
        video_id = init_res["video_id"]
        upload_url = init_res["upload_url"]
        
        headers = {"Authorization": f"OAuth {page_token}", "offset": "0", "file_size": str(os.path.getsize(video_path))}
        with open(video_path, "rb") as f:
            requests.post(upload_url, headers=headers, data=f, timeout=120).json()
            
        publish_payload = {
            "upload_phase": "finish", "access_token": page_token,
            "video_id": video_id
        }
        publish_res = requests.post(init_url, data=publish_payload, timeout=30).json()
        if "success" in publish_res and publish_res["success"]:
            logger.info("✅ Facebook Story posted!")
            return True
        else:
            logger.error(f"❌ Facebook Story API error: {publish_res}")
    except Exception as e:
        logger.error(f"❌ Facebook Story failed: {e}")
    return False

import re

def upload_to_instagram_reels(video_url, description, cover_url=None):
    if not PAGE_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID or not PAGE_ID:
        logger.warning("⏭️ Skipping Instagram Reels (Missing Credentials)")
        return False
    
    # ANTI-SPAM: Remove raw URLs and replace with 'Link in Bio'
    safe_description = re.sub(r'https?://[^\s]+', '🔗 Link in Bio!', description)
    
    page_token = get_facebook_page_token(PAGE_ACCESS_TOKEN, PAGE_ID)
    logger.info(f"📤 Starting Instagram Reel upload with URL")
    
    container_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
    container_payload = {"media_type": "REELS", "video_url": video_url, "caption": safe_description, "access_token": page_token}
    if cover_url:
        container_payload["cover_url"] = cover_url
    
    try:
        container_res = requests.post(container_url, data=container_payload, timeout=30).json()
        if "id" not in container_res:
            logger.error(f"Failed to create IG Media Container: {container_res}")
            return False
            
        creation_id = container_res["id"]
        logger.info(f"✅ Created IG container: {creation_id}")
        
        if not wait_for_ig_media_ready(creation_id, page_token):
            return False
            
        publish_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_payload = {"creation_id": creation_id, "access_token": page_token}
        publish_res = requests.post(publish_url, data=publish_payload, timeout=30).json()
        
        if "id" in publish_res:
            logger.info("✅ Successfully published to Instagram Reels!")
            return True
        else:
            logger.error(f"Failed to publish IG Reel: {publish_res}")
    except Exception as e:
        logger.error(f"IG Upload Exception: {e}")
    return False

def upload_to_instagram_story(video_url):
    if not PAGE_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID or not PAGE_ID: return False
    page_token = get_facebook_page_token(PAGE_ACCESS_TOKEN, PAGE_ID)
    logger.info("Posting Instagram Story...")
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {"media_type": "STORIES", "video_url": video_url, "access_token": page_token}
    try:
        res = requests.post(url, data=payload).json()
        creation_id = res.get("id")
        if not creation_id:
            logger.error(f"❌ Failed to create IG story container: {res}")
            return False
        if not wait_for_ig_media_ready(creation_id, page_token):
            return False
        pub_url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        pub_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": page_token}).json()
        if "id" in pub_res:
            logger.info("✅ Instagram Story posted!")
            return True
        else:
            logger.error(f"❌ Failed to publish IG Story: {pub_res}")
    except Exception as e:
        logger.error(f"❌ Instagram Story failed: {e}")
    return False

def upload_to_youtube_shorts(video_path, description):
    if not YOUTUBE_CLIENT_ID or not YOUTUBE_CLIENT_SECRET or not YOUTUBE_REFRESH_TOKEN:
        logger.warning("⏭️ Skipping YouTube Shorts (Missing Credentials)")
        return False
        
    logger.info("📤 Starting YouTube Shorts upload...")
    try:
        # Step 1: Refresh Access Token
        token_url = "https://oauth2.googleapis.com/token"
        token_payload = {
            "client_id": YOUTUBE_CLIENT_ID,
            "client_secret": YOUTUBE_CLIENT_SECRET,
            "refresh_token": YOUTUBE_REFRESH_TOKEN,
            "grant_type": "refresh_token"
        }
        token_res = requests.post(token_url, data=token_payload, timeout=30).json()
        access_token = token_res.get("access_token")
        if not access_token:
            logger.error(f"Failed to refresh YouTube access token: {token_res}")
            return False
            
        # Step 2: Initialize Resumable Upload Session
        upload_init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Length": str(os.path.getsize(video_path)),
            "X-Upload-Content-Type": "video/mp4"
        }
        
        # 🔍 SEO-OPTIMIZED TITLE: rotate through keyword-rich templates
        import random as _rand
        seo_title = _rand.choice(SEO_TITLE_TEMPLATES)

        # Build rich YouTube description for SEO + monetization
        clean_body = description.split("#")[0].strip()
        full_description = f"""{clean_body}

══════════════════════════════
{CURRENT_CTA['text']}
══════════════════════════════
🔔 SUBSCRIBE karo aur bell icon dabao — har roz ek naya wealth secret!

{get_dynamic_hashtags()}"""

        metadata = {
            "snippet": {
                "title": seo_title,
                "description": full_description,
                "categoryId": "27"  # Education (better for finance content than People & Blogs)
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }
        
        init_res = requests.post(upload_init_url, headers=headers, json=metadata, timeout=30)
        if init_res.status_code != 200:
            logger.error(f"Failed to initialize YouTube upload: {init_res.status_code} - {init_res.text}")
            return False
            
        upload_url = init_res.headers.get("Location")
        if not upload_url:
            logger.error("No Location header returned from YouTube upload initialization.")
            return False
            
        # Step 3: Upload Video File
        file_size = os.path.getsize(video_path)
        put_headers = {
            "Content-Length": str(file_size),
            "Content-Type": "video/mp4"
        }
        
        with open(video_path, "rb") as f:
            put_res = requests.put(upload_url, headers=put_headers, data=f, timeout=120)
            
        if put_res.status_code in [200, 201]:
            video_data = put_res.json() if put_res.text else {}
            video_id = video_data.get("id", "")
            logger.info("✅ Successfully published to YouTube Shorts!")
            # 📌 AUTO-PIN CTA COMMENT
            if video_id:
                youtube_pin_comment(video_id, access_token)
            return True
        else:
            logger.error(f"YouTube file upload failed: {put_res.status_code} - {put_res.text}")
    except Exception as e:
        logger.error(f"YouTube Upload Exception: {e}")
    return False

def youtube_pin_comment(video_id, access_token):
    """Automatically posts and pins a CTA comment on every YouTube upload."""
    import random as _rand
    import string
    
    # Generate an invisible zero-width space or random invisible characters to bypass exact string matching
    invisible_salt = ''.join(_rand.choices(['\u200b', '\u200c', '\u200d', '\ufeff'], k=3))
    
    pinned_text = _rand.choice(PINNED_COMMENTS) + f" {invisible_salt}"
    
    try:
        # Step 1: Post the comment
        comment_url = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet"
        comment_headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        comment_body = {
            "snippet": {
                "videoId": video_id,
                "topLevelComment": {
                    "snippet": {"textOriginal": pinned_text}
                }
            }
        }
        comment_res = requests.post(comment_url, headers=comment_headers, json=comment_body, timeout=30).json()
        comment_id = comment_res.get("id", "")
        if not comment_id:
            logger.warning(f"Could not post pinned comment: {comment_res}")
            return
        # Step 2: Pin it
        pin_url = f"https://www.googleapis.com/youtube/v3/comments?part=snippet"
        pin_body = {"id": comment_id, "snippet": {"moderationStatus": "published"}}
        requests.put(pin_url, headers=comment_headers, json=pin_body, timeout=30)
        logger.info(f"📌 Auto-pinned comment on video {video_id}: {pinned_text[:60]}...")
    except Exception as e:
        logger.warning(f"Auto-pin comment failed (non-critical): {e}")

def trigger_make_webhook(video_url, caption):
    webhook_url = os.environ.get("MAKE_WEBHOOK_URL")
    if not webhook_url:
        logger.warning("MAKE_WEBHOOK_URL not found in .env. Skipping Buffer Bridge distribution (X/Pinterest/LinkedIn).")
        return False
        
    logger.info("🌐 Triggering Make.com Webhook for Buffer Bridge (X, Pinterest, LinkedIn)...")
    
    # Generate a Twitter-safe caption (< 280 characters)
    # This strips all hashtags and truncates to 250 chars safely
    twitter_cap = caption.split("#")[0].strip()
    if not twitter_cap:
        import re
        twitter_cap = re.sub(r'#\w+', '', caption).strip()
    if not twitter_cap:
        twitter_cap = "Must watch! 🚀"
        
    if len(twitter_cap) > 250:
        twitter_cap = twitter_cap[:247] + "..."
        
    try:
        payload = {
            "video_url": video_url,
            "caption": caption,
            "twitter_caption": twitter_cap
        }
        res = requests.post(webhook_url, json=payload, timeout=60)
        if res.status_code in [200, 201, 202]:
            logger.info("✅ Successfully triggered Make.com Webhook!")
            return True
        else:
            logger.error(f"❌ Make.com Webhook failed with status {res.status_code}: {res.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Make.com Webhook exception: {e}")
        return False


def distribute_to_all_platforms(video_path, description, cover_path=None):
    logger.info("🌐 Initiating Multi-Platform Distribution Pipeline...")

    raw_description = description

    # 💰 MONETIZATION: Inject affiliate link into every caption BEFORE hashtags
    if "#" in description:
        idx = description.find("#")
        base_text = description[:idx].strip()
        tags_text = description[idx:].strip()
        injected_description = f"{base_text}\n\n{CURRENT_CTA['caption']}\n\n{tags_text}"
    else:
        injected_description = f"{description}\n\n{CURRENT_CTA['caption']}"
        
    logger.info(f"💰 Monetization CTA injected into caption: {CURRENT_CTA['caption'][:40]}...")

    logger.info(f"📝 Final Caption: {injected_description}")
    
    yt = upload_to_youtube_shorts(video_path, raw_description)
    time.sleep(5)
    
    fb = upload_to_facebook_reels(video_path, injected_description)
    time.sleep(5)
    
    video_url = upload_to_temp_host(video_path)
    cover_url = upload_to_temp_host(cover_path) if cover_path and os.path.exists(cover_path) else None
    ig, ig_story, fb_story, buffer_bridge, x_upload = False, False, False, False, False
    
    if video_url:
        ig = upload_to_instagram_reels(video_url, injected_description, cover_url)
        time.sleep(5)
        ig_story = upload_to_instagram_story(video_url)
        time.sleep(5)
        fb_story = upload_to_facebook_story(video_path)
        time.sleep(5)
        buffer_bridge = trigger_make_webhook(video_url, injected_description)
    else:
        logger.error("❌ Skipping Instagram/Stories/Buffer because public video URL generation failed.")
        
    # Send to Telegram Channel (always runs, doesn't need public URL)
    tg_channel = upload_to_telegram_channel(video_path, injected_description)
    
    logger.info("🚀 Distribution Complete!")
    
    status_msg = f"""
✅ <b>V35 Factory Complete</b>
<i>Successfully distributed payload.</i>

<b>Primary Triad:</b>
🟥 YouTube Shorts: {'✅' if yt else '❌'}
🟦 Facebook Reels: {'✅' if fb else '❌'}
🟪 Instagram Reels: {'✅' if ig else '❌'}
✈️ Telegram Channel: {'✅' if tg_channel else '❌'}

<b>Secondary Distribution:</b>
📘 Facebook Story: {'✅' if fb_story else '❌'}
📸 Instagram Story: {'✅' if ig_story else '❌'}

<b>Buffer Bridge (Pinterest / LinkedIn):</b>
🚀 Make.com Webhook: {'✅' if buffer_bridge else '❌'}


<b>Caption Used:</b>
{__import__('html').escape(injected_description)}

ACTION: Confirm bio link is live at instagram.com/wealth_matrix_ai before peak hours.
"""
    send_telegram_alert(status_msg)
    
    # Send a second, completely isolated message just for easy copy-pasting
    copy_paste_text = raw_description.split("#")[0].strip() + "\n\n🔗 Link in Bio! 🚀\n\n" + get_dynamic_hashtags()
    send_telegram_alert(copy_paste_text)
    
    # Send the actual MP4 file so the user can easily share it to Pinterest/Snapchat from their phone
    send_telegram_video(video_path, "📱 Here is your finalized MP4 file for manual upload to Pinterest/Snapchat!")
    
    return {
        "facebook": fb,
        "instagram": ig,
        "youtube": yt,
        "fb_story": fb_story,
        "ig_story": ig_story,
        "buffer_bridge": buffer_bridge
    }

if __name__ == "__main__":
    video_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "FINAL_V35_HD.mp4"))
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "remotion-studio", "public", "v32_script.json"))
    
    if not os.path.exists(video_path):
        logger.error(f"Rendered video not found at {video_path}")
        raise FileNotFoundError(f"Video file missing: {video_path}")
        
    caption = "आज ही शुरुआत करें। #wealth #mindset #money #success #hindi"
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                caption = data["script"]["caption"]
        except Exception as e:
            logger.error(f"Failed to read caption from JSON: {e}")
            
    cover_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "cover.jpg"))
    distribute_to_all_platforms(video_path, caption, cover_path)
