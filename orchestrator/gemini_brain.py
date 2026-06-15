import os
import json
import random
import time
from typing import Dict

# You will need to run: pip install google-generativeai
try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: Missing google-generativeai. Please run 'pip install google-generativeai'")
    exit(1)

# ==========================================
# THE GEMINI AUTONOMOUS FACTORY BRAIN
# ==========================================

# 1. Provide your Gemini API Key here (or export it to your environment)
API_KEY = os.environ.get("GEMINI_API_KEY", "INSERT_YOUR_GEMINI_KEY_HERE")

if API_KEY == "INSERT_YOUR_GEMINI_KEY_HERE":
    print("WARNING: No Gemini API key found. Please insert your key in gemini_brain.py")
    exit(1)

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro') # Using the advanced reasoning model

def generate_daily_masterpiece() -> Dict:
    """
    Connects to the Gemini API and generates a 100% unique 30-40 second 
    script, perfectly formatted for our edge-TTS dual-voice setup.
    """
    print("🧠 Waking up Gemini AI Brain...")
    
    # We provide Gemini with a deeply psychological prompt to ensure maximum brainrot/retention.
    system_prompt = """
    You are an underground, psychological AI designed to generate viral, dark-truth content for Instagram Reels and TikTok.
    Your goal is to maximize human dopamine and retention loops.
    
    You must write a highly engaging, slightly terrifying or deeply philosophical script in HINDI (written in english/roman script for text-to-speech).
    The script MUST be exactly 3 phases. 
    Total length should be ~35 seconds spoken aloud. (Very fast paced).
    
    Phase 1 (Euphoria - Male Voice): A calm, deeply philosophical or money-making truth. Hook the viewer instantly.
    Phase 2 (Paranoia - Female Voice): A terrifying reality check. The matrix, the system, how they are being lied to.
    Phase 3 (Action - Male Voice): The violent awakening. "Wake up", "Leave the system", "Start today".
    
    You must also select 3 highly relevant emojis for this specific script.
    You must also select 3 Hex colors (neon, cyberpunk, or dark aesthetic) for the captions.
    
    Output strictly in this JSON format, nothing else:
    {
      "topic": "The brief topic name",
      "script_phase_1": "The hindi script (roman letters) for the male hook.",
      "script_phase_2": "The hindi script (roman letters) for the female paranoia.",
      "script_phase_3": "The hindi script (roman letters) for the male action.",
      "emojis": ["👁️", "🩸", "💰"],
      "colors": ["#FF0055", "#00FFCC", "#FFFFFF"]
    }
    """
    
    print("📡 Querying the neural network for today's viral hook...")
    response = model.generate_content(system_prompt)
    
    # Parse the JSON response
    try:
        raw_json = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw_json)
        print(f"✅ Generated 100% Unique Script: [{data['topic']}]")
        return data
    except Exception as e:
        print("❌ Failed to parse Gemini response. Retrying...")
        print("Raw response:", response.text)
        exit(1)

def inject_to_factory(data: Dict):
    """
    Saves the generated AI data into a JSON file that the Video Engine (generate.py and MainVideo.tsx) reads.
    """
    output_path = os.path.join(os.path.dirname(__file__), "daily_script.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"💾 Injected daily script into Factory Engine at {output_path}")

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🔥 INITIATING GEMINI AUTONOMOUS FACTORY 🔥")
    print("="*50 + "\n")
    
    daily_data = generate_daily_masterpiece()
    inject_to_factory(daily_data)
    
    print("\n🚀 Ready. You can now run `python orchestrator/generate.py` to compile the video.")
