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

logging.basicConfig(level=logging.INFO, format='%(asctime)s - V31_ENGINE - %(levelname)s - %(message)s')
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

# We use the exact same Quantum Gardening JSON to give the user a 1:1 comparison of the visual fixes
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

def generate_audio(text, voice_id, output_path):
    cmd = [sys.executable, "-m", "edge_tts", "--text", text, "--voice", voice_id, "--write-media", output_path]
    subprocess.run(cmd, check=True)

def get_audio_duration(file_path):
    try:
        audio = MP3(file_path)
        return audio.info.length
    except:
        return 2.0

def build_v31_payload():
    logger.info("⚡ INITIATING V31 BRIGHT POLISH ENGINE ⚡")
    
    script_json_str = FALLBACK_JSON
    script_data = json.loads(script_json_str)
    logger.info(f"✅ Generated Niche: {script_data.get('micro_niche')} (V31 Visual Polish)")
    
    phases = [script_data["phase_1"], script_data["phase_2"], script_data["phase_3"], script_data["phase_4"], script_data["phase_5"]]
    
    # Force Swara to be the main voice and Madhur to be the alternate just to keep it consistent with the previous run
    base_voice = "hi-IN-SwaraNeural"
    alternate_voice = "hi-IN-MadhurNeural"
    
    public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio", "public"))
    os.makedirs(public_dir, exist_ok=True)
    
    timings = []
    audio_offsets = []
    current_time = 0.0
    
    for i, phase_text in enumerate(phases):
        logger.info(f"Generating audio for Phase {i+1}...")
        audio_path = os.path.join(public_dir, f"v31_audio_{i}.mp3")
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
    
    json_path = os.path.join(public_dir, "v31_script.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        
    logger.info("Triggering Remotion Render (V31 - Bright Polish)...")
    studio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio"))
    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "FINAL_V31_BRIGHT_POLISH.mp4"))
    
    cmd = ["npx", "remotion", "render", "src/index.ts", "MainVideo", out_file, "--props", json_path]
    subprocess.run(cmd, cwd=studio_dir, check=True, shell=True)
    logger.info(f"✅ SUCCESSFULLY RENDERED V31 REEL: {out_file}")

if __name__ == "__main__":
    build_v31_payload()
