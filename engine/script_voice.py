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
    logger.info("Initializing Brain 2 & Brain 3...")
    
    # Ensure trend file exists
    if not os.path.exists(TREND_FILE):
        logger.warning(f"'{TREND_FILE}' not found. Generating fallback...")
        fallback = {
            "topic": "Digital India AI Evolution",
            "traffic": "500K+",
            "summary": "Artificial Intelligence adoption sky-rockets across India.",
            "news_snippets": ["India launches national AI program"],
            "region": "IN"
        }
        with open(TREND_FILE, "w", encoding="utf-8") as f:
            json.dump(fallback, f, indent=2)

    with open(TREND_FILE, "r", encoding="utf-8") as f:
        trend_data = json.load(f)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is not set!")
        raise ValueError("Missing GEMINI_API_KEY")
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    try:
        # ---------------------------------------------------------
        # PHASE 2: Brain 2 (The Hook Optimizer)
        # ---------------------------------------------------------
        logger.info("Executing Brain 2: The Hook Optimizer...")
        brain_2_prompt = f"""
You are Brain 2 (The Hook Optimizer).
Your task is to study the top-performing reels in the following niche and break down the hook structure.
Theme: {trend_data['topic']}
Context: {trend_data['summary']}

Generate 5 NEW hook variations (in Hindi) that are curiosity-driven, emotionally charged, and optimized to stop scrolling instantly.
Focus on triggers like Surprise, Fear, Ego, Urgency, or Desire.
They must be aggressive and under 2 seconds when spoken.

Return exactly 5 hooks in this JSON schema:
{{
  "hooks": [
    {{"trigger": "Fear", "hook_text": "Hindi hook text..."}},
    {{"trigger": "Ego", "hook_text": "Hindi hook text..."}}
  ]
}}
"""
        response_2 = model.generate_content(brain_2_prompt, generation_config={"response_mime_type": "application/json"})
        hooks_data = json.loads(response_2.text).get("hooks", [])
        if not hooks_data: raise ValueError("Brain 2 failed to generate hooks.")
        
        # Brain 2 picks the most aggressive hook
        winning_hook = hooks_data[0]["hook_text"]
        logger.info(f"Brain 2 Selected Hook: {winning_hook}")

        # ---------------------------------------------------------
        # PHASE 3: Brain 3 (The Scriptwriter)
        # ---------------------------------------------------------
        logger.info("Executing Brain 3: The Scriptwriter...")
        
        # 20% Affiliate Promo Logic (ManyChat DM Funnel)
        import random
        is_promo = random.random() < 0.20
        promo_instruction = ""
        if is_promo:
            logger.info("Brain 3: Generating ManyChat Keyword Affiliate Script!")
            promo_instruction = "IMPORTANT: This is a Monetization Promo Script! You must pitch a secret AI tool or guide that makes money. NEVER say 'link in bio'. You MUST end the spoken script exactly with: 'Follow me and comment the word PROFIT and I will DM you the secret tool!'. Also, in the instagram_caption, explicitly tell them to follow you and comment 'PROFIT' for the link."
            
        brain_3_prompt = f"""
You are Brain 3 (The Viral Scriptwriter).
Take the following Theme and the Winning Hook to write an addictive 15-20 second Hindi script.

Theme: {trend_data['topic']}
Context: {trend_data['summary']}
Winning Hook (MUST be the first sentence): {winning_hook}
{promo_instruction}

Strict Requirements:
1. The script must be complete within 15-20 seconds when read (around 35 to 55 words).
2. START WITH THE WINNING HOOK exactly as provided.
3. Tell a high-retention micro-story that builds suspense.
4. MUST USE A LOOP ENDING.
5. The spoken script must be ONLY in Hindi (Devanagari). No english characters or symbols.
6. Provide three highly descriptive English search queries for Pexels to pull relevant cinematic vertical (9:16) stock b-roll clips.
7. Design a 2 to 4 word, highly clickbait Hindi phrase for the `thumbnail_text`. Make it punchy (e.g., "ये 1 गलती मत करना!").
8. ANTI-SPAM CAPTION VARIANCE: Design a highly engaging Hindi caption. Drastically vary length/style. Include a strong CTA ("Tag a friend", "Save this").
9. ANTI-SPAM HASHTAG VARIANCE: Provide EXACTLY 3-5 unique, hyper-relevant hashtags.

Return response in this JSON schema:
{{
  "thumbnail_text": "2-4 word clickbait hindi phrase",
  "script_text": "आपके 15 सेकंड का हिंदी ऑडियो नरेशन...",
  "pexels_keywords": ["query 1", "query 2", "query 3"],
  "instagram_caption": "धमाकेदार हिंदी कैप्शन... 🔥",
  "instagram_hashtags": "#InstaIndia #TrendingHindi #ViralReels"
}}
"""
        response_3 = model.generate_content(brain_3_prompt, generation_config={"response_mime_type": "application/json"})
        script_json = json.loads(response_3.text)
        logger.info("Brain 3 successfully generated the viral script.")
        
        with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as sf:
            json.dump(script_json, sf, ensure_ascii=False, indent=2)
            
        return script_json
        
    except Exception as e:
        logger.error(f"Brain execution failed: {e}")
        fallback_script = {
            "thumbnail_text": "यह 1 गलती मत करना!",
            "script_text": "क्या आपको पता है कि भारत में एआई क्रांति कितनी तेजी से बढ़ रही है? छोटे व्यापारी अब एआई टूल्स का उपयोग करके अपना बिजनेस दोगुना कर रहे हैं। तकनीक की दुनिया में आगे रहने के लिए हमें अभी फॉलो करें!",
            "pexels_keywords": ["cyberpunk dynamic mumbai street", "indian software engineer typing", "artificial intelligence network loop"],
            "instagram_caption": "भारत में AI का तहलका! क्या आपका बिजनेस रेडी है? हमें फॉलो करें और इस रील को सेव करें! 🇮🇳💻",
            "instagram_hashtags": "#AIRevolution #TechIndia #DigitalIndia #ReelsIndia #HindiTech"
        }
        with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as sf:
            json.dump(fallback_script, sf, ensure_ascii=False, indent=2)
        return fallback_script

def run():
    script_data = build_hindi_script()
    asyncio.run(generate_narration_and_subtitles(script_data["script_text"]))

if __name__ == "__main__":
    run()
