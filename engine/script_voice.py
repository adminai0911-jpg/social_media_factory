#!/usr/bin/env python3
"""
Script & Voice Engine
Pulls the latest trend from 'current_trend.json', utilizes Gemini 1.5 Flash 
to craft an addictive 15-second Hindi script, and compiles high-quality 
neural TTS audio ('audio_narration.mp3') and exact-timed subtitles ('subtitles.srt') 
using edge-tts (SwaraNeural profile).
"""

import os
import json
import asyncio
import logging
import edge_tts
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ScriptVoiceEngine")

TREND_FILE = "current_trend.json"
SCRIPT_OUTPUT = "script_output.json"
AUDIO_OUTPUT = "audio_narration.mp3"
SRT_OUTPUT = "subtitles.srt"

async def generate_narration_and_subtitles(text, voice="hi-IN-SwaraNeural"):
    """
    Asynchronously invokes edge-tts to stream audio and compile dynamic,
    millisecond-level word boundaries into a precise SRT subtitle file.
    """
    logger.info(f"Generating TTS Audio via edge-tts with voice '{voice}'...")
    communicate = edge_tts.Communicate(text, voice)
    submaker = edge_tts.SubMaker()

    with open(AUDIO_OUTPUT, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

    logger.info(f"TTS Audio file saved to '{AUDIO_OUTPUT}'")
    
    # Save the subtitle track
    with open(SRT_OUTPUT, "w", encoding="utf-8") as srt_file:
        srt_file.write(submaker.get_srt())
        
    logger.info(f"Subtitles (SRT) successfully generated and saved to '{SRT_OUTPUT}'")

def build_hindi_script():
    logger.info("Initializing Gemini API script generation...")
    
    # Ensure trend file exists
    if not os.path.exists(TREND_FILE):
        logger.warning(f"'{TREND_FILE}' not found. Generating default trend info...")
        # Create a fallback current_trend.json if missing
        fallback = {
            "topic": "Digital India AI Evolution",
            "traffic": "500K+",
            "summary": "Artificial Intelligence adoption sky-rockets across India, changing how businesses operate.",
            "news_snippets": ["India launches national AI program", "AI tools driving efficiency in India"],
            "region": "IN"
        }
        with open(TREND_FILE, "w", encoding="utf-8") as f:
            json.dump(fallback, f, indent=2)

    with open(TREND_FILE, "r", encoding="utf-8") as f:
        trend_data = json.load(f)

    # Configure Gemini API
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is not set!")
        raise ValueError("Missing GEMINI_API_KEY")
        
    genai.configure(api_key=api_key)
    
    # Prompt engineering for addictive short-form AI Cinematic script in Hindi
    prompt = f"""
You are an elite, highly creative viral content architect specializing in fast-paced, high-retention AI Cinematic Reels for Indian audiences.
Your goal is to transform the following theme into an addictive, dark, motivational, or mysterious 15-second script translated into highly conversational, snappy Hindi (written in clean Devanagari script).

Theme: {trend_data['topic']}
Context: {trend_data['summary']}
Inspiration: {", ".join(trend_data.get('news_snippets', []))}

Strict Requirements:
1. The script must be short and complete within exactly 15 seconds when read (around 35 to 45 words maximum).
2. START WITH A VIRAL 1-SECOND HOOK (e.g., "क्या आपको पता है...", "ये एक गलती...", "२०३५ में...").
3. Tell a deep, emotional, or mysterious micro-story.
4. MUST USE A LOOP ENDING (The last sentence must seamlessly connect back to the first sentence).
5. The spoken script must be ONLY in Hindi (Devanagari script) and MUST NOT contain any english words in Latin script, symbols, bullet points, numbers in digits, or emojis in the text.
6. Provide three highly descriptive English search queries for Pexels to pull relevant high-quality, cinematic, dark, luxury, or sci-fi vertical (9:16) stock b-roll clips (e.g., "dark luxury mansion vertical", "futuristic cyberpunk city vertical", "sad man raining vertical").
7. Design a clickbait, engagement-rich Hindi caption with 5 high-velocity hashtags for Instagram.

You MUST return your response in the following precise JSON schema format:
{{
  "script_text": "आपके 15 सेकंड का हिंदी ऑडियो नरेशन बिना किसी इंग्लिश शब्द, सिंबल, या इमोजी के यहाँ होगा।",
  "pexels_keywords": ["specific cinematic vertical stock video query 1", "specific cinematic vertical stock video query 2", "specific cinematic vertical stock video query 3"],
  "instagram_caption": "धमाकेदार हिंदी कैप्शन जो ऑडियंस को अट्रैक्ट करे। 🔥🚀",
  "instagram_hashtags": "#InstaIndia #TrendingHindi #ViralTrends #ReelsIndia #DigitalIndia"
}}
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        script_json = json.loads(response.text)
        logger.info("Successfully generated scripted assets from Gemini.")
        logger.info(f"Generated Script: {script_json['script_text']}")
        logger.info(f"Pexels Keywords: {script_json['pexels_keywords']}")
        
        # Save assets for downstream render/publishing
        with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as sf:
            json.dump(script_json, sf, ensure_ascii=False, indent=2)
            
        return script_json
        
    except Exception as e:
        logger.error(f"Failed to generate content from Gemini API: {e}")
        # Return fallback script to keep the system robust and fault-tolerant
        fallback_script = {
            "script_text": "क्या आपको पता है कि भारत में एआई क्रांति कितनी तेजी से बढ़ रही है? छोटे व्यापारी अब एआई टूल्स का उपयोग करके अपना बिजनेस दोगुना कर रहे हैं। तकनीक की दुनिया में आगे रहने के लिए हमें अभी फॉलो करें!",
            "pexels_keywords": ["cyberpunk dynamic mumbai street", "indian software engineer typing", "artificial intelligence network loop"],
            "instagram_caption": "भारत में AI का तहलका! क्या आपका बिजनेस रेडी है? 🇮🇳💻",
            "instagram_hashtags": "#AIRevolution #TechIndia #DigitalIndia #ReelsIndia #HindiTech"
        }
        with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as sf:
            json.dump(fallback_script, sf, ensure_ascii=False, indent=2)
        logger.warning("Saved fallback scripted assets due to Gemini API failure.")
        return fallback_script

def run():
    script_data = build_hindi_script()
    asyncio.run(generate_narration_and_subtitles(script_data["script_text"]))

if __name__ == "__main__":
    run()
