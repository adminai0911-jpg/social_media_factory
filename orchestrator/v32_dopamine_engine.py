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

VOICES = [
    "hi-IN-MadhurNeural", # Male
    "hi-IN-SwaraNeural",  # Female
]


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

        # 🏆 CATEGORY 4: AUTHORITY + PROOF — Builds instant credibility and trust
        "Dhirubhai Ambani, Rakesh Jhunjhunwala — दोनों ने यह एक rule follow किया।",
        "Harvard Business Study says: 92% of middle class makes THIS mistake before 35.",
        "Warren Buffett ने यह rule 14 साल की उम्र में सीखा। आप आज सीखोगे।",
        "The wealth rule that took me 7 years to learn — in 60 seconds.",

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

    prompt = f"""You are the world's most elite viral content strategist — combining the psychological precision of Robert Cialdini, the storytelling of Gary Vee, and the wealth knowledge of Naval Ravikant — specifically optimized for Indian short-form video (Instagram Reels, YouTube Shorts, Facebook Reels).

═══════════════════════════════════════════════
DUAL MISSION (BOTH are non-negotiable):
═══════════════════════════════════════════════
1. PSYCHOLOGICAL AGGRESSION: Every second of the video must be so gripping the viewer physically cannot scroll away.
2. GENUINE DEEP VALUE: Every insight must be so real, specific, and actionable that the viewer feels they just learned something worth ₹10,000. This is what builds loyal followers who keep coming back.

The SECRET formula of the most viral Indian finance accounts (FinancewithSharan, Ankur Warikoo, CA Rachana): They are AGGRESSIVE enough to stop the scroll AND VALUABLE enough to earn the save and share. Your script must do BOTH.

═══════════════════════════════════════════════
6 PSYCHOLOGICAL WEAPONS (USE ALL 6):
═══════════════════════════════════════════════
1. CURIOSITY GAP: The hook opens a mental loop. The only way to close it is to watch to the end. Never answer the hook's question before the final 5 seconds.
2. IDENTITY MIRROR: Every line should make the viewer feel "This is talking directly to ME." Use "tum", "tumhara", "tum log" — never generic "log" or "people."
3. SPECIFIC NUMBERS: Vague claims are ignored. Specific numbers are believed. Use exact figures: "₹43,847", "73% of Indians under 35", "18 months", "Mukesh Ambani was 24 when he did this." (CRITICAL: THESE ARE JUST EXAMPLES. DO NOT COPY THEM. INVENT COMPLETELY NEW AND UNIQUE NUMBERS/PERCENTAGES EVERY TIME).
4. LOSS AVERSION (2X POWER): The human brain reacts to loss 2.5x more strongly than gain. Frame every insight as something the viewer is CURRENTLY LOSING if they don't know this.
5. SOCIAL PROOF ESCALATION: Reference real people, real studies, real companies. "Warren Buffett", "IIM study", "Zerodha data shows" — these phrases make viewers trust and share immediately.
6. DOPAMINE MICRO-REWARDS: Every 3-4 seconds must deliver a NEW surprising fact, number, or insight. This creates a chemical dopamine loop that makes the video literally addictive to watch.
7. ABSOLUTE UNIQUENESS & REAL DATA: You MUST generate completely unique angles and topics every single time without repeating yourself. However, EVERY STATISTIC, NUMBER, AND FACT MUST BE 100% REAL AND VERIFIABLE. DO NOT HALLUCINATE OR INVENT FAKE DATA. Use different, REAL financial statistics from credible sources for each script.

═══════════════════════════════════════════════
CONTENT QUALITY RULES (NON-NEGOTIABLE):
═══════════════════════════════════════════════
- Language: Natural Hinglish — the way a brilliant, wealthy friend speaks over chai. NOT formal textbook Hindi.
- GRAMMAR QA PASS: Ensure every generated sentence is a complete, grammatically correct thought in either English or Hindi. Reject and rewrite any broken fragments (e.g., 'Dhirubhai Ambani, Rakesh Jhunjhunwala — rule follow'). Do not mix English and Hindi into a non-grammatical fragment.
- ZERO generic advice: Never say "work hard", "save money", "be disciplined." These are content killers.
- Every insight MUST be counterintuitive — something that surprises even a financially aware person.
- The numbered list must teach a COMPLETE, ACTIONABLE mini-framework — not just disconnected tips.
- proof_demo MUST name a real person (Indian preferred: Ambani, Premji, Bajaj, Rakesh Jhunjhunwala) or a credible study.
- This is Part {series_part} of 3 in a series. If hook mentions a series part number, use {series_part}.
- End with an OPEN LOOP: tease something even bigger in the next video to force follows.
- Length constraint: Total spoken words must map to a 35-45 second video. Be punchy. Trim anything that repeats information.
- Return ONLY raw JSON. No markdown. No backticks. No explanation text.

Mandatory: hook MUST use this text exactly: {hook}
Mandatory: save_cta MUST use this text exactly: {cta}

JSON Schema:
{{
  "hook": "{hook}",
  "curiosity_teaser": "An open loop question or incomplete thought related to the hook. Max 6 words. Example: '₹847 ka asli sach?' or 'Sirf 1% log jaante hain...'",
  "curiosity_payoff": "The explicit resolution to the curiosity_teaser, revealed during the proof section to close the loop. Max 8 words. Example: 'Yahi ₹847 tumhara loss hai.'",
  "split_screen": {{
    "left": "BROKE trap: [The single most PAINFUL and SPECIFIC behavior keeping 90% of Indians poor — max 6 words. Must sting.]",
    "right": "WEALTH move: [The counterintuitive, surprising behavior of top 1% Indians — max 6 words. Must inspire.]"
  }},
  "authority_claim": "ONE brutal, specific, stat-backed truth bomb that makes the viewer's jaw drop. Must include a real Rupee amount OR a real percentage OR a real Indian name. Sound like a professor who has seen behind the curtain. MAX 18 words.",
  "numbered_list": [ // MUST BE EXACTLY 3 ITEMS. NO MORE. NO LESS.
    "Rule 1: [A counterintuitive, specific, actionable wealth rule with a number. Something a rich dad teaches his son. Max 10 words.]",
    "Rule 2: [A dark psychological truth about money that most people are too scared to admit about themselves. Max 10 words.]",
    "Rule 3: [A SHOCKING, jaw-dropping statistic with a real Rupee figure or percentage that reframes everything. Max 12 words. This is the 'Aha!' moment.]"
  ],
  "proof_demo": "Real-world proof using a NAMED Indian or global billionaire, or a credible institution (IIM, RBI, SEBI, Forbes). Make it feel like insider knowledge. Example: 'Rakesh Jhunjhunwala ne 5,000 se shuru kiya tha — 40,000 crore banaye. Yahi rule use kiya.' MAX 15 words.",
  "proof_source": "ONE real, verifiable source for the proof_demo claim (e.g. 'Source: Forbes India 2024' or 'Source: RBI Annual Report 2025'). ONLY add if the claim is real and verifiable. If not verifiable, return empty string.",
  "source_tag": "ONE short, real, verifiable source for Rule 3 only (e.g. 'Source: SEBI 2024' or 'Source: IIM-A Study 2023'). ONLY add if Rule 3 contains a real verifiable statistic. If not verifiable, return empty string.",
  "comment_question": "A SPECIFIC question about this reel's exact content — NOT generic. Example for a 3-rules reel: 'Rule 1, 2, ya 3 — kaunsa tumne abhi tak miss kiya? Sach bolo neeche' or for a mindset reel: 'Poor mindset ya Rich mindset — aap kis side ho? Type P ya R neeche 👇'. MAX 12 words. Must be answerable in 1-3 words so viewers actually comment.",
  "save_cta": "{cta}",
  "caption": "2 sentences total. Sentence 1 (THE STOP-SCROLL BOMB): A controversial, provocative, or deeply uncomfortable truth about money in India. Sentence 2 (THE COMMENT MAGNET): A direct, personal question the viewer MUST answer right now. End with EXACTLY these hashtags on a new line: {hashtags}"
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
          "split_screen": {
              "left": "Poor Mindset - Saves money",
              "right": "Rich Mindset - Invests money"
          },
          "authority_claim": "Tumhe lagta hai luck hai. Yeh ek pattern hai.",
          "numbered_list": [
              "Loss se zyada dar nahi lagta",
              "Decisions data se, emotion se nahi",
              "99% log EMI trap mein har saal 5 lakh khote hain"
          ],
          "proof_demo": "Proof: Mutual funds mein ₹10k/mo se tum 15 saal mein crorepati ho.",
          "save_cta": "Save and Share with someone who needs to wake up 🚀 Tum kaunsa karte ho — 1, 2, ya 3? Comment karo 👇",
          "caption": "आज ही शुरुआत करें। #WealthMindset #PsychologyFacts #HindiMotivation #SuccessRules"
        },
        {
          "hook": "Why you are secretly sabotaging your own success...",
          "split_screen": {
              "left": "Poor Mindset - Blames others",
              "right": "Rich Mindset - Takes responsibility"
          },
          "authority_claim": "Success koi accident nahi, ek formula hai.",
          "numbered_list": [
              "Stop waiting for the perfect time",
              "Focus on skills, not salary",
              "Average insaan scroll karta hai, top 1% create karta hai"
          ],
          "proof_demo": "Fact: Content creators make 5x more than average 9-to-5 workers in India.",
          "save_cta": "Save this rule before you forget! 📌 Tum kaunsa karte ho — 1, 2, ya 3? Comment karo 👇",
          "caption": "सच्चाई कड़वी है। #WealthMindset #PsychologyFacts #HindiMotivation #SuccessRules"
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
    TRUE 8D SPATIAL ROTATING AUDIO — sounds like the music moves around your head.
    Technique: HRTF-inspired stereo panning + binaural beat + room reverb simulation.

    The audio physically rotates in a circle around the listener:
      Left  = cos(rotation_angle) * signal   [0..1 oscillating]
      Right = sin(rotation_angle) * signal   [0..1 oscillating]
    Rotation speed slowly varies (0.08–0.25 Hz) for organic 8D feel.
    432 Hz left carrier + 436 Hz right carrier = 4 Hz THETA binaural beat.
    Room reverb: 3-tap delay (15ms / 28ms / 45ms) for spatial depth.
    Sub-bass 60 Hz pulse adds physical vibration feel.
    """
    sample_rate = 44100
    n_samples   = int(sample_rate * duration)

    # Reverb delay taps (samples)
    taps    = [int(0.015 * sample_rate),
               int(0.028 * sample_rate),
               int(0.045 * sample_rate)]
    tap_vol = [0.35, 0.22, 0.12]
    max_tap = max(taps)
    delay_buf = [0.0] * (max_tap + 1)
    buf_idx   = 0

    try:
        with wave.open(filename, 'w') as f:
            f.setnchannels(2)
            f.setsampwidth(2)
            f.setframerate(sample_rate)

            angle = 0.0  # running rotation angle (radians)

            for i in range(n_samples):
                t = float(i) / sample_rate

                # ── Envelope: 2s fade-in, 3s fade-out, slight mid-breath ──
                fade_in  = min(1.0, t / 2.0)
                fade_out = min(1.0, (duration - t) / 3.0)
                breath   = 0.88 + 0.12 * math.sin(2 * math.pi * 0.07 * t)  # ultra-slow
                env      = fade_in * fade_out * breath

                # ── 8D rotation speed (slowly varies 0.08–0.25 Hz) ──
                rot_speed = 0.16 + 0.09 * math.sin(2 * math.pi * 0.04 * t)
                angle    += (2 * math.pi * rot_speed) / sample_rate

                pan_l = 0.15 + 0.85 * ((1 + math.cos(angle)) / 2)
                pan_r = 0.15 + 0.85 * ((1 + math.sin(angle)) / 2)

                dist_mod = 0.75 + 0.25 * math.sin(2 * math.pi * 0.11 * t)

                # ── SIGMA TRAP BEAT GENERATOR ──
                import random as _rand
                bpm = 105.0
                beat_len = 60.0 / bpm
                bar_t = t % (beat_len * 4)

                # 1. 808 Sub Kick (Beats 1 & 3)
                is_kick = (bar_t < beat_len) or (bar_t >= beat_len * 2 and bar_t < beat_len * 2.5)
                kick = 0.0
                if is_kick:
                    k_phase = bar_t if bar_t < beat_len else (bar_t - beat_len * 2)
                    kick_freq = 120.0 * math.exp(-25.0 * k_phase) + 40.0
                    kick_env = math.exp(-5.0 * k_phase)
                    kick = math.sin(2 * math.pi * kick_freq * k_phase) * kick_env * 0.8

                # 2. Trap Hi-Hat (Every 1/4 beat, faster bursts)
                hh_phase = t % (beat_len / 4.0)
                hh_env = math.exp(-40.0 * hh_phase)
                hihat = ((i % 17) / 17.0 - 0.5) * hh_env * 0.3 # Pseudo-noise

                # 3. Dark Phonk Drone (A1 + Harmonics)
                drone_freq = 55.0
                drone = math.sin(2 * math.pi * drone_freq * t)
                drone += 0.5 * math.sin(2 * math.pi * drone_freq * 2.01 * t)
                drone += 0.25 * math.sin(2 * math.pi * drone_freq * 3.0 * t)
                drone *= 0.15 * (0.8 + 0.2 * math.sin(2 * math.pi * 0.5 * t)) # Wobble

                # Mix: Kick is centered (mono), Hihat/Drone are 8D panned
                sig_l = kick + (hihat + drone) * pan_l
                sig_r = kick + (hihat + drone) * pan_r

                # ── Room reverb (3 taps) ──
                reverb_l = 0.0
                reverb_r = 0.0
                for tap_i, tap_samp in enumerate(taps):
                    idx_past = (buf_idx - tap_samp) % (max_tap + 1)
                    reverb_l += tap_vol[tap_i] * delay_buf[idx_past]
                    reverb_r += tap_vol[tap_i] * delay_buf[idx_past]

                wet_l = sig_l * 0.7 + reverb_l * 0.3
                wet_r = sig_r * 0.7 + reverb_r * 0.3

                # Store in delay buffer (mono mix)
                delay_buf[buf_idx] = (sig_l + sig_r) * 0.5
                buf_idx = (buf_idx + 1) % (max_tap + 1)

                # ── Final mix with distance attenuation ──
                vol = 0.35 # Slightly louder for the beat
                left_val  = int(vol * dist_mod * env * wet_l * 32767)
                right_val = int(vol * dist_mod * env * wet_r * 32767)
                left_val  = max(-32767, min(32767, left_val))
                right_val = max(-32767, min(32767, right_val))
                f.writeframes(struct.pack('<hh', left_val, right_val))

        logger.info(f"✅ True 8D spatial audio generated: {filename}")
    except Exception as e:
        logger.error(f"Failed to create 8D audio {filename}: {e}")

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

def generate_audio(text, voice_id, output_path):
    """Generate TTS audio using edge-tts."""
    cmd = [sys.executable, "-m", "edge_tts", "--text", text, "--voice", voice_id, "--rate", "+10%", "--write-media", output_path]
    subprocess.run(cmd, check=True)

def get_audio_duration(file_path):
    """Get duration of an MP3 file in seconds."""
    try:
        audio = MP3(file_path)
        return audio.info.length
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
                            subprocess.run([
                                "ffmpeg", "-y", "-i", raw_out,
                                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                                       "unsharp=3:3:0.5:3:3:0.0,eq=contrast=1.05:saturation=1.2",
                                "-c:v", "libx264", "-preset", "superfast", "-tune", "fastdecode",
                                "-crf", "17", "-g", "1", "-keyint_min", "1", "-an", final_out
                            ], check=True, timeout=180, capture_output=True)
                            os.remove(raw_out)
                            logger.info(f"✅ [{name}] Direct fallback ready!")
                            downloaded = True
                            break
                except Exception as ce:
                    logger.warning(f"⚠️ Direct URL failed: {ce}")
                    continue

        if not downloaded:
            logger.error(f"❌ [{name}] All sources failed — creating solid-color placeholder")
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi",
                "-i", f"color=c=0x1a1a2e:s=1080x1920:d=15",
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28", final_out
            ], check=False, capture_output=True)

    logger.info("✅ All 4 HD Backgrounds Ready (Pexels/Pixabay/Mixkit Engine)!")



def build_v32_payload():
    logger.info("⚡ INITIATING V32 ULTIMATE AESTHETIC ENGINE ⚡")

    
    script_data = generate_dynamic_script()
    if not script_data:
        logger.error("❌ V32 FAILED - Gemini could not generate script. Aborting run.")
        logger.error("Failed to generate dynamic script. Aborting.")
        sys.exit(1)
        
    logger.info(f"✅ Generated Niche: {script_data.get('micro_niche')}")
    logger.info(f"✅ Generated Caption: {script_data.get('caption')}")

    
    # Extract phases safely from new Storyboard JSON format
    try:
        phase_1 = script_data.get("hook", "Rich vs Poor Mindset")
        
        split_screen_data = script_data.get("split_screen", {})
        if not isinstance(split_screen_data, dict):
            split_screen_data = {}
            
        split_left = split_screen_data.get("left", "Poor Mindset")
        split_right = split_screen_data.get("right", "Rich Mindset")
        phase_2 = f"{split_left}. {split_right}."
        phase_3 = script_data.get("authority_claim", "Most people never learn this.")
        
        nl = script_data.get("numbered_list", [])
        if not isinstance(nl, list):
            nl = []
            
        phase_l1 = nl[0] if len(nl) > 0 else "Rule 1: Always learn."
        phase_l2 = nl[1] if len(nl) > 1 else "Rule 2: Invest early."
        phase_l3 = nl[2] if len(nl) > 2 else "Rule 3: Stay consistent."
        
        phase_proof = script_data.get("proof_demo", "Proof: 99% fail without action.")
        phase_cta = script_data.get("save_cta", "Save this video now.")
        
        phases = [phase_1, phase_2, phase_3, phase_l1, phase_l2, phase_l3, phase_proof, phase_cta]
    except Exception as e:
        logger.error(f"Script JSON parsing failed: {e}. Aborting.")
        sys.exit(1)
    
    # Randomly pick voice pair
    base_voice = random.choice(VOICES)
    alternate_voice = VOICES[1] if base_voice == VOICES[0] else VOICES[0]
    
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
        voice_to_use = alternate_voice if i == 2 else base_voice
        generate_audio(phase_text, voice_to_use, audio_path)
        
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
        current_time += duration + 0.1
    
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

    cmd = [
        "npx", "remotion", "render",
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

    # ── GENERATE COVER FRAME ──
    cover_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cover.jpg"))
    logger.info("📸 Exporting unique cover frame (Frame 15)...")
    subprocess.run([
        "npx", "remotion", "still",
        "src/index.ts", "MainVideo", cover_file,
        "--props", json_path,
        "--frame=15"
    ], cwd=studio_dir, check=True)

    # ── PROFESSIONAL AUDIO MIX (BGM DUCKING & VO COMPRESSION) ──
    logger.info("🎛️ Starting Professional Audio Mix...")
    bgm_path = os.path.join(public_dir, "bgm.mp3")
    if not os.path.exists(bgm_path):
        logger.info("🎵 Downloading ambient BGM...")
        subprocess.run([
            "yt-dlp", "ytsearch1:ambient cinematic drone background music royalty free",
            "-x", "--audio-format", "mp3", "-o", bgm_path
        ], check=True)
    
    mixed_file = out_file.replace(".mp4", "_mixed.mp4")
    
    # Extract raw VO from remotion output
    subprocess.run(["ffmpeg", "-y", "-i", out_file, "-q:a", "0", "-map", "a", "temp_vo.wav"], check=True)
    
    # FFmpeg Magic:
    # 1. Denoiser and compressor on VO
    # 2. BGM set to extremely low volume (0.06 baseline)
    # 3. Sidechain ducking BGM by another 6-8dB when VO is active
    # 4. Mix them and mux with original video
    mix_cmd = [
        "ffmpeg", "-y",
        "-i", out_file,
        "-i", "temp_vo.wav",
        "-i", bgm_path,
        "-filter_complex",
        "[1:a]afftdn,acompressor=threshold=-15dB:ratio=4:attack=5:release=50:makeup=2dB[vo_polished];"
        "[2:a]volume=0.06[bgm_vol];"
        "[bgm_vol][vo_polished]sidechaincompress=threshold=0.06:ratio=4:attack=50:release=1000[bgm_ducked];"
        "[vo_polished][bgm_ducked]amix=inputs=2:duration=first:dropout_transition=2[a_out]",
        "-map", "0:v",
        "-map", "[a_out]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        mixed_file
    ]
    subprocess.run(mix_cmd, check=True)
    
    os.replace(mixed_file, out_file)
    try:
        os.remove("temp_vo.wav")
    except:
        pass

    logger.info("Video rendering complete. Script execution finished.")

    return out_file

if __name__ == "__main__":
    build_v32_payload()
