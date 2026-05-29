#!/usr/bin/env python3
"""
Master Orchestrator
Sequentially coordinates:
1. Scouting trends (`scrapers.trend_scout`)
2. Writing script & generating voiceover (`engine.script_voice`)
3. Sourcing vertical clips & rendering final reel (`studio.video_renderer`)
4. Uploading and publishing to Instagram (`publisher.meta_api`)

Supports Dual Modes:
- CLI mode: Run `python main.py` for direct manual execution.
- Web Service mode: Exposes a Flask app (`app`) to handle HTTP trigger calls 
  from Google Cloud Scheduler when deployed as a serverless container.
"""

import sys
import os
import logging

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
from flask import Flask, jsonify
from dotenv import load_dotenv

# Setup logging to stdout for Cloud Logging compatibility
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SocialMediaFactoryMaster")

# Load environment variables (supports local testing via .env file)
load_dotenv()

# Initialize Flask Application
app = Flask(__name__)

def verify_environment():
    """
    Checks that all essential configuration variables are present.
    """
    essential_vars = [
        "GEMINI_API_KEY",
        "PEXELS_API_KEY",
        "GCP_GCS_BUCKET_NAME",
        "INSTAGRAM_BUSINESS_ACCOUNT_ID",
        "META_USER_ACCESS_TOKEN"
    ]
    
    missing = [var for var in essential_vars if not os.environ.get(var)]
    
    if missing:
        logger.warning(f"Missing essential configuration variables: {', '.join(missing)}")
        logger.warning("The pipeline might fail during downstream operations.")
    else:
        logger.info("All essential environment configuration variables present.")

def execute_pipeline():
    """
    Executes the 4-step pipeline end-to-end.
    """
    logger.info("--- STARTING SOCIAL MEDIA AUTONOMOUS FACTORY PIPELINE ---")
    
    # ADVANCED HUMAN JITTER:
    # GitHub Actions wakes this server up at exactly 8:30am, 1:30pm, and 7:30pm.
    import time
    import random
    
    # 15% chance to post at a completely weird, unusual time (simulating a messy human schedule)
    is_unusual_time = random.random() < 0.15 
    
    if is_unusual_time:
        jitter_seconds = random.randint(3600, 10800) # Sleep for 1 to 3 hours!
        logger.info(f"Advanced Jitter: Triggering UNUSUAL POST TIME. Sleeping for {jitter_seconds//60} minutes...")
    else:
        # Standard window: Sleep anywhere between 0 and 60 minutes
        # This spreads the post randomly across the 8:30-9:30, 1:30-2:30 windows.
        jitter_seconds = random.randint(0, 3600)
        logger.info(f"Advanced Jitter: Standard window delay. Sleeping for {jitter_seconds//60} minutes...")
        
    time.sleep(jitter_seconds)
    
    verify_environment()
    
    # 1. Trend Scouting
    logger.info("\n--- STEP 1: SCOUTING VIRAL INDIA TRENDS ---")
    from scrapers.trend_scout import scout_top_trend
    scout_top_trend()
    logger.info("Step 1 Complete: Trend cached.")
        
    # 2. Scripting & Voice Generation
    logger.info("\n--- STEP 2: CREATING SCRIPT & NEURAL TTS AUDIO ---")
    from engine.script_voice import run as run_script_voice
    run_script_voice()
    logger.info("Step 2 Complete: Script, b-roll keywords, and TTS complete.")
        
    # 3. Studio Video Rendering
    logger.info("\n--- STEP 3: DOWNLOADING B-ROLL & COMPILING REEL ---")
    from studio.video_renderer import render as run_renderer
    run_renderer()
    logger.info("Step 3 Complete: HD vertical reel compiled with custom dynamic subtitles.")
        
    # 4. Meta Instagram Publishing
    logger.info("\n--- STEP 4: INSTAGRAM METADATA PUBLISHING ---")
    from publisher.facebook_api import publish_to_facebook
    from publisher.youtube_api import publish_to_youtube
    
    import json
    try:
        with open("script_output.json", "r", encoding="utf-8") as f:
            script_data = json.load(f)
    except Exception as e:
        logger.error(f"Failed to load script_output.json: {e}")
        script_data = {}
        
    caption = script_data.get("instagram_caption", "Amazing Video! 🔥")
    tags = script_data.get("instagram_hashtags", ["#viral"])
    if isinstance(tags, str):
        tags = tags.split()
    
    tags_str = " ".join(tags)
    full_caption = f"{caption}\n\n{tags_str}"
    
    # 4a. Publish to Instagram (Meta API)
    logger.info("Publishing to Instagram...")
    from publisher.meta_api import run as run_meta_publisher
    run_meta_publisher()
    
    # 4b. Publish to Facebook Reels
    logger.info("Publishing to Facebook Reels...")
    publish_to_facebook("final_reel.mp4", full_caption)
    
    # 4c. Publish to YouTube Shorts
    logger.info("Publishing to YouTube Shorts...")
    # Extract just the tags list for YT without hashtags
    yt_tags = [t.strip('#') for t in tags if t.startswith('#')]
    publish_to_youtube("final_reel.mp4", script_data.get("thumbnail_text", "Must Watch"), caption, yt_tags)
    
    logger.info("\n--- PIPELINE SUCCESSFULLY EXECUTED ---")

@app.route("/", methods=["GET", "POST"])
@app.route("/run", methods=["GET", "POST"])
def http_trigger():
    """
    GCP Cloud Run Endpoint
    Handles the HTTP request generated by Google Cloud Scheduler 3 times a day.
    """
    logger.info("Pipeline triggered via Google Cloud Run HTTP endpoint.")
    try:
        execute_pipeline()
        return jsonify({
            "status": "success",
            "message": "Instagram Reel compiled and published successfully!"
        }), 200
    except Exception as e:
        logger.error(f"HTTP Pipeline execution encountered a critical error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Pipeline execution failed: {str(e)}"
        }), 500

if __name__ == "__main__":
    # If run directly as a CLI script, trigger the pipeline immediately
    logger.info("Starting master orchestrator in direct CLI mode...")
    try:
        execute_pipeline()
        sys.exit(0)
    except Exception as e:
        logger.critical(f"CLI Pipeline execution failed: {e}", exc_info=True)
        sys.exit(1)
