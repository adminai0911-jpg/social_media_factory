import os
import sys
import json
from dotenv import load_dotenv
import asyncio
import logging
import edge_tts
import shutil
import subprocess

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(env_path)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - V5_ENGINE - %(levelname)s - %(message)s")
logger = logging.getLogger("Brain_V3")

API_KEY = os.environ.get("GEMINI_API_KEY", "")

def generate_script():
    logger.info("Generating explosive v3 script...")
    
    if not API_KEY:
        logger.warning("No API Key. Using fallback script.")
        return {
            "title": "The Simulation",
            "script_text": "This fact will mess with your perception of time. Did you know that Cleopatra lived closer in time to the iPhone than she did to the building of the Great Pyramid? When the Great Pyramid was being built, woolly mammoths were still roaming the earth. Every time you think history is long, remember that."
        }
    
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=API_KEY.split(",")[0].strip())
        
        prompt = """
        You are a master scriptwriter for the top 0.01% viral TikToks and YouTube Shorts. 
        Write a highly engaging, high-retention 30-second script for a faceless channel.
        Topic: A Dark Psychology fact, mind-blowing wealth hack, or conspiracy.
        
        CRITICAL RULES (THE LOOPHOLE ENGINE):
        1. ZERO INTRODUCTIONS. Start mid-sentence with extreme high energy.
        2. EXTREME PACE: The script must be breathless. Short, punchy sentences. Overstimulate the brain so the viewer has no time to think. 
        3. AGGRESSIVE HOOKS: Use words like 'WARNING', 'ILLEGAL', 'SECRET', 'HIJACK'.
        4. THE SLOT MACHINE TENSION: Halfway through, explicitly say something like "Look at the numbers spinning on your screen" or "Don't blink or you'll miss the flash."
        5. INFINITE LOOP: The script MUST be an infinite loop. The final sentence must grammatically cut off and flow PERFECTLY into the very first word of the script.
        Example Loop: End with "Which is exactly why you need to..." -> Start with "...stop trusting your friends."
        6. Output ONLY pure raw JSON with the following structure:
        {
          "script_text": "The full spoken text as one continuous string.",
          "title": "A short dramatic title"
        }
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.9)
        )
        text = response.text.strip()
        if text.startswith("```json"): text = text[7:]
        if text.startswith("```"): text = text[3:]
        if text.endswith("```"): text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        logger.error(f"Failed to generate script: {e}")
        return {
            "title": "The Simulation",
            "script_text": "This fact will mess with your perception of time. Did you know that Cleopatra lived closer in time to the iPhone than she did to the building of the Great Pyramid? When the Great Pyramid was being built, woolly mammoths were still roaming the earth. Every time you think history is long, remember that."
        }

async def generate_tts_and_timings(script_json, output_audio="audio.mp3", output_timings="timings.json"):
    logger.info("Generating TTS and extracting precise word timings...")
    
    full_text = script_json["script_text"]
    
    # Use an intense voice, male or female
    communicate = edge_tts.Communicate(full_text, "en-US-ChristopherNeural", rate="+15%")
    
    words = []
    
    with open(output_audio, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                words.append({
                    "word": chunk["text"],
                    "start": chunk["offset"] / 10000000.0,
                    "end": (chunk["offset"] + chunk["duration"]) / 10000000.0
                })
    
    with open(output_timings, "w", encoding="utf-8") as f:
        json.dump(words, f, indent=2)
        
    logger.info(f"Saved TTS to {output_audio} and timings to {output_timings}")
    return words

def run_pipeline():
    script = generate_script()
    
    public_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio", "public"))
    os.makedirs(public_dir, exist_ok=True)
    
    audio_path = os.path.join(public_dir, "audio.mp3")
    timings_path = os.path.join(public_dir, "timings.json")
    
    timings = asyncio.run(generate_tts_and_timings(script, audio_path, timings_path))
    
    props = {
        "title": script["title"],
        "script_text": script["script_text"],
        "timings": timings,
        "totalDurationInSeconds": timings[-1]["end"] + 1.0 if timings else 15.0
    }
    
    props_path = os.path.join(public_dir, "props.json")
    with open(props_path, "w", encoding="utf-8") as f:
        json.dump(props, f, indent=2)
        
    logger.info(f"Props saved to {props_path}")
    
    logger.info("Triggering Remotion Render...")
    studio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio"))
    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "final_reel_v5.mp4"))
    
    cmd = [
        "npx", "remotion", "render", "src/index.ts", "MainVideo", out_file,
        "--props=public/props.json"
    ]
    
    try:
        subprocess.run(cmd, cwd=studio_dir, check=True, shell=True)
        logger.info(f"✅ SUCCESSFULLY RENDERED V5 REEL: {out_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Remotion render failed: {e}")

if __name__ == "__main__":
    run_pipeline()
