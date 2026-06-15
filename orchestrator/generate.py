import os
import sys
import json
import asyncio
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - V5_ENGINE - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- V17 MULTI-VOICE HINDI PODCAST SCRIPT ---
# Segment 1: Euphoria (Female Voice)
# Segment 2: Paranoia (Male Voice)
# Segment 3: Gamification (Male Voice)
SEGMENTS = [
    {
        "text": "रिलैक्स... अपनी आँखें बंद करो। तुम्हें कैसा लग रहा है? बिल्कुल शांत... सब कुछ बिल्कुल परफेक्ट है।",
        "voice": "hi-IN-SwaraNeural"
    },
    {
        "text": "तुम्हें लगता है तुम सुरक्षित हो? जाग जाओ! यह सब एक धोखा है! तुम एक सिमुलेशन में फँस गए हो!",
        "voice": "hi-IN-MadhurNeural"
    },
    {
        "text": "सिस्टम हैक हो चुका है। सच तुम्हारे सामने है। इसे अभी शेयर करो, इससे पहले कि बहुत देर हो जाए।",
        "voice": "hi-IN-MadhurNeural"
    }
]

async def generate_audio_segment(index, text, voice, out_dir):
    temp_mp3 = os.path.join(out_dir, f"temp_{index}.mp3")
    temp_json = os.path.join(out_dir, f"temp_{index}_timings.json")
    
    cmd = [
        sys.executable, "-m", "edge_tts",
        "--text", text,
        "--voice", voice,
        "--write-media", temp_mp3,
        "--write-subtitles", temp_json
    ]
    
    logger.info(f"Generating segment {index} with voice {voice}...")
    process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        logger.error(f"Failed to generate segment {index}: {stderr.decode()}")
        sys.exit(1)
        
    return temp_mp3, temp_json

def get_audio_duration(file_path):
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(result.stdout.strip())

async def main():
    logger.info("\u26a0\ufe0f INITIATING V17 MULTI-VOICE CHAOS ENGINE...")
    
    studio_public = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio", "public"))
    os.makedirs(studio_public, exist_ok=True)
    
    mp3_files = []
    json_files = []
    
    # Generate parts
    for i, seg in enumerate(SEGMENTS):
        # Save directly as audio_0.mp3 etc
        temp_mp3 = os.path.join(studio_public, f"audio_{i}.mp3")
        temp_json = os.path.join(studio_public, f"temp_{i}_timings.json")
        
        cmd = [
            sys.executable, "-m", "edge_tts",
            "--text", seg["text"],
            "--voice", seg["voice"],
            "--write-media", temp_mp3,
            "--write-subtitles", temp_json
        ]
        
        logger.info(f"Generating segment {i} with voice {seg['voice']}...")
        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            logger.error(f"Failed to generate segment {i}: {stderr.decode()}")
            sys.exit(1)
            
        mp3_files.append(temp_mp3)
        json_files.append(temp_json)
        
    # Manually construct timings and offsets since edge-tts word-boundaries fail on Hindi
    logger.info("Constructing Row-based timings and audio offsets...")
    
    # We will use approximate offsets. 
    # Segment 0 usually takes ~8 seconds. Segment 1 ~8 seconds. Segment 2 ~8 seconds.
    # To be safe and ensure no overlap, we will space them out.
    audio_offsets = [0.0, 11.0, 21.0]
    
    final_timings = [
        # Segment 0 (0 to 11s)
        {"word": "रिलैक्स... अपनी आँखें बंद करो।", "start": 0.5, "end": 4.0},
        {"word": "तुम्हें कैसा लग रहा है?", "start": 4.5, "end": 7.0},
        {"word": "बिल्कुल शांत... सब परफेक्ट है।", "start": 7.5, "end": 10.5},
        
        # Segment 1 (11 to 21s)
        {"word": "तुम्हें लगता है तुम सुरक्षित हो?", "start": 11.5, "end": 14.0},
        {"word": "जाग जाओ! यह सब एक धोखा है!", "start": 14.5, "end": 17.5},
        {"word": "तुम एक सिमुलेशन में फँस गए हो!", "start": 18.0, "end": 20.5},
        
        # Segment 2 (21 to 30s)
        {"word": "सिस्टम हैक हो चुका है।", "start": 21.5, "end": 24.0},
        {"word": "सच तुम्हारे सामने है।", "start": 24.5, "end": 26.5},
        {"word": "इसे अभी शेयर करो...", "start": 27.0, "end": 28.5},
        {"word": "...इससे पहले कि बहुत देर हो जाए।", "start": 28.5, "end": 30.0}
    ]
    
    # Write final timings
    final_json_path = os.path.join(studio_public, "timings.json")
    with open(final_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "timings": final_timings,
            "audio_offsets": audio_offsets
        }, f, indent=2)
        
    # Cleanup temp JSON files
    for f in json_files:
        if os.path.exists(f):
            try:
                os.remove(f)
            except:
                pass
            
    # Write script text
    script_path = os.path.join(studio_public, "script.txt")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(" ".join([s["text"] for s in SEGMENTS]))
        
    logger.info("Triggering Remotion Render (V17 - MultiVoice Chaos)...")
    studio_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remotion-studio"))
    out_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "final_reel_v17_hindi_chaos.mp4"))
    
    cmd = [
        "npx", "remotion", "render", "src/index.ts", "MainVideo", out_file,
        "--props=./public/timings.json",
        f"--totalDurationInSeconds=30.0", # Force exactly 30s
        "--videoBitrate=40M",
        "--codec=h264"
    ]
    
    try:
        subprocess.run(cmd, cwd=studio_dir, check=True, shell=True)
        logger.info(f"\u2705 SUCCESSFULLY RENDERED V17 REEL: {out_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Render failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
