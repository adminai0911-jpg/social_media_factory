import os
import json
import random
import requests
import subprocess
import sys
import logging
import time
import google.generativeai as genai
from dotenv import load_dotenv
from mutagen.mp3 import MP3

logging.basicConfig(level=logging.INFO, format='%(asctime)s - V32_ENGINE - %(levelname)s - %(message)s')
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

def get_gemini_client():
    valid_keys = [k for k in GEMINI_KEYS if k]
    if not valid_keys:
        logger.error("No Gemini keys found in .env or environment!")
        return None
    key = random.choice(valid_keys)
    genai.configure(api_key=key)
    return genai.GenerativeModel('gemini-2.5-flash')

def generate_dynamic_script():
    model = get_gemini_client()
    if not model:
        return None

    prompt = """
    You are an elite, neuro-marketing viral scriptwriter.
    Generate a highly engaging short-form video script specifically designed to trigger dopamine and adrenaline.
    You must return ONLY a raw JSON object (no markdown, no backticks).
    
    Structure:
    {
      "micro_niche": "A highly specific, unique niche (e.g., Quantum Gardening, Biohacking Sleep, Psychology of Colors)",
      "style_seed": <integer 1-100>,
      "emojis": ["<emoji1>", "<emoji2>", "<emoji3>"],
      "red_box_keyword": "A single intense 5-8 letter word (e.g., FAKE, LIES, TRAP)",
      "subliminal_flash_word": "A short phrase (e.g., WAKE UP, LOOK CLOSER)",
      "serotonin_payoff_number": <random large integer>,
      "phase_1": "The Hook. 1 sentence. Curiosity gap.",
      "phase_2": "The Build-up. 1 sentence. Personal/relatable stakes.",
      "phase_3": "The Pattern Interrupt. 2-3 sentences. A shocking realization or weird fact.",
      "phase_4": "The Payoff. 1-2 sentences. The resolution to the hook.",
      "phase_5": "The Loop/CTA. 1 sentence. A valuable takeaway that loops back visually.",
      "caption": "A highly engaging 1-2 sentence caption. IT MUST CONTAIN EXACTLY 5 HASHTAGS AT THE END. NO MORE, NO LESS."
    }
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        
        return json.loads(text.strip())
    except Exception as e:
        logger.error(f"Gemini generation failed: {e}")
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

def build_v32_payload():
    logger.info("⚡ INITIATING V32 ULTIMATE AESTHETIC ENGINE ⚡")
    
    script_data = generate_dynamic_script()
    if not script_data:
        logger.error("Failed to generate dynamic script. Aborting.")
        return
        
    logger.info(f"✅ Generated Niche: {script_data.get('micro_niche')}")
    logger.info(f"✅ Generated Caption: {script_data.get('caption')}")
    
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
        
    payload = {
        "script": script_data,
        "timings": timings,
        "audio_offsets": audio_offsets,
        "total_duration": current_time
    }
    
    json_path = os.path.join(public_dir, "v32_script.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        
    logger.info("Triggering Remotion Render (V32 - Ultimate Aesthetic)...")
    studio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio"))
    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "FINAL_V32_ULTIMATE_AESTHETIC.mp4"))
    
    cmd = ["npx", "remotion", "render", "src/index.ts", "MainVideo", out_file, "--props", json_path]
    subprocess.run(cmd, cwd=studio_dir, check=True, shell=True)
    logger.info(f"✅ SUCCESSFULLY RENDERED V32 REEL: {out_file}")
    
    # Trigger uploader
    logger.info("Triggering the 4-Platform Uploader...")
    caption = script_data.get('caption', "This will blow your mind 🤯 #viral #trending #fyp #mindset #growth")
    
    try:
        import uploader
        uploader.distribute_to_all_platforms(out_file, caption)
    except Exception as e:
        logger.error(f"Uploader failed: {e}")

if __name__ == "__main__":
    build_v32_payload()
