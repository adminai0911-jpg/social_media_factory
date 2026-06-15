import os
import sys
import json
import asyncio
import subprocess
import logging
import requests
import random
import requests
import random
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s - V24_ENGINE - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

GEMINI_KEYS = [
    os.environ.get("GEMINI_API_KEY_1"),
    os.environ.get("GEMINI_API_KEY_2"),
    os.environ.get("GEMINI_API_KEY_3"),
    os.environ.get("GEMINI_API_KEY_4"),
    os.environ.get("GEMINI_API_KEY_5")
]
if not any(GEMINI_KEYS):
    logger.error("Missing API Keys in .env")
    sys.exit(1)

# Pick a random Gemini key from the 5 available
GEMINI_API_KEY = random.choice([k for k in GEMINI_KEYS if k])

# Raw REST API used instead

# Top 10 Best ElevenLabs Voices for Viral Hooks
ELEVEN_VOICES = [
    {"name": "Adam", "id": "pNInz6obpgDQGcFmaJgB"},
    {"name": "Rachel", "id": "21m00Tcm4TlvDq8ikWAM"},
    {"name": "Antoni", "id": "ErXwobaYiN019PkySvjV"},
    {"name": "Josh", "id": "tx3xgqwjuETCu1CGvnA6"},
    {"name": "Bella", "id": "EXAVITQu4vr4xnSDxMaL"},
    {"name": "Arnold", "id": "VR6AewLTigWG4xSOukaG"},
    {"name": "Callum", "id": "N2lVS1w4EtoT3dr4eOWO"},
    {"name": "Charlie", "id": "IKne3meq5aSn9XLyUdCD"},
    {"name": "Clyde", "id": "2EiwWnXFnvU5JabPnv8n"},
    {"name": "Dave", "id": "CYw3kZ02Hs0563khs1Fj"}
]

def generate_infinite_script():
    logger.info("🧠 Brain spinning up Infinite Chaos Sequence...")
    
    system_prompt = """
    You are an underground, psychological AI designed to generate viral, dark-truth content.
    Your goal is to maximize human dopamine and retention loops using 4 hormones:
    Adrenaline (0-2s), Dopamine (2-5s), Oxytocin (5-20s), Serotonin (20-25s), and the Loop (25-30s).
    
    You must output a highly engaging script in HINDI (written in english/roman script for text-to-speech).
    It MUST be exactly 5 phases, totaling about 30 seconds spoken.
    
    Phase 1: Adrenaline Hook (Shocking statement or pattern interrupt). (0-10s)
    Phase 2: Dopamine Gap (The curiosity builder). (0-10s)
    Phase 3: Oxytocin Build (Vulnerable, relatable middle. Conversational). (10-20s, this is where Split Screen happens)
    Phase 4: Serotonin Payoff (The big reveal. Use highly SPECIFIC odd numbers, e.g., 47,212). (20-30s)
    Phase 5: The Loop (The final sentence must grammatically connect perfectly back to the first sentence of Phase 1). (20-30s)
    
    Also hallucinate a random 'micro_niche' that has never existed before (e.g. 'Anxious College Dropouts doing Crypto').
    Also generate a 4D Style Seed (a number from 1 to 10 for the visual theme).
    Also pick 3 emojis perfectly suited to the niche.
    Pick ONE word from Phase 1 or 2 to be the 'red_box_keyword' (a word to highlight with a red box).
    Pick ONE word from Phase 4 or 5 to be the 'jackpot_keyword' (the climactic moment).
    
    Output strictly in JSON:
    {
      "micro_niche": "...",
      "style_seed": 7,
      "emojis": ["...", "...", "..."],
      "red_box_keyword": "...",
      "jackpot_keyword": "...",
      "phase_1": "...",
      "phase_2": "...",
      "phase_3": "...",
      "phase_4": "...",
      "phase_5": "..."
    }
    """
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": system_prompt}]}]
    }
    import time
    for attempt in range(5):
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            break
        logger.warning(f"Gemini API returned {response.status_code}. Retrying... ({attempt+1}/5)")
        time.sleep(2)
    
    try:
        raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        raw_json = raw_text.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_json)
        return data
    except Exception as e:
        logger.error(f"Failed to parse Gemini: {response.text}")
        sys.exit(1)

ELEVENLABS_KEYS = [
    os.environ.get("ELEVENLABS_API_KEY_1"),
    os.environ.get("ELEVENLABS_API_KEY_2")
]

def generate_audio(text, voice_id, output_path):
    # Fallback to edge_tts (Microsoft Neural) for infinite free scale in Hindi
    cmd = [
        sys.executable, "-m", "edge_tts",
        "--text", text,
        "--voice", "hi-IN-MadhurNeural", # Or hi-IN-SwaraNeural
        "--write-media", output_path
    ]
    subprocess.run(cmd, check=True)

from mutagen.mp3 import MP3
def get_audio_duration(file_path):
    try:
        audio = MP3(file_path)
        return audio.info.length
    except Exception as e:
        logger.error(f"Mutagen error: {e}")
        return 5.0 # fallback

async def main():
    logger.info("⚡ INITIATING V24 INFINITE DOPAMINE ENGINE ⚡")
    
    studio_public = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio", "public"))
    os.makedirs(studio_public, exist_ok=True)
    
    script_data = generate_infinite_script()
    logger.info(f"✅ Generated Niche: {script_data['micro_niche']}")
    
    voice = random.choice(ELEVEN_VOICES)
    logger.info(f"🎤 Selected Voice Actor: {voice['name']} ({voice['id']})")
    
    # We will generate 5 audio files for the 5 phases
    phases = [
        script_data["phase_1"],
        script_data["phase_2"],
        script_data["phase_3"],
        script_data["phase_4"],
        script_data["phase_5"]
    ]
    
    audio_offsets = []
    timings = []
    current_time = 0.0
    
    for i, phase_text in enumerate(phases):
        audio_path = os.path.join(studio_public, f"v24_audio_{i}.mp3")
        logger.info(f"Generating audio for Phase {i+1}...")
        generate_audio(phase_text, voice["id"], audio_path)
        
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
        
        current_time += duration + 0.1 # 100ms gap
        
    # Write V24 JSON for React
    v24_json_path = os.path.join(studio_public, "v24_script.json")
    with open(v24_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "script": script_data,
            "voice": voice["name"],
            "timings": timings,
            "audio_offsets": audio_offsets,
            "total_duration": current_time
        }, f, indent=2)
        
    logger.info("JSON Payload built. React Engine is ready.")
    
    logger.info("Triggering Remotion Render (V24 - Infinite Dopamine Engine)...")
    studio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio"))
    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "FINAL_V26_V23_STRICT_MERGE.mp4"))
    
    cmd = [
        "npx", "remotion", "render", "src/index.ts", "MainVideo", out_file,
        "--props=./public/v24_script.json",
        f"--totalDurationInSeconds={current_time}",
        "--videoBitrate=40M",
        "--codec=h264"
    ]
    
    try:
        subprocess.run(cmd, cwd=studio_dir, check=True, shell=True)
        logger.info(f"✅ SUCCESSFULLY RENDERED V24 REEL: {out_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Render failed: {e}")
    
if __name__ == "__main__":
    asyncio.run(main())
