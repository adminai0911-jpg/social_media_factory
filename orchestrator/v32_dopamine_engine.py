import os
import json
import random
import requests
import subprocess
import sys
import logging
import time
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
        client = genai.Client(api_key=key)
        
        for attempt in range(2):  # Retry up to 2 times per key
            try:
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        safety_settings=[
                            types.SafetySetting(
                                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                                threshold=types.HarmBlockThreshold.BLOCK_NONE,
                            ),
                            types.SafetySetting(
                                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                                threshold=types.HarmBlockThreshold.BLOCK_NONE,
                            ),
                            types.SafetySetting(
                                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                                threshold=types.HarmBlockThreshold.BLOCK_NONE,
                            ),
                            types.SafetySetting(
                                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                                threshold=types.HarmBlockThreshold.BLOCK_NONE,
                            ),
                        ]
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
    
    logger.error("All Gemini keys and attempts failed.")
    return None

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
        
    logger.info("Triggering Remotion Render (V32 - Ultimate Aesthetic)...")
    studio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio"))
    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "FINAL_V32_ULTIMATE_AESTHETIC.mp4"))
    
    # BUG FIX: Removed shell=True on Linux; pass command as list for cross-platform safety
    cmd = ["npx", "remotion", "render", "src/index.ts", "MainVideo", out_file, "--props", json_path]
    subprocess.run(cmd, cwd=studio_dir, check=True)
    logger.info(f"✅ SUCCESSFULLY RENDERED V32 REEL: {out_file}")
    
    # Trigger uploader with the generated caption
    caption = script_data.get('caption', "Yeh sach aapko haila kar dega! 🤯 #viral #trending #fyp #mindset #growth")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        import uploader
        uploader.distribute_to_all_platforms(out_file, caption)
    except Exception as e:
        logger.error(f"Uploader failed: {e}")
        send_telegram_alert(f"❌ <b>Uploader Failed</b>\n{str(e)}")

    return out_file

if __name__ == "__main__":
    build_v32_payload()
