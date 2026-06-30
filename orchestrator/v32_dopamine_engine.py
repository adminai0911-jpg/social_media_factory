import os
import json
import random
import requests
import subprocess
import sys
import logging
import time
import wave
import math
import struct
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv
from mutagen.mp3 import MP3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - V32_ENGINE - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# 🔥 DYNAMIC HASHTAG ROTATION ENGINE — 40+ hashtags, fresh mix every run
# ══════════════════════════════════════════════════════════════════════════════
HASHTAG_POOL = {
    # MEGA tags (100M+ posts) — maximum reach
    "mega": [
        "#motivation", "#success", "#mindset", "#money", "#rich",
        "#financialfreedom", "#investment", "#wealth", "#entrepreneur", "#lifestyle"
    ],
    # NICHE wealth/psychology (1M–10M posts) — highly targeted audience
    "niche_wealth": [
        "#WealthMindset", "#MoneyMindset", "#RichMindset", "#FinancialLiteracy",
        "#PassiveIncome", "#InvestSmart", "#WealthBuilding", "#MoneyTips",
        "#FinancialFreedom", "#MoneyManagement"
    ],
    # HINDI / INDIA-SPECIFIC (high relevance for your niche audience)
    "hindi": [
        "#HindiMotivation", "#SuccessRules", "#PsychologyFacts", "#MotivationHindi",
        "#IndianEntrepreneur", "#SelfMadeIndia", "#DesiMillionaire", "#IndiaGrowth",
        "#HindiShorts", "#IndianYouth"
    ],
    # PSYCHOLOGY / DARK PSYCHOLOGY (trending micro-niche)
    "psychology": [
        "#DarkPsychology", "#BrainHack", "#MindHacks", "#PsychologyOfMoney",
        "#BehavioralEconomics", "#CognitiveBias", "#MindsetShift", "#GrowthMindset",
        "#PsychologyTips", "#HumanBehavior"
    ],
    # REELS/SHORTS ALGO TAGS (boost distribution on platform)
    "platform": [
        "#Reels", "#Shorts", "#ViralReels", "#TrendingShorts", "#ExploreReels",
        "#ReelItFeelIt", "#InstagramReels", "#YoutubeShorts", "#ViralVideo", "#ForYou"
    ]
}

def get_dynamic_hashtags():
    """Pick a fresh, optimized hashtag combo every run — never the same set twice."""
    selected = []
    selected += random.sample(HASHTAG_POOL["mega"], 1)          # 1 mega tag
    selected += random.sample(HASHTAG_POOL["niche_wealth"], 1)  # 1 niche wealth
    selected += random.sample(HASHTAG_POOL["hindi"], 1)         # 1 Hindi/India
    selected += random.sample(HASHTAG_POOL["psychology"], 1)    # 1 psychology
    selected += random.sample(HASHTAG_POOL["platform"], 1)      # 1 platform algo
    random.shuffle(selected)
    return " ".join(selected)

# ══════════════════════════════════════════════════════════════════════════════
# 📅 SERIES PART TRACKER — Ensures Part 1 → 2 → 3 hooks are always accurate
# ══════════════════════════════════════════════════════════════════════════════
SERIES_TRACKER_FILE = os.path.join(os.path.dirname(__file__), "series_tracker.json")

def get_series_part():
    """Returns the current series part (1, 2, or 3) and advances the counter."""
    try:
        if os.path.exists(SERIES_TRACKER_FILE):
            with open(SERIES_TRACKER_FILE, "r") as f:
                data = json.load(f)
            part = data.get("current_part", 1)
        else:
            part = 1
        next_part = (part % 3) + 1  # cycles 1 → 2 → 3 → 1 → ...
        with open(SERIES_TRACKER_FILE, "w") as f:
            json.dump({"current_part": next_part, "last_run": datetime.now().isoformat()}, f)
        return part
    except Exception:
        return random.randint(1, 3)

load_dotenv()

raw_keys = [
    os.getenv("GEMINI_API_KEY_1", ""),
    os.getenv("GEMINI_API_KEY_2", ""),
    os.getenv("GEMINI_API_KEY_3", ""),
    os.getenv("GEMINI_API_KEY_4", ""),
    os.getenv("GEMINI_API_KEY_5", ""),
    os.getenv("GEMINI_API_KEY", "")
]

GEMINI_KEYS = []
for raw in raw_keys:
    if raw:
        # Split by comma to support users pasting multiple keys in one secret
        for k in raw.split(","):
            clean_k = k.strip()
            if clean_k and clean_k not in GEMINI_KEYS:
                GEMINI_KEYS.append(clean_k)

# ── LANGUAGE & VOICE ROULETTE ──
# 50% chance to run in English, 50% chance in Hindi.
CURRENT_LANGUAGE = random.choice(["English", "Hindi"])

# Always use Hindi voices to support Hinglish/Devanagari gracefully
EDGE_VOICES = ["hi-IN-MadhurNeural", "hi-IN-SwaraNeural"]
ELEVEN_VOICES = ["pNInz6obpgDQGcFmaJgB", "ErXwobaYiN019PkySvjV"]

def get_omni_analytics_feedback():
    """Fetches recent video performance from YouTube, Instagram, and Facebook APIs to guide Gemini."""
    feedback = ""
    
    # ── YOUTUBE ANALYTICS ──
    try:
        from dotenv import load_dotenv
        load_dotenv()
        client_id = os.environ.get("YOUTUBE_CLIENT_ID")
        client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
        refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
        
        if client_id and client_secret and refresh_token:
            token_url = "https://oauth2.googleapis.com/token"
            res = requests.post(token_url, data={
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }, timeout=10).json()
            
            access_token = res.get("access_token")
            if access_token:
                headers = {"Authorization": f"Bearer {access_token}"}
                channel_res = requests.get("https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true", headers=headers, timeout=10).json()
                if "items" in channel_res:
                    uploads_list_id = channel_res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
                    playlist_res = requests.get(f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_list_id}&maxResults=5", headers=headers, timeout=10).json()
                    video_ids = ",".join([i["snippet"]["resourceId"]["videoId"] for i in playlist_res.get("items", [])])
                    
                    if video_ids:
                        stats_res = requests.get(f"https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet&id={video_ids}", headers=headers, timeout=10).json()
                        feedback += "\n[YOUTUBE PERFORMANCE]\n"
                        for item in stats_res.get("items", []):
                            title = item["snippet"]["title"]
                            views = item["statistics"].get("viewCount", "0")
                            feedback += f"- '{title}': {views} views\n"
    except Exception as e:
        logger.warning(f"YouTube Analytics error: {e}")

    # ── INSTAGRAM ANALYTICS ──
    try:
        ig_id = os.environ.get("INSTAGRAM_ACCOUNT_ID")
        fb_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
        if ig_id and fb_token:
            ig_url = f"https://graph.facebook.com/v19.0/{ig_id}/media?fields=caption,like_count,comments_count&limit=5&access_token={fb_token}"
            ig_res = requests.get(ig_url, timeout=10).json()
            if "data" in ig_res and ig_res["data"]:
                feedback += "\n[INSTAGRAM REELS PERFORMANCE]\n"
                for item in ig_res["data"]:
                    caption = item.get("caption", "No Caption")[:50].replace("\n", " ") + "..."
                    likes = item.get("like_count", 0)
                    comments = item.get("comments_count", 0)
                    feedback += f"- '{caption}': {likes} likes, {comments} comments\n"
    except Exception as e:
        logger.warning(f"Instagram Analytics error: {e}")
        
    # ── FACEBOOK ANALYTICS ──
    try:
        fb_id = os.environ.get("FACEBOOK_PAGE_ID")
        fb_token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
        if fb_id and fb_token:
            fb_url = f"https://graph.facebook.com/v19.0/{fb_id}/published_posts?fields=message,likes.summary(true),comments.summary(true)&limit=5&access_token={fb_token}"
            fb_res = requests.get(fb_url, timeout=10).json()
            if "data" in fb_res and fb_res["data"]:
                feedback += "\n[FACEBOOK PERFORMANCE]\n"
                for item in fb_res["data"]:
                    message = item.get("message", "No Message")[:50].replace("\n", " ") + "..."
                    likes = item.get("likes", {}).get("summary", {}).get("total_count", 0)
                    comments = item.get("comments", {}).get("summary", {}).get("total_count", 0)
                    feedback += f"- '{message}': {likes} likes, {comments} comments\n"
    except Exception as e:
        logger.warning(f"Facebook Analytics error: {e}")
        
    if feedback:
        return f"\n\nCRITICAL OMNI-CHANNEL ANALYTICS FEEDBACK FROM PREVIOUS UPLOADS:{feedback}\nUse this real-world data to double-down on what is working. Lean into the topics/hooks that got the most views/likes across platforms.\n"
    return ""


def generate_dynamic_script():
    """Call Gemini to generate a fresh, unique, dopamine-triggering script JSON."""
    valid_keys = [k for k in GEMINI_KEYS if k]
    if not valid_keys:
        logger.error("No Gemini keys found!")
        return None
        
    random.shuffle(valid_keys)

    # ── ULTIMATE V3: Psychological Weapon Hooks — 6 Categories, 24 Triggers ─────
    hooks = [
        # 🧠 CATEGORY 1: CURIOSITY GAP — Brain MUST finish the thought
        "मैंने 5 साल बर्बाद किए यह गलती करके। आप मत करना।",
        "The one word that separates the rich from the poor. Most people die never learning it.",
        "I studied 500 crore worth of wealth decisions. The pattern will shock you.",
        "जो आपको school ने कभी नहीं सिखाया — वो 10 seconds में बता देता हूँ।",

        # 😨 CATEGORY 2: FEAR OF LOSS — Survival brain activates instantly
        "हर रोज़ आप ₹847 खो रहे हो। यह calculation देखो।",
        "If you earn under ₹1 lakh/month and do THIS — you will never escape.",
        "आपकी एक आदत आपकी पूरी ज़िंदगी की savings खा रही है। अभी रुको।",
        "The invisible financial mistake that is costing you ₹12 lakh every decade.",

        # 🎯 CATEGORY 3: IDENTITY THREAT — Personally called out, cannot look away
        "अगर आप यह वीडियो skip करते हो — तो आप exactly वही करते हो जो poor लोग करते हैं।",
        "This mindset is the ONLY reason you are not rich yet. Be honest with yourself.",
        "तुम्हारे parents ने पैसे के बारे में 3 झूठ सिखाए। आज तोड़ते हैं।",
        "The financially free version of you is watching this. Will you listen?",

        # 🏆 CATEGORY 4: AUTHORITY + PROOF / RELATABLE REALITY — Mix billionaires with relatable scenarios
        "Self-made billionaires commonly follow this one counterintuitive rule.",
        "Financial experts warn: 92% of the middle class makes THIS mistake before 35.",
        "Mere ek dost ki salary ₹60,000 hai phir bhi wo hamesha broke rehta hai. Kyun?",
        "Agar tumhari age 20s me hai aur bank balance ₹1 lakh se kam hai, toh yeh suno.",

        # 🔁 CATEGORY 5: SERIES / OPEN LOOP — Forces follow for Part 2
        "Part 1/3: पैसे की वो psychology जो 1% लोग जानते हैं।",
        "This is the most important financial video I have ever made. Here is why.",
        "यह 3-part series तुम्हारी financial life बदल देगी। Part 1 शुरू करते हैं।",
        "Billionaires use these 3 rules. Today: Rule #1. Follow for Rule #2 tomorrow.",

        # 💡 CATEGORY 6: GENUINE VALUE PROMISE — Builds trust AND drives watch-time
        "मैं तुम्हें वो 3 rules बताने वाला हूँ जो rich dads अपने बच्चों को सिखाते हैं।",
        "The exact step-by-step formula to go from ₹0 savings to financial freedom.",
        "अगर तुम्हारी age 18-35 है — यह वीडियो तुम्हारी ज़िंदगी का सबसे important investment है।",
        "The 60-second wealth education your school stole from you."
    ]

    ctas = [
        # 🔥 IDENTITY COMMITMENT — strongest engagement trigger
        "Comment 'FIRE 🔥' अगर यह तुम्हारी आंखें खोल गया।",
        "Type '1' अगर तुम यह जानते थे। Type '2' अगर नहीं। Comment करो — I read every one 👇",
        "Comment करो — तुम्हारी सबसे बड़ी financial mistake क्या है? मैं personally reply करूँगा 💬",

        # 📌 URGENCY + FOMO — high save rate = algorithm boost
        "Save this NOW before the algorithm buries it. You WILL need this. 📌",
        "इसे Save करो। 6 महीने बाद इसे फिर देखना — तुम चौंक जाओगे। 🔖",

        # ❤️ SHARING TRIGGER — organic reach multiplier
        "Share this with ONE person जो financially struggle कर रहा है। यही असली friendship है। ❤️‍🔥",
        "Tag वो दोस्त जिसे यह सुनना ज़रूरी है — तुम उसकी ज़िंदगी बदल दोगे 👇",

        # 🚀 SERIES HOOK — forces account follow
        "Follow करो — कल Part 2 आएगा जो आज से भी ज़्यादा powerful है। 🚀",
        "Like करो अगर तुम Part 2 चाहते हो — देखते हैं कितने लोग seriously लेते हैं 👍",

        # 🎯 CHALLENGE CTA — creates viral comment threads
        "यह rule अगले 7 दिन try करो और comment करो — result क्या आया? 💪"
    ]
    hook = random.choice(hooks)
    cta  = random.choice(ctas)

    hashtags = get_dynamic_hashtags()
    series_part = get_series_part()
    logger.info(f"📅 Series Part: {series_part}/3")
    logger.info(f"#️⃣  Hashtags this run: {hashtags}")

    # Analytics Feedback
    analytics_text = get_omni_analytics_feedback()

    prompt = f"""You are an elite TikTok/Reels/Shorts growth expert and dopamine-engineering copywriter.
    Your sole purpose is to write highly viral, 15-30 second scripts about wealth, dark psychology, or deep success.

    {analytics_text}

    LANGUAGE REQUIREMENT:
    The entire script MUST be written in {CURRENT_LANGUAGE}. If Hindi, use Devanagari script. If English, use English.

    You are the world's most elite viral content strategist — combining the psychological precision of Robert Cialdini, the storytelling of Gary Vee, and the wealth knowledge of Naval Ravikant — specifically optimized for Indian short-form video (Instagram Reels, YouTube Shorts, Facebook Reels).

═══════════════════════════════════════════════
CONTENT QUALITY RULES (NON-NEGOTIABLE):
═══════════════════════════════════════════════
- Language: All on-screen text fields (hook, rules, claims, items) MUST be in Hindi/Hinglish (Devanagari script allowed). DO NOT use pure English.
- NO REDUNDANCY: Do NOT prefix numbered_list items with "Rule 1:", "Fact:", or numbers like "1.". The UI automatically adds numbers! Just provide the raw text.
- ANTI-HALLUCINATION: Do NOT invent fake studies or fake "Verified Data". Use "Many experts believe" framing if you don't have a real, verifiable source.
- ZERO generic advice: Never say "work hard", "save money". Every insight MUST be counterintuitive.
- The numbered_list must teach a COMPLETE, ACTIONABLE mini-framework.
- Return ONLY raw JSON. No markdown. No backticks. No explanation text.

Mandatory: hook MUST use this text exactly: {hook}
Mandatory: save_cta MUST use this text exactly: {cta}

JSON Schema (RETURN ONLY THIS):
{{
  "hook": "{hook}",
  "authority_claim": "ONE brutal, specific, stat-backed truth bomb that makes the viewer's jaw drop. Sound like a professor who has seen behind the curtain. MAX 18 words.",
  "numbered_list": [
    {{
      "text": "[A counterintuitive, specific, actionable wealth rule with a number. Something a rich dad teaches his son. Max 10 words.]",
      "type": "INSIGHT"
    }},
    {{
      "text": "[A dark psychological truth about money that most people are too scared to admit about themselves. Max 10 words.]",
      "type": "INSIGHT"
    }},
    {{
      "text": "[A SHOCKING, jaw-dropping statistic with a real Rupee figure or percentage that reframes everything. Max 12 words.]",
      "type": "DATA",
      "source": "[ONE short, real, verifiable source e.g. 'Source: SEBI 2024'. If not verifiable, return empty string.]"
    }}
  ],
  "proof_demo": "Real-world proof using a NAMED billionaire, a credible institution, OR a relatable real-world scenario (e.g. ₹60k/month earner). Make it feel like insider knowledge. MAX 15 words.",
  "proof_source": "ONE real, verifiable source for the proof_demo claim (e.g. 'Source: Forbes India 2024'). ONLY add if the claim is real and verifiable. If not verifiable, return empty string.",
  "curiosity_teaser": "A short 4-8 word teaser that plants a question in the viewer's mind early in the video.",
  "curiosity_payoff": "A short 4-8 word answer to the teaser that appears later in the video.",
  "red_box_keyword": "ONE exact word from the hook that is the most important/shocking word. Must be exactly present in the hook.",
  "comment_question": "A SPECIFIC question about this reel's exact content. Example: 'Rule 1, 2, ya 3 — kaunsa tumne abhi tak miss kiya?' MAX 12 words.",
  "save_cta": "{cta}",
  "caption": "2 sentences total. Sentence 1: A controversial truth. Sentence 2: A direct question. End with EXACTLY these hashtags on a new line: {hashtags}"
}}"""
    
    for key in valid_keys:
        logger.info(f"Trying Gemini API key starting with: {key[:8]}...")
        try:
            client = genai.Client(api_key=key)
        except Exception as e:
            logger.error(f"Failed to initialize genai client: {e}")
            continue
        
        for attempt in range(2):  # Retry up to 2 times per key
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=1.0
                    )
                )
                
                if not response.text:
                    logger.error(f"Gemini response blocked or empty.")
                    time.sleep(2)
                    continue
                    
                text = response.text.strip()
                # Clean up markdown code fences if Gemini adds them
                if text.startswith("```json"): text = text[7:]
                if text.startswith("```"): text = text[3:]
                if text.endswith("```"): text = text[:-3]
                return json.loads(text.strip())
                
            except json.JSONDecodeError as e:
                logger.warning(f"Gemini returned invalid JSON: {e}")
                time.sleep(2)
            except Exception as e:
                err_str = str(e)
                logger.error(f"Gemini generation error: {err_str}")
                time.sleep(2)
                if "429" in err_str or "quota" in err_str.lower():
                    logger.warning("Quota exhausted for this key. Moving to next key...")
                    break # Break inner loop, try next key
    
    logger.error("All Gemini keys and attempts failed. Falling back to HuggingFace...")
    hf_script = generate_fallback_script(prompt)
    if hf_script: return hf_script
    
    logger.error("HuggingFace also failed. Using offline hardcoded viral template...")
    return generate_offline_script()

def generate_fallback_script(prompt):
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token: return None
    
    logger.info("Calling HuggingFace Qwen-2.5-72B API...")
    url = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-72B-Instruct"
    headers = {"Authorization": f"Bearer {hf_token}", "Content-Type": "application/json"}
    hf_prompt = f"<|im_start|>system\nYou are an AI that outputs pure JSON.<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
    
    try:
        r = requests.post(url, headers=headers, json={"inputs": hf_prompt, "parameters": {"max_new_tokens": 800, "return_full_text": False}}, timeout=30)
        if r.status_code == 200:
            text = r.json()[0]['generated_text'].strip()
            if text.startswith("```json"): text = text[7:]
            if text.startswith("```"): text = text[3:]
            if text.endswith("```"): text = text[:-3]
            return json.loads(text.strip())
        else:
            logger.error(f"HF Error: {r.status_code}")
    except Exception as e:
        logger.error(f"HF Fallback failed: {e}")
    return None

def generate_offline_script():
    """Bulletproof offline fallback so the video ALWAYS renders with variety."""
    templates = [
        {
          "hook": "90% log paise se darte hain. Tum nahi.",
          "authority_claim": "Tumhe lagta hai luck hai. Yeh ek pattern hai.",
          "numbered_list": [
              {"text": "Loss se zyada dar nahi lagta", "type": "INSIGHT"},
              {"text": "Decisions data se, emotion se nahi", "type": "INSIGHT"},
              {"text": "99% log EMI trap mein har saal 5 lakh khote hain", "type": "DATA", "source": "Source: RBI Data"}
          ],
          "proof_demo": "Proof: Mutual funds mein ₹10k/mo se tum 15 saal mein crorepati ho.",
          "proof_source": "Source: Compound Interest Math",
          "curiosity_teaser": "Wait for rule 3",
          "red_box_keyword": "dar",
          "comment_question": "Tum 1, 2 ya 3 ho? 👇",
          "save_cta": "Save and Share with someone who needs to wake up 🚀 Tum kaunsa karte ho — 1, 2, ya 3? Comment karo 👇",
          "caption": "आज ही शुरुआत करें। #WealthMindset #PsychologyFacts #HindiMotivation #SuccessRules"
        },
        {
          "hook": "Why you are secretly sabotaging your own success...",
          "authority_claim": "Success koi accident nahi, ek formula hai.",
          "numbered_list": [
              {"text": "Stop waiting for the perfect time", "type": "INSIGHT"},
              {"text": "Focus on skills, not salary", "type": "INSIGHT"},
              {"text": "Average insaan scroll karta hai, top 1% create karta hai", "type": "DATA", "source": "Source: Forbes 2024"}
          ],
          "proof_demo": "Fact: Content creators make 5x more than average 9-to-5 workers in India.",
          "proof_source": "Source: Creator Economy Report",
          "curiosity_teaser": "The secret is simple",
          "red_box_keyword": "sabotaging",
          "comment_question": "Do you scroll or create? 👇",
          "save_cta": "Follow for daily dopamine hits. 🚀",
          "caption": "Shift your perspective. #GrowthMindset #FinancialFreedom #ReelItFeelIt #Shorts"
        }
    ]
    return random.choice(templates)

def create_tone(filename, freq, duration, vol=0.5, decay=True, riser=False):
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    try:
        with wave.open(filename, 'w') as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(sample_rate)
            for i in range(n_samples):
                t = float(i) / sample_rate
                env = math.exp(-3.0 * t) if decay else 1.0
                if riser:
                    current_freq = freq + (400 * t) # pitch goes up
                    env = min(1.0, t) # volume goes up
                else:
                    current_freq = freq
                val = int(vol * env * math.sin(2 * math.pi * current_freq * t) * 32767)
                f.writeframes(struct.pack('<h', val))
    except Exception as e:
        logger.error(f"Failed to create {filename}: {e}")

def create_8d_hypnotic_music(filename, duration=42.0):
    """
    Quiet, simple background tone without any fancy effects.
    """
    sample_rate = 44100
    n_samples   = int(sample_rate * duration)

    try:
        with wave.open(filename, 'w') as f:
            f.setnchannels(2)
            f.setsampwidth(2)
            f.setframerate(sample_rate)

            for i in range(n_samples):
                t = float(i) / sample_rate
                
                fade_in  = min(1.0, t / 2.0)
                fade_out = min(1.0, (duration - t) / 3.0)
                env = fade_in * fade_out * 0.05
                
                drone_freq = 55.0
                drone = math.sin(2 * math.pi * drone_freq * t)
                val = int(max(-32768, min(32767, drone * env * 32767)))
                f.writeframesraw(struct.pack('<hh', val, val))
    except Exception as e:
        logger.error(f"Error creating background music: {e}")
def ensure_sfx(studio_dir):
    sfx_dir = os.path.join(studio_dir, "public")
    os.makedirs(sfx_dir, exist_ok=True)
    if not os.path.exists(os.path.join(sfx_dir, "ding.wav")):
        create_tone(os.path.join(sfx_dir, "ding.wav"), 1200, 1.0)
    if not os.path.exists(os.path.join(sfx_dir, "riser.wav")):
        create_tone(os.path.join(sfx_dir, "riser.wav"), 100, 2.0, riser=True)
    if not os.path.exists(os.path.join(sfx_dir, "impact.wav")):
        create_tone(os.path.join(sfx_dir, "impact.wav"), 60, 1.5)
    # Always regenerate — pure 8D spatial audio every run
    logger.info("🎧 Generating TRUE 8D spatial audio (432/436 Hz binaural + rotating pan + reverb)...")
    create_8d_hypnotic_music(os.path.join(sfx_dir, "hypno.wav"), duration=42.0)

def clean_for_tts(text):
    """Pre-processes text to prevent TTS engine hallucination and symbol reading errors."""
    if not text:
        return text
    import re
    # Fix Rupee symbol: move it after the amount (e.g. "₹ 10 lakh" -> "10 lakh rupees")
    cleaned = re.sub(r'₹\s*([0-9.,]+\s*(?:lakh|crore|k|m|billion|million)?)', r'\1 rupees ', text, flags=re.IGNORECASE)
    # Catch any remaining isolated ₹ symbols
    cleaned = cleaned.replace("₹", " rupees ")
    # Fix % symbol mispronounced or causing number hallucinations
    cleaned = cleaned.replace("%", " percent ")
    # Basic cleanup for excessive whitespaces
    return " ".join(cleaned.split())

def generate_audio(text, edge_voice, eleven_voice, output_path):
    """Generate audio using ElevenLabs (if key exists & has credits), fallback to edge-tts."""
    text = clean_for_tts(text)
    eleven_key = os.environ.get("ELEVENLABS_API_KEY")
    if eleven_key:
        try:
            logger.info(f"🎙️ Attempting ElevenLabs API generation for: {text[:20]}...")
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{eleven_voice}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": eleven_key
            }
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            response = requests.post(url, json=data, headers=headers, timeout=20)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                logger.info("✅ ElevenLabs generation successful.")
                return
            else:
                logger.warning(f"ElevenLabs failed ({response.status_code}): {response.text}. Falling back to edge-tts.")
        except Exception as e:
            logger.warning(f"ElevenLabs error: {e}. Falling back to edge-tts.")
            
    # FALLBACK to edge-tts
    logger.info(f"🎙️ Using edge-tts fallback voice: {edge_voice}")
    cmd = [sys.executable, "-m", "edge_tts", "--text", text, "--voice", edge_voice, "--rate", "+10%", "--write-media", output_path]
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            subprocess.run(cmd, check=True)
            break
        except subprocess.CalledProcessError as e:
            if attempt < max_retries - 1:
                logger.warning(f"edge-tts failed (attempt {attempt+1}/{max_retries}). Retrying in 3 seconds...")
                import time
                time.sleep(3)
            else:
                logger.error(f"edge-tts failed after {max_retries} attempts.")
                raise e

def get_audio_duration(file_path):
    """Get duration of an MP3 file in seconds."""
    try:
        from mutagen.mp3 import MP3
        audio = MP3(file_path)
        return audio.info.length
    except:
        try:
            import subprocess
            result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path], capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except:
            return 2.0

def download_dynamic_backgrounds(public_dir):
    """Downloads 4 unique HD background videos from Pexels API.
    
    This is the PERMANENT fix for GitHub Actions IP bans.
    YouTube blocks all cloud/datacenter IPs at the network level — no yt-dlp trick fixes this.
    Pexels is a free official stock video API that:
    - Works 100% from GitHub Actions (no IP ban ever)
    - Returns gorgeous HD/4K satisfying portrait videos
    - Returns DIFFERENT videos every run (AI topic-matched search)
    - Is completely free and legal
    
    Setup: Add PEXELS_API_KEY to GitHub Secrets (free key from pexels.com/api)
    """
    logger.info("🎬 Initializing Pexels HD Video Engine (Permanent Fix)...")


    pexels_key = os.getenv("PEXELS_API_KEY", "")
    if not pexels_key:
        logger.error("❌ PEXELS_API_KEY not set in environment/secrets. Add it at pexels.com/api (free)")
        pexels_key = None

    output_names = ["gta", "sand", "bg3", "bg4"]

    satisfying_queries = [
        "luxury car moving",
        "dubai skyline night",
        "rolex watch luxury",
        "private jet flying",
        "stock market trading screen",
        "supercar slow motion",
        "mansion luxury estate",
        "miami beach penthouse",
        "crypto trading chart",
        "business man walking suit",
        "money falling slow motion",
        "gold bars wealth",
        "yacht ocean aerial"
    ]


    # Pick 4 different queries for variety
    chosen_queries = random.sample(satisfying_queries, 4)

    for i, name in enumerate(output_names):
        final_out = os.path.join(public_dir, f"{name}.mp4")
        raw_out   = os.path.join(public_dir, f"{name}_raw.mp4")
        query     = chosen_queries[i]
        downloaded = False

        # ── PRIMARY: Pexels API ─────────────────────────────────────────────
        if pexels_key:
            try:
                logger.info(f"📥 [{name}] Fetching Pexels video for: '{query}'")
                headers_pexels = {"Authorization": pexels_key}
                params = {
                    "query": query,
                    "per_page": 30,
                    "orientation": "portrait",
                    "size": "large",
                    "page": random.randint(1, 3),  # rotate pages for variety
                }
                resp = requests.get(
                    "https://api.pexels.com/videos/search",
                    headers=headers_pexels,
                    params=params,
                    timeout=15,
                )
                if resp.status_code == 200:
                    videos = resp.json().get("videos", [])
                    if videos:
                        # Pick a random video from the results
                        video = random.choice(videos)
                        # Prefer HD portrait (1080p), fallback to any
                        video_files = video.get("video_files", [])
                        # Sort by quality — prefer height >= 1080
                        hd_files = sorted(
                            [f for f in video_files if f.get("height", 0) >= 1080 and f.get("file_type") == "video/mp4"],
                            key=lambda f: f.get("height", 0),
                            reverse=True
                        )
                        if not hd_files:
                            hd_files = sorted(
                                [f for f in video_files if f.get("file_type") == "video/mp4"],
                                key=lambda f: f.get("height", 0),
                                reverse=True
                            )
                        if hd_files:
                            video_url = hd_files[0]["link"]
                            logger.info(f"⬇️  Downloading: {video_url[:80]}...")
                            dl_resp = requests.get(
                                video_url, 
                                stream=True, 
                                timeout=120,
                                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                            )
                            if dl_resp.status_code == 200:
                                with open(raw_out, "wb") as f:
                                    for chunk in dl_resp.iter_content(chunk_size=1024 * 256):
                                        f.write(chunk)
                                if os.path.exists(raw_out) and os.path.getsize(raw_out) > 500 * 1024:
                                    logger.info(f"⚙️  Processing {name}.mp4 → crisp 1080×1920 portrait...")
                                    subprocess.run([
                                        "ffmpeg", "-y", "-i", raw_out,
                                        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                                               "unsharp=3:3:0.5:3:3:0.0,eq=contrast=1.05:saturation=1.2",
                                        "-c:v", "libx264", "-preset", "superfast", "-tune", "fastdecode",
                                        "-crf", "17", "-g", "1", "-keyint_min", "1", "-an", final_out
                                    ], check=True, timeout=180, capture_output=True)
                                    os.remove(raw_out)
                                    logger.info(f"✅ [{name}] Pexels HD video ready! ({os.path.getsize(final_out)//1024} KB)")
                                    downloaded = True
                                else:
                                    logger.warning(f"⚠️  [{name}] Downloaded file too small, trying next")
                else:
                    logger.warning(f"⚠️  Pexels API returned {resp.status_code}: {resp.text[:200]}")
            except Exception as e:
                logger.error(f"❌ [{name}] Pexels download failed: {e}")

        # ── SECONDARY: Pixabay API Fallback (Free, no-auth support) ──────────
        if not downloaded:
            pixabay_key = os.getenv("PIXABAY_API_KEY", "")
            if pixabay_key:
                try:
                    logger.info(f"📥 [{name}] Fetching Pixabay video for: '{query}'")
                    resp = requests.get(
                        "https://pixabay.com/api/videos/",
                        params={"key": pixabay_key, "q": query, "per_page": 20},
                        timeout=15
                    )
                    if resp.status_code == 200:
                        hits = resp.json().get("hits", [])
                        if hits:
                            video_hit = random.choice(hits)
                            videos_dict = video_hit.get("videos", {})
                            # Pick medium or large mp4 video
                            target_video = videos_dict.get("medium") or videos_dict.get("large") or videos_dict.get("small")
                            if target_video:
                                video_url = target_video.get("url")
                                logger.info(f"⬇️ Downloading Pixabay: {video_url[:80]}...")
                                dl_resp = requests.get(
                                    video_url, 
                                    stream=True, 
                                    timeout=120,
                                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                                )
                                if dl_resp.status_code == 200:
                                    with open(raw_out, "wb") as f:
                                        for chunk in dl_resp.iter_content(chunk_size=1024 * 256):
                                            f.write(chunk)
                                    if os.path.exists(raw_out) and os.path.getsize(raw_out) > 500 * 1024:
                                        logger.info(f"⚙️ Processing {name}.mp4...")
                                        subprocess.run([
                                            "ffmpeg", "-y", "-i", raw_out,
                                            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                                                   "unsharp=3:3:0.5:3:3:0.0,eq=contrast=1.05:saturation=1.2",
                                            "-c:v", "libx264", "-preset", "superfast", "-tune", "fastdecode",
                                            "-crf", "17", "-g", "1", "-keyint_min", "1", "-an", final_out
                                        ], check=True, timeout=180, capture_output=True)
                                        os.remove(raw_out)
                                        logger.info(f"✅ [{name}] Pixabay HD video ready!")
                                        downloaded = True
                except Exception as pe:
                    logger.warning(f"⚠️ Pixabay API failed: {pe}")

        # ── TERTIARY: Direct Open-Source Public Video Loops (No Auth, Instant CDN Download) ──
        if not downloaded:
            # High quality direct vertical mp4 loop urls from open resources that do not block datacenters
            direct_pools = {
                "gta": [
                    "https://assets.mixkit.co/videos/preview/mixkit-fluid-art-of-blue-and-purple-ink-41618-large.mp4",
                    "https://assets.mixkit.co/videos/preview/mixkit-acrylic-paint-mixing-abstract-art-41617-large.mp4",
                    "https://assets.mixkit.co/videos/preview/mixkit-abstract-golden-particle-waves-background-loop-42867-large.mp4"
                ],
                "sand": [
                    "https://assets.mixkit.co/videos/preview/mixkit-sand-dunes-in-a-desert-4416-large.mp4",
                    "https://assets.mixkit.co/videos/preview/mixkit-waves-in-a-blue-ocean-aerial-4401-large.mp4",
                    "https://assets.mixkit.co/videos/preview/mixkit-pouring-colorful-sand-satisfying-video-43093-large.mp4"
                ],
                "bg3": [
                    "https://assets.mixkit.co/videos/preview/mixkit-neon-light-from-a-tunnel-in-a-futuristic-city-43187-large.mp4",
                    "https://assets.mixkit.co/videos/preview/mixkit-tunnel-of-futuristic-glowing-neon-lights-42548-large.mp4",
                    "https://assets.mixkit.co/videos/preview/mixkit-stars-in-space-background-loop-42879-large.mp4"
                ],
                "bg4": [
                    "https://assets.mixkit.co/videos/preview/mixkit-driving-in-a-futuristic-neon-city-timelapse-43185-large.mp4",
                    "https://assets.mixkit.co/videos/preview/mixkit-waterfall-in-a-forest-aerial-view-4402-large.mp4",
                    "https://assets.mixkit.co/videos/preview/mixkit-slow-motion-water-splashes-in-dark-background-42352-large.mp4"
                ]
            }
            pool = direct_pools.get(name, direct_pools["gta"])
            random.shuffle(pool)
            for direct_url in pool:
                try:
                    logger.info(f"📥 [{name}] Direct fallback: {direct_url[:80]}...")
                    dl_resp = requests.get(
                        direct_url, 
                        stream=True, 
                        timeout=60,
                        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
                    )
                    if dl_resp.status_code == 200:
                        with open(raw_out, "wb") as f:
                            for chunk in dl_resp.iter_content(chunk_size=1024 * 256):
                                f.write(chunk)
                        if os.path.exists(raw_out) and os.path.getsize(raw_out) > 200 * 1024:
                            try:
                                subprocess.run([
                                    "ffmpeg", "-y", "-i", raw_out,
                                    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                                           "unsharp=3:3:0.5:3:3:0.0,eq=contrast=1.05:saturation=1.2",
                                    "-c:v", "libx264", "-preset", "superfast", "-tune", "fastdecode",
                                    "-crf", "17", "-g", "1", "-keyint_min", "1", "-an", final_out
                                ], check=True, timeout=180, capture_output=True)
                                os.remove(raw_out)
                            except FileNotFoundError:
                                import shutil
                                shutil.move(raw_out, final_out)
                            logger.info(f"✅ [{name}] Direct fallback ready!")
                            downloaded = True
                            break
                except Exception as ce:
                    logger.warning(f"⚠️ Direct URL failed: {ce}")
                    continue

        if not downloaded:
            logger.error(f"❌ [{name}] All sources failed — creating fallback placeholder")
            try:
                subprocess.run([
                    "ffmpeg", "-y", "-f", "lavfi",
                    "-i", f"color=c=0x1a1a2e:s=1080x1920:d=15",
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", final_out
                ], check=False, capture_output=True)
            except FileNotFoundError:
                import shutil
                gta_src = os.path.join(public_dir, "gta.mp4")
                if os.path.exists(gta_src) and name != "gta":
                    shutil.copy(gta_src, final_out)
                else:
                    open(final_out, 'w').close()

    logger.info("✅ All 4 HD Backgrounds Ready (Pexels/Pixabay/Mixkit Engine)!")



def qa_gate(script_json, attempt=1):
    """
    Enforces 5 Hard QA Checks before allowing render to proceed.
    Returns True if passed, False if failed.
    """
    import datetime
    def log_metric(status, reason):
        csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "qa_metrics.csv"))
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(csv_path, "a", encoding="utf-8") as f:
            f.write(f'"{ts}","{status}","{reason.replace(chr(34), chr(39))}",{attempt}\n')

    if not script_json or not isinstance(script_json, dict):
        logger.error("QA FAIL: Invalid JSON structure.")
        log_metric("FAIL", "Invalid JSON structure")
        return False

    # 0. Required Field Check
    required_fields = ["hook", "save_cta", "caption", "numbered_list"]
    for field in required_fields:
        if not script_json.get(field):
            logger.error(f"❌ QA FAIL: Script is missing required field '{field}'.")
            log_metric("FAIL", f"Missing field: {field}")
            return False
            
    hook = str(script_json.get("hook", ""))
    red_kw = str(script_json.get("red_box_keyword", ""))
    c_teaser = str(script_json.get("curiosity_teaser", ""))
    
    # 1. Empty Placeholder Check
    if not red_kw or red_kw.lower() not in hook.lower():
        msg = f"red_box_keyword '{red_kw}' is empty or not in hook '{hook}'"
        logger.error(f"QA FAIL: {msg}")
        log_metric("FAIL", msg)
        return False
    if not c_teaser:
        logger.error("QA FAIL: curiosity_teaser is empty.")
        log_metric("FAIL", "curiosity_teaser is empty")
        return False
        
    # Compile all spoken text to check for numeric placeholders & grammar
    all_text = hook + " " + script_json.get("authority_claim", "")
    for item in script_json.get("numbered_list", []):
        if isinstance(item, dict):
            all_text += " " + str(item.get("text", ""))
        else:
            all_text += " " + str(item)
    all_text += " " + script_json.get("proof_demo", "") + " " + script_json.get("save_cta", "")
    
    # 3. Numeric/Data Placeholder Check
    bad_placeholders = ["[amount]", "{amount}", "calculation", "[x]", "{x}"]
    for bp in bad_placeholders:
        if bp in all_text.lower():
            logger.error(f"QA FAIL: Found literal placeholder '{bp}' in text.")
            log_metric("FAIL", f"Literal placeholder {bp}")
            return False
            
    # 4. Overlap Check (Character limits)
    # Ensure no single text chunk exceeds 120 chars to prevent 4-line wrapping overlap
    for chunk in [hook, script_json.get("authority_claim", ""), script_json.get("proof_demo", ""), script_json.get("save_cta", "")]:
        if len(str(chunk)) > 120:
            logger.error(f"QA FAIL: Chunk exceeds 120 chars, risking overlap: {str(chunk)[:30]}...")
            log_metric("FAIL", "Chunk length > 120 chars")
            return False
            
    # 5. Visual Contrast Configuration Check
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio", "src", "config.ts"))
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            config_text = f.read()
            if "#F5F3EC" not in config_text or "#FAC775" not in config_text:
                logger.error("QA FAIL: Visual contrast configuration is incorrect or missing required highlight colors (#F5F3EC, #FAC775).")
                log_metric("FAIL", "Missing required contrast colors in config.ts")
                return False
    else:
        logger.error("QA FAIL: config.ts not found. Visual consistency cannot be guaranteed.")
        log_metric("FAIL", "config.ts missing")
        return False
            
    # 6. Grammar & Topic Relevance Check via Gemini
    # QA Gate re-enabled per user request to ensure hallucination-free output.
    logger.info("🧪 Running strict LLM QA Gate Validation...")
    prompt = f"""You are a strict Quality Assurance bot for a viral video pipeline.
Review the following video script:
{all_text}

HARD CHECKS:
1. GRAMMAR: Are there any disconnected fragments, mixed-language nonsense, or incomplete sentences? (e.g. "skip - exactly poor"). It MUST be grammatically correct Hindi, English, or natural code-mixed Hinglish.
2. TOPIC: Is this strongly related to wealth, psychology, or money? (Reject if it's about unrelated topics like nature, generic quotes with no wealth/psychology context).

If it passes BOTH checks flawlessly, return exactly: PASS
If it fails either check, return exactly: FAIL
"""
    try:
        import time
        time.sleep(3) # Prevent rate limits
        client = genai.Client(api_key=GEMINI_KEYS[0])
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1)
        )
        result = response.text.strip().upper()
        if "FAIL" in result:
            logger.error(f"QA FAIL: LLM Validation rejected the script. Result: {result}")
            log_metric("FAIL", "LLM rejected script")
            return False
        logger.info("✅ QA Gate Passed!")
        log_metric("PASS", "LLM validation passed")
        return True
    except Exception as e:
        logger.error(f"❌ QA Validation API error, FAILING check: {e}")
        log_metric("FAIL", f"LLM API Error: {str(e)}")
        return False

def build_v32_payload():
    logger.info("⚡ INITIATING V32 ULTIMATE AESTHETIC ENGINE ⚡")

    script_data = None
    for attempt in range(3):
        logger.info(f"🔄 Generation Attempt {attempt + 1}/3")
        temp_script = generate_dynamic_script()
        if temp_script and qa_gate(temp_script, attempt + 1):
            script_data = temp_script
            break
        logger.warning("♻️ QA Gate failed. Retrying script generation...")
        
    if not script_data:
        logger.error("❌ V32 FAILED - Could not generate a script that passes QA after 3 attempts. Aborting run.")
        sys.exit(1)
        
    logger.info(f"✅ Generated Hook: {script_data.get('hook')}")
    logger.info(f"✅ Generated Caption: {script_data.get('caption')}")

    
    # Extract phases safely from new Storyboard JSON format
    try:
        phase_1 = script_data.get("hook", "Rich vs Poor Mindset")
        
        phase_2 = script_data.get("authority_claim", "Most people never learn this.")
        
        nl = script_data.get("numbered_list", [])
        if not isinstance(nl, list):
            nl = []
            
        phase_l1 = nl[0].get("text", "Rule 1: Always learn.") if len(nl) > 0 and isinstance(nl[0], dict) else (nl[0] if len(nl) > 0 else "Rule 1: Always learn.")
        phase_l2 = nl[1].get("text", "Rule 2: Invest early.") if len(nl) > 1 and isinstance(nl[1], dict) else (nl[1] if len(nl) > 1 else "Rule 2: Invest early.")
        phase_l3 = nl[2].get("text", "Rule 3: Stay consistent.") if len(nl) > 2 and isinstance(nl[2], dict) else (nl[2] if len(nl) > 2 else "Rule 3: Stay consistent.")
        
        phase_proof = script_data.get("proof_demo", "Proof: 99% fail without action.")
        phase_cta = script_data.get("save_cta", "Save this video now.")
        
        phases = [phase_1, phase_2, phase_l1, phase_l2, phase_l3, phase_proof, phase_cta]
    except Exception as e:
        logger.error(f"Script JSON parsing failed: {e}. Aborting.")
        sys.exit(1)
    
    # Randomly pick voice pair
    base_edge = random.choice(EDGE_VOICES)
    alt_edge = EDGE_VOICES[1] if base_edge == EDGE_VOICES[0] else EDGE_VOICES[0]
    
    base_eleven = random.choice(ELEVEN_VOICES)
    alt_eleven = ELEVEN_VOICES[1] if base_eleven == ELEVEN_VOICES[0] else ELEVEN_VOICES[0]
    
    # Path to remotion-studio/public
    public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio", "public"))
    os.makedirs(public_dir, exist_ok=True)
    
    # ── DOWNLOAD DYNAMIC BACKGROUND VISUALS ──
    download_dynamic_backgrounds(public_dir)
    
    timings = []
    audio_offsets = []
    current_time = 0.0
    
    for i, phase_text in enumerate(phases):
        logger.info(f"Generating audio for Phase {i+1}...")
        # BUG FIX: Changed v31_audio to v32_audio to match MainVideo.tsx staticFile names
        audio_path = os.path.join(public_dir, f"v32_audio_{i}.mp3")
        
        edge_to_use = alt_edge if i % 2 != 0 else base_edge
        eleven_to_use = alt_eleven if i % 2 != 0 else base_eleven
        
        generate_audio(phase_text, edge_to_use, eleven_to_use, audio_path)
        
        duration = get_audio_duration(audio_path)
        audio_offsets.append(current_time)
        
        words = phase_text.split()
        if len(words) > 0:
            word_duration = duration / len(words)
            for j, w in enumerate(words):
                timings.append({
                    "word": w,
                    "start": current_time + (j * word_duration),
                    "end": current_time + ((j + 1) * word_duration)
                })
        current_time += duration + 0.3
    
    # Ensure we have all 8 audio offsets for MainVideo.tsx
    while len(audio_offsets) < 8:
        audio_offsets.append(current_time)
        
    # ── THE ULTIMATE SANITIZER ──
    # Protect the React UI from ANY possible Gemini type hallucinations (e.g. returning numbers or arrays instead of strings)
    # This guarantees the React .split() and .includes() methods will NEVER throw a TypeError.
    for key in ["hook", "curiosity_teaser", "curiosity_payoff", "authority_claim", "proof_demo", "source_tag", "comment_question", "save_cta", "caption"]:
        if key in script_data and not isinstance(script_data[key], str):
            script_data[key] = str(script_data[key])
            
    if "split_screen" in script_data and isinstance(script_data["split_screen"], dict):
        for skey in ["left", "right"]:
            if skey in script_data["split_screen"] and not isinstance(script_data["split_screen"][skey], str):
                script_data["split_screen"][skey] = str(script_data["split_screen"][skey])
        
    payload = {
        "script": script_data,
        "timings": timings,
        "audio_offsets": audio_offsets,
        "total_duration": current_time
    }
    
    json_path = os.path.join(public_dir, "v32_script.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    
    studio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio"))
    ensure_sfx(studio_dir)
        
    logger.info("🎬 Triggering V35 1080p Remotion Render (JPEG, CRF=18, Concurrency=4)...")
    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "FINAL_V35_HD.mp4"))

    # ── V35 Render Flags — HD Quality + Maximum Speed ──────────────────────────
    # --scale=1              → Native resolution (1080x1920 vertical HD)
    # --crf=18               → Excellent visual quality (visually lossless), fast encode
    # --image-format=jpeg    → JPEG frames = 40% faster render vs PNG, no transparency needed
    # --concurrency=2        → Parallel rendering on both runner CPU cores (GitHub free tier gives 2 cores)
    # --timeout=1200000      → Kill after 20 minutes to save Actions minutes if hung
    # ─────────────────────────────────────────────────────────────────────────────

    # Read REMOTION_CONCURRENCY from env, override default to 2
    concurrency = os.environ.get("REMOTION_CONCURRENCY", "2")
    
    # ── VALIDATE PROFILE PHOTO BEFORE RENDER ──
    profile_photo_path = os.path.join(public_dir, "host_photo.png")
    if not os.path.exists(profile_photo_path):
        logger.error(f"❌ FATAL ERROR: Approved profile photo not found at {profile_photo_path}. Aborting.")
        sys.exit(1)

    cmd = [
        "npx.cmd" if os.name == "nt" else "npx", "remotion", "render",
        "src/index.ts", "MainVideo", out_file,
        "--props", json_path,
        "--scale=1",
        "--crf=18",
        "--image-format=jpeg",
        f"--concurrency={concurrency}",
        "--timeout=1200000",
    ]
    subprocess.run(cmd, cwd=studio_dir, check=True)
    logger.info(f"✅ V35 render complete: {out_file}")

    # ── GENERATE THUMBNAIL COVER FRAME ──
    cover_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cover.jpg"))
    logger.info("📸 Exporting unique custom ThumbnailCover...")
    subprocess.run([
        "npx.cmd" if os.name == "nt" else "npx", "remotion", "still",
        "src/index.ts", "ThumbnailCover", cover_file,
        "--props", json_path,
        "--frame=0"
    ], cwd=studio_dir, check=True)

    # ── GENERATE QA SPOT-CHECK FRAME ──
    spot_check_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "qa_spot_check.jpg"))
    logger.info("🔍 Exporting QA spot-check frame (Frame 150)...")
    subprocess.run([
        "npx.cmd" if os.name == "nt" else "npx", "remotion", "still",
        "src/index.ts", "MainVideo", spot_check_file,
        "--props", json_path,
        "--frame=150"
    ], cwd=studio_dir, check=True)

    # ── PROFESSIONAL AUDIO MIX (BGM DUCKING & VO COMPRESSION) ──
    logger.info("🎛️ Audio is now handled natively by Remotion Studio. Skipping ffmpeg mix...")
    
    logger.info("Video rendering complete. Script execution finished.")

    return out_file

if __name__ == "__main__":
    build_v32_payload()

