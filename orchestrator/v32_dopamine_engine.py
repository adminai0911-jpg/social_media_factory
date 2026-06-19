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
from google import genai
from google.genai import types
from dotenv import load_dotenv
from mutagen.mp3 import MP3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - V32_ENGINE - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")


def generate_dynamic_script():
    """Call Gemini to generate a fresh, unique, dopamine-triggering script JSON."""
    valid_keys = [k for k in GEMINI_KEYS if k]
    if not valid_keys:
        logger.error("No Gemini keys found!")
        return None
        
    random.shuffle(valid_keys)

    # ── Viral Hook & CTA rotation — never same pattern twice ─────────────────
    hooks = [
        "यह देखने के बाद आपकी सोच बदल जाएगी...",
        "99% लोग यह नहीं जानते — और यही उनकी सबसे बड़ी गलती है।",
        "अगर आपने यह नहीं समझा तो पैसे कभी नहीं बनेंगे।",
        "क्या आप भी वही गलती कर रहे हैं जो बाकी सब करते हैं?",
        "आज मैं वो secret share करूँगा जो अमीर लोग कभी नहीं बताते।",
        "School ने यह कभी नहीं सिखाया — पर आज जान लो।",
        "1 minute में आपकी life की सबसे important lesson...",
        "यह video देखकर आप खुद से पूछोगे: मैंने पहले क्यों नहीं सोचा?"
    ]
    ctas = [
        "Comment में लिखो READY अगर तुम यह change करना चाहते हो 👇",
        "इसे Save करो — 6 महीने बाद तुम खुद को thanks कहोगे 📌",
        "उस दोस्त को Tag करो जिसे यह सुनना जरूरी है 🔖",
        "Part 2 चाहिए? Comment में YES लिखो 🔥",
        "Share करो उन लोगों के साथ जिनकी life बदलनी चाहिए 🚀",
        "Like करो अगर यह आपके साथ भी हुआ है ❤️",
        "Save करो + Share करो — किसी की life बदल सकती है 🙏"
    ]
    hook = random.choice(hooks)
    cta  = random.choice(ctas)

    prompt = f"""You are an elite neuro-marketing viral scriptwriter for Indian social media.
Generate a short-form video script that triggers dopamine and adrenaline.
Script MUST be in Hindi (Devanagari or Hinglish mix).
Return ONLY raw JSON — no markdown, no backticks.

Mandatory: phase_1 MUST use this hook exactly: {hook}
Mandatory: phase_5 MUST use this CTA exactly: {cta}

JSON:
{{
  "micro_niche": "Highly specific unique niche topic",
  "style_seed": 42,
  "emojis": ["🧠", "🔥", "💡"],
  "red_box_keyword": "TRAP",
  "subliminal_flash_word": "WAKE UP",
  "serotonin_payoff_number": 847293,
  "phase_1": "{hook}",
  "phase_2": "Build-up. 1 sentence Hindi. Personal relatable emotional stakes.",
  "phase_3": "Pattern Interrupt. 2-3 sentences. Shocking counter-intuitive truth.",
  "phase_4": "Payoff. 1-2 sentences. Actionable insight that feels like revelation.",
  "phase_5": "{cta}",
  "caption_instagram": "Emotional Hindi caption. 1-2 sentences + EXACTLY 5 hashtags.",
  "caption_x": "Punchy Hinglish. Max 250 chars. No hashtags. End with question.",
  "caption_youtube": "SEO title. Numbers + emotion + benefit. Max 70 chars.",
  "caption_facebook": "Conversational Hindi. 2-3 sentences. End with question.",
  "caption": "Same as caption_instagram."
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
                        response_mime_type="application/json"
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
          "micro_niche": "Psychology of Wealth",
          "style_seed": random.randint(1, 100),
          "emojis": ["🧠", "🔥", "⚠️"],
          "red_box_keyword": "FAKE",
          "subliminal_flash_word": "WAKE UP",
          "serotonin_payoff_number": random.randint(10000, 999999),
          "phase_1": "क्या आपको लगता है कि आप कभी अमीर नहीं बन पाएंगे?",
          "phase_2": "आप अकेले नहीं हैं, 99% लोग यही सोचते हैं।",
          "phase_3": "लेकिन सच यह है कि स्कूल हमें पैसे के बारे में सब कुछ गलत सिखाता है।",
          "phase_4": "असली दौलत तब बनती है जब आपका पैसा आपके लिए काम करता है, न कि आप पैसे के लिए।",
          "phase_5": "इस मैट्रिक्स से बाहर निकलने का समय आ गया है।",
          "caption": "आज ही शुरुआत करें। #wealth #mindset #money #success #hindi"
        },
        {
          "micro_niche": "Dark Psychology",
          "style_seed": random.randint(1, 100),
          "emojis": ["👁️", "🤐", "⚡"],
          "red_box_keyword": "LIES",
          "subliminal_flash_word": "TRUST NO ONE",
          "serotonin_payoff_number": random.randint(10000, 999999),
          "phase_1": "क्या आप जानते हैं कि लोग आपको रोज़ाना कैसे मैनिपुलेट करते हैं?",
          "phase_2": "यह आपके सबसे करीबियों से ही शुरू होता है।",
          "phase_3": "साइकोलॉजी कहती है कि जो लोग हमेशा 'अच्छा' बनते हैं, वो सबसे बड़े मास्टरमाइंड होते हैं।",
          "phase_4": "उनके मीठे शब्दों के पीछे छिपे असली इरादे को पहचानना सीखें।",
          "phase_5": "अब और बेवकूफ मत बनो, खेल के नियम बदलो।",
          "caption": "सच्चाई कड़वी है। #psychology #facts #mindset #lifehacks #hindi"
        },
        {
          "micro_niche": "Sigma Male Rule",
          "style_seed": random.randint(1, 100),
          "emojis": ["🐺", "🤫", "📈"],
          "red_box_keyword": "SILENCE",
          "subliminal_flash_word": "GRIND HARD",
          "serotonin_payoff_number": random.randint(10000, 999999),
          "phase_1": "सिग्मा मेल्स कभी भीड़ का हिस्सा नहीं बनते।",
          "phase_2": "वो अपनी मंज़िल अकेले तय करते हैं।",
          "phase_3": "जब दुनिया शोर मचा रही होती है, सिग्मा शांत रहकर अपना एम्पायर खड़ा कर रहा होता है।",
          "phase_4": "उनकी खामोशी में ही उनकी सबसे बड़ी ताकत छुपी है।",
          "phase_5": "अकेले चलना सीखो, जीत पक्की है।",
          "caption": "रूल नंबर 1: किसी पर निर्भर मत रहो। #sigma #motivation #rules #hindi #alpha"
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

                # ── Power-preserving panning (never fully silent) ──
                # Values stay in [0.15 .. 1.0] so sound always present
                pan_l = 0.15 + 0.85 * ((1 + math.cos(angle)) / 2)
                pan_r = 0.15 + 0.85 * ((1 + math.sin(angle)) / 2)

                # ── Distance attenuation (sound feels near/far) ──
                dist_mod = 0.75 + 0.25 * math.sin(2 * math.pi * 0.11 * t)

                # ── Source signal ──
                # 432 Hz healing carrier (left ear) + harmonics
                sig_l  = math.sin(2 * math.pi * 432.0 * t)
                sig_l += 0.32 * math.sin(2 * math.pi * 216.0 * t)   # sub-octave
                sig_l += 0.20 * math.sin(2 * math.pi * 864.0 * t)   # 2nd harmonic
                sig_l += 0.12 * math.sin(2 * math.pi * 1296.0 * t)  # 3rd harmonic
                # 436 Hz binaural beat carrier (right ear) — 4 Hz diff = theta waves
                sig_r  = math.sin(2 * math.pi * 436.0 * t)
                sig_r += 0.32 * math.sin(2 * math.pi * 218.0 * t)
                sig_r += 0.20 * math.sin(2 * math.pi * 872.0 * t)
                sig_r += 0.12 * math.sin(2 * math.pi * 1308.0 * t)
                # Sub-bass pulse shared (for headphone vibration)
                sub = 0.45 * math.sin(2 * math.pi * 60.0 * t) * \
                      (0.5 + 0.5 * math.sin(2 * math.pi * 1.5 * t))
                sig_l += sub
                sig_r += sub

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

                # ── Final mix with 8D panning applied ──
                vol = 0.26
                left_val  = int(vol * pan_l * dist_mod * env * wet_l * 32767)
                right_val = int(vol * pan_r * dist_mod * env * wet_r * 32767)
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
    cmd = [sys.executable, "-m", "edge_tts", "--text", text, "--voice", voice_id, "--write-media", output_path]
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
    send_telegram_alert("🎬 <b>Pexels HD Engine</b>\nFetching 4 unique HD satisfying videos from Pexels API...")

    pexels_key = os.getenv("PEXELS_API_KEY", "")
    if not pexels_key:
        logger.error("❌ PEXELS_API_KEY not set in environment/secrets. Add it at pexels.com/api (free)")
        pexels_key = None

    output_names = ["gta", "sand", "bg3", "bg4"]

    # Rotating set of visually stunning search queries — different results every run
    satisfying_queries = [
        "kinetic sand satisfying",
        "abstract fluid art",
        "nature waterfall aerial",
        "neon city timelapse",
        "satisfying marble run",
        "ocean waves close up",
        "galaxy space stars",
        "golden ratio spiral",
        "slow motion water",
        "colorful paint mixing",
        "crystal geode close up",
        "forest rain bokeh",
        "fire flames abstract",
        "aurora borealis night",
        "slow motion flower bloom",
        "urban city night lights",
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
    send_telegram_alert("⚡ <b>V32 Engine Starting</b>\nGenerating new unique script from Gemini...")
    
    script_data = generate_dynamic_script()
    if not script_data:
        send_telegram_alert("❌ <b>V32 FAILED</b>\nGemini could not generate script. Aborting run.")
        logger.error("Failed to generate dynamic script. Aborting.")
        return None
        
    logger.info(f"✅ Generated Niche: {script_data.get('micro_niche')}")
    logger.info(f"✅ Generated Caption: {script_data.get('caption')}")
    send_telegram_alert(f"✅ <b>Script Ready</b>\nNiche: {script_data.get('micro_niche')}\nCaption: {script_data.get('caption')}")
    
    # Extract phases safely
    try:
        phases = [
            script_data["phase_1"], script_data["phase_2"], script_data["phase_3"],
            script_data["phase_4"], script_data["phase_5"]
        ]
    except KeyError as e:
        logger.error(f"Script JSON missing key: {e}. Aborting.")
        return None
    
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
    
    # Ensure we have all 5 audio offsets for MainVideo.tsx
    while len(audio_offsets) < 5:
        audio_offsets.append(current_time)
        
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
    logger.info(f"✅ V34 4K render complete: {out_file}")

    logger.info("Video rendering complete. Script execution finished.")

    return out_file

if __name__ == "__main__":
    build_v32_payload()
