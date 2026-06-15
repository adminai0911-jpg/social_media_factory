import os
import json
import random
import requests
import subprocess
import sys
import logging
import time
from dotenv import load_dotenv
from mutagen.mp3 import MP3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - V30_ENGINE - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

GEMINI_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4"),
    os.getenv("GEMINI_API_KEY_5")
]

VOICES = [
    "hi-IN-MadhurNeural", # Male
    "hi-IN-SwaraNeural",  # Female
]

FALLBACK_JSON = """
{
  "micro_niche": "Quantum Gardening for Urban Minimalists",
  "style_seed": 7,
  "emojis": ["🌱", "👁️", "⏳"],
  "red_box_keyword": "SIMULATION",
  "subliminal_flash_word": "WAKE UP",
  "serotonin_payoff_number": 88319,
  "phase_1": "kya aapko lagta hai ki aapke paudhe sach mein badh rahe hain ya yeh sirf ek simulation hai?",
  "phase_2": "maine apne living room mein ek experiment kiya, aur jo mujhe pata chala woh aapko dara dega.",
  "phase_3": "main bhi pehle sochta tha ki mitti aur paani hi sab kuch hai. lekin phir maine quantum light frequencies ko test kiya. jab main raat ko sota tha, tab wahan kuch aur hi chal raha tha. aapki aankhon ke peeche jo chhippa hai, woh sab badal dega.",
  "phase_4": "asal mein, aapke paudhe quantum tunneling ka istemaal karke energy absorb kar rahe hain. yeh hai sach.",
  "phase_5": "isliye agli baar jab aap unhe paani dein, toh yaad rakhein..."
}
"""

def generate_script_from_gemini():
    api_key = random.choice([k for k in GEMINI_KEYS if k])
    if not api_key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    prompt = """
    You are an evil, hyper-optimized AI designed to hijack the human brain's dopamine receptors using short-form video.
    You must output a highly engaging script in HINDI (written in english/roman script for text-to-speech).
    It MUST perfectly follow this 30-second timeline mapping based on the 5 psychological levers:
    Phase 1: Adrenaline Hook (0-2s): A shocking statement, mid-result open, or fast pattern interrupt. Very short.
    Phase 2: Dopamine Gap (2-5s): The curiosity gap. State an unresolved question or mystery.
    Phase 3: Oxytocin Build (5-20s): Vulnerable, relatable middle. Conversational, podcast style ("I used to think like you..."). Build the tension.
    Phase 4: Serotonin Payoff (20-25s): The big reveal. The tension resolves into a satisfying answer.
    Phase 5: The Loop (25-30s): The final sentence must grammatically connect perfectly back to the first sentence of Phase 1. Provide a real tip/value.
    
    Also hallucinate a random 'micro_niche' that has never existed before (e.g. '30-Day Money Challenge for Introverted Pet Owners').
    Also generate a 4D Style Seed (a number from 1 to 10 for the visual theme).
    Also pick 3 emojis perfectly suited to the niche.
    Pick ONE word from Phase 1 or 2 to be the 'red_box_keyword'.
    Pick ONE word from Phase 3 or 4 to be the 'subliminal_flash_word' (should be commanding like 'WAKE', 'LISTEN', 'LOOK').
    Pick a random, highly specific odd number (e.g. 47212) to be the 'serotonin_payoff_number'.
    
    Output strictly in JSON:
    {
      "micro_niche": "...",
      "style_seed": 7,
      "emojis": ["...", "...", "..."],
      "red_box_keyword": "...",
      "subliminal_flash_word": "...",
      "serotonin_payoff_number": 47212,
      "phase_1": "...",
      "phase_2": "...",
      "phase_3": "...",
      "phase_4": "...",
      "phase_5": "..."
    }
    """
    
    data = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 1.2, "response_mime_type": "application/json"}}
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            logger.error(f"Gemini API {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Gemini Error: {e}")
        return None

def generate_audio(text, voice_id, output_path):
    cmd = [sys.executable, "-m", "edge_tts", "--text", text, "--voice", voice_id, "--write-media", output_path]
    subprocess.run(cmd, check=True)

def get_audio_duration(file_path):
    try:
        audio = MP3(file_path)
        return audio.info.length
    except:
        return 2.0

def build_v30_payload():
    logger.info("⚡ INITIATING V30 ULTIMATE HORMONE BOOSTER ENGINE ⚡")
    
    script_json_str = None
    for attempt in range(3):
        script_json_str = generate_script_from_gemini()
        if script_json_str: break
        logger.warning(f"Retrying Gemini API... ({attempt+1}/3)")
        time.sleep(2)
        
    if not script_json_str:
        logger.error("API DOWN. USING HARDCODED V29 QUANTUM GARDENING FALLBACK.")
        script_json_str = FALLBACK_JSON
        
    script_data = json.loads(script_json_str)
    logger.info(f"✅ Generated Niche: {script_data.get('micro_niche')}")
    
    phases = [script_data["phase_1"], script_data["phase_2"], script_data["phase_3"], script_data["phase_4"], script_data["phase_5"]]
    
    base_voice = random.choice(VOICES)
    alternate_voice = VOICES[1] if base_voice == VOICES[0] else VOICES[0]
    
    public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio", "public"))
    os.makedirs(public_dir, exist_ok=True)
    
    timings = []
    audio_offsets = []
    current_time = 0.0
    
    for i, phase_text in enumerate(phases):
        logger.info(f"Generating audio for Phase {i+1}...")
        audio_path = os.path.join(public_dir, f"v30_audio_{i}.mp3")
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
        
    payload = {
        "script": script_data,
        "timings": timings,
        "audio_offsets": audio_offsets,
        "total_duration": current_time
    }
    
    json_path = os.path.join(public_dir, "v30_script.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        
    logger.info("Triggering Remotion Render (V30 - Ultimate Booster)...")
    studio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio"))
    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "FINAL_V30_ULTIMATE_BOOSTER.mp4"))
    
    cmd = ["npx", "remotion", "render", "src/index.ts", "MainVideo", out_file, "--props", json_path]
    subprocess.run(cmd, cwd=studio_dir, check=True, shell=True)
    logger.info(f"✅ SUCCESSFULLY RENDERED V30 REEL: {out_file}")

if __name__ == "__main__":
    build_v30_payload()
