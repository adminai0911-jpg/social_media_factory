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
import google.generativeai as genai
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

    prompt = """
    You are an elite, neuro-marketing viral scriptwriter.
    Generate a highly engaging short-form video script specifically designed to trigger dopamine and adrenaline in the viewer.
    The script MUST be in Hindi (Devanagari or Roman Hindi).
    You must return ONLY a raw JSON object (no markdown, no backticks, no explanation).
    
    Structure:
    {
      "micro_niche": "A highly specific, unique niche (e.g., 'Quantum Gardening for City Dwellers', 'Psychology of Getting Rich')",
      "style_seed": <integer 1-100>,
      "emojis": ["<emoji1>", "<emoji2>", "<emoji3>"],
      "red_box_keyword": "A single intense 4-6 letter English word (e.g., FAKE, LIES, TRAP, SCAM)",
      "subliminal_flash_word": "A short English phrase (e.g., WAKE UP, LOOK CLOSER)",
      "serotonin_payoff_number": <random large integer between 10000 and 999999>,
      "phase_1": "The Hook. 1 sentence in Hindi. Create a curiosity gap.",
      "phase_2": "The Build-up. 1 sentence in Hindi. Personal/relatable stakes.",
      "phase_3": "The Pattern Interrupt. 2-3 sentences in Hindi. A shocking realization or weird fact.",
      "phase_4": "The Payoff. 1-2 sentences in Hindi. The resolution to the hook.",
      "phase_5": "The Loop/CTA. 1 sentence in Hindi. A valuable takeaway that mirrors the opening.",
      "caption": "A single engaging Hindi caption sentence followed by EXACTLY 5 English hashtags (NO MORE, NO LESS)."
    }
    """
    
    for key in valid_keys:
        logger.info(f"Trying Gemini API key starting with: {key[:8]}...")
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        for attempt in range(2):  # Retry up to 2 times per key
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json"
                    )
                )
                
                if not response.candidates or not response.text:
                    logger.error(f"Gemini response blocked or empty. Candidates: {response.candidates}")
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
        
    logger.info("🎬 Triggering V34 4K Premium Remotion Render (CRF=12, Scale=2, Concurrency=2)...")
    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "FINAL_V34_ULTRA_4K.mp4"))

    # ── V34 Render Flags — Max Quality + Optimized Speed ─────────────────────
    # --scale=2         → Double resolution (1080x1920 to 2160x3840 = True 4K!)
    # --crf=12          → Near-lossless visual quality (ultra-glossy, crisp text)
    # --video-bitrate=8000k → High bitrate for pristine 4K playback
    # --concurrency=2   → Parallel rendering on both runner CPU cores
    # --timeout=1200    → Kill after 20 minutes to save Actions minutes if hung
    # --gl=swangle      → Software WebGL rendering on headless Linux
    # ─────────────────────────────────────────────────────────────────────────

    # Read REMOTION_CONCURRENCY from env (set to 2 in workflow for 2-core runners)
    concurrency = os.environ.get("REMOTION_CONCURRENCY", "2")

    cmd = [
        "npx", "remotion", "render",
        "src/index.ts", "MainVideo", out_file,
        "--props", json_path,
        "--scale=2",
        "--crf=12",
        "--video-bitrate=8000k",
        f"--concurrency={concurrency}",
        "--timeout=1200",
        "--gl=swangle",
    ]
    subprocess.run(cmd, cwd=studio_dir, check=True)
    logger.info(f"✅ V34 4K render complete: {out_file}")

    logger.info("Video rendering complete. Script execution finished.")

    return out_file

if __name__ == "__main__":
    build_v32_payload()
