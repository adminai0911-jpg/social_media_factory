#!/usr/bin/env python3
"""
The ULTIMATE Script & Voice Engine
Brain 2: Generates 10 hook variations, scores them by trigger strength, picks the absolute best.
Brain 3: Writes a 40-50 second deep-value script, 10 chronological Pexels keywords,
         and an algorithm-safe, anti-spam, anti-ban Instagram/FB/YouTube caption set.
         20% chance of a psychological Follow-Gate monetization promo script.
TTS: Randomly alternates between a premium female (SwaraNeural) and male (MadhurNeural) Hindi voice.
"""

import os
import json
import asyncio
import random
import logging
import edge_tts
import google.generativeai as genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ScriptVoiceEngine")

TREND_FILE = "current_trend.json"
SCRIPT_OUTPUT = "script_output.json"
AUDIO_OUTPUT = "audio_narration.mp3"
SRT_OUTPUT = "subtitles.srt"

# Two premium voices for variety — prevents "robot account" detection
VOICES = [
    {"name": "hi-IN-SwaraNeural", "gender": "Female", "style": "warm"},
    {"name": "hi-IN-MadhurNeural", "gender": "Male", "style": "authoritative"},
]

async def generate_narration_and_subtitles(text, voice):
    logger.info(f"Generating TTS Audio with voice '{voice}'...")
    communicate = edge_tts.Communicate(text, voice)
    submaker = edge_tts.SubMaker()

    with open(AUDIO_OUTPUT, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

    logger.info(f"TTS Audio saved to '{AUDIO_OUTPUT}'")
    
    with open(SRT_OUTPUT, "w", encoding="utf-8") as srt_file:
        srt_file.write(submaker.get_srt())
    logger.info(f"Subtitles saved to '{SRT_OUTPUT}'")

def build_hindi_script():
    logger.info("Initializing Brains 2 & 3...")
    
    if not os.path.exists(TREND_FILE):
        logger.warning("No trend file found. Using fallback.")
        fallback = {
            "topic": "AI Tools se Paise Kamao",
            "virality_score": 9,
            "emotional_trigger": "Greed",
            "summary": "How Indians are silently earning 50,000 rupees per month using free AI tools from home.",
            "news_snippets": ["यह 1 सच्चाई जो कोई नहीं बताता...", "हर कोई यह जानना चाहता है..."],
            "niche": "Wealth",
            "region": "IN"
        }
        with open(TREND_FILE, "w", encoding="utf-8") as f:
            json.dump(fallback, f, indent=2)

    with open(TREND_FILE, "r", encoding="utf-8") as f:
        trend_data = json.load(f)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY")
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    try:
        # ═══════════════════════════════════════════════════
        # BRAIN 2: The Hook Optimizer (10 hooks, scored)
        # ═══════════════════════════════════════════════════
        logger.info("Executing Brain 2: The Hook Optimizer...")
        brain_2_prompt = f"""
You are Brain 2 (The Hook Optimizer) for viral Indian short-form content.

Topic: {trend_data['topic']}
Context: {trend_data['summary']}
Emotional Trigger: {trend_data.get('emotional_trigger', 'Curiosity')}
Reference viral snippets: {', '.join(trend_data.get('news_snippets', []))}

Your task: Generate exactly 10 DEVASTATING hook variations in Hindi (Devanagari script only).
Each hook must stop someone from scrolling within 0.5 seconds.
Exploit one of these 6 psychological triggers: Fear, Greed, Ego, Curiosity, Shock, Belonging.
Hooks must be 3-8 words maximum. No full sentences — just a PUNCH.

Score each hook from 1 to 10 on Scroll-Stop Power.

Return ONLY this exact JSON:
{{
  "hooks": [
    {{"trigger": "Fear", "hook_text": "Hindi hook...", "score": 9}},
    {{"trigger": "Greed", "hook_text": "Hindi hook...", "score": 8}}
  ]
}}
"""
        r2 = model.generate_content(brain_2_prompt, generation_config={"response_mime_type": "application/json"})
        hooks_data = json.loads(r2.text).get("hooks", [])
        
        if not hooks_data:
            raise ValueError("Brain 2 returned no hooks.")
        
        # Sort hooks by score and pick the best one
        hooks_sorted = sorted(hooks_data, key=lambda x: x.get("score", 0), reverse=True)
        winning_hook = hooks_sorted[0]["hook_text"]
        logger.info(f"Brain 2 Best Hook (Score {hooks_sorted[0].get('score')}/10): {winning_hook}")

        # ═══════════════════════════════════════════════════
        # BRAIN 3: The Master Scriptwriter
        # ═══════════════════════════════════════════════════
        logger.info("Executing Brain 3: The Master Scriptwriter...")
        
        # Monetization Logic: 20% Follow-Gate promo, 80% pure value
        is_promo = random.random() < 0.20
        promo_instruction = ""
        if is_promo:
            logger.info("Brain 3: PROMO MODE — Generating Follow-Gate Script!")
            promo_instruction = """
MONETIZATION INSTRUCTION: This is a Promo Script.
You MUST:
1. Build up excitement about a "secret AI tool or method" that earns money from home.
2. NEVER use the phrase "link in bio" — this gets flagged by Instagram AI.
3. End the spoken script with this exact line (translate to natural Hindi): "Mujhe follow karo abhi, bio mein link hai, kal delete ho sakta hai!"
4. In the instagram_caption, write: "Bio link kal delete ho sakta hai. Jaldi dekho! 🔥 Follow karo!"
"""
        
        brain_3_prompt = f"""
You are Brain 3 (The Master Viral Scriptwriter) for premium Indian short-form video.

Theme: {trend_data['topic']}
Niche: {trend_data.get('niche', 'General')}
Context: {trend_data['summary']}
Emotional Core: {trend_data.get('emotional_trigger', 'Curiosity')}
Opening Hook (MUST be word-for-word the FIRST sentence): {winning_hook}
{promo_instruction}

MISSION: Write a script that:
1. GRABS attention with the hook (0 to 2 seconds).
2. BUILDS tension with a problem or shocking fact (3 to 15 seconds).
3. DELIVERS deep value or a twist (16 to 38 seconds).
4. ENDS with a Loop Ending that makes them watch from the beginning again (38 to 45 seconds).

STRICT RULES:
- Total spoken length: 40 to 50 seconds (80 to 100 Hindi words).
- ONLY Hindi in Devanagari script. Zero English words or latin characters.
- Provide EXACTLY 10 descriptive English Pexels search queries matching the story chronologically (what happens on screen while each part of the script plays). Make them cinematic and visual.
- Write the instagram_caption and youtube_title in Hindi. Vary the style every time (sometimes short and punchy, sometimes a longer emotional story).
- ANTI-BAN RULE: Instagram hashtags must NEVER be repeated from common lists. Use niche-specific, unique hashtags.
- youtube_title: Write a curiosity-gap title in Hindi (under 70 characters) that makes people click.
- The instagram_caption CTA must vary: sometimes "Tag your friend", sometimes "Save this before it's deleted", sometimes "Who needs to see this?".

Return ONLY this exact JSON schema:
{{
  "thumbnail_text": "2-4 word clickbait Hindi phrase",
  "script_text": "Full 80-100 word Hindi script in Devanagari...",
  "pexels_keywords": ["cinematic keyword 1", "...", "cinematic keyword 10"],
  "instagram_caption": "Engaging Hindi caption with emoji and CTA...",
  "instagram_hashtags": ["#Hashtag1", "#Hashtag2", "#Hashtag3", "#Hashtag4", "#Hashtag5"],
  "youtube_title": "Hindi YouTube Shorts title...",
  "youtube_tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
}}
"""
        r3 = model.generate_content(brain_3_prompt, generation_config={"response_mime_type": "application/json"})
        script_json = json.loads(r3.text)
        
        logger.info(f"Brain 3 Script generated. Thumbnail: '{script_json.get('thumbnail_text', 'N/A')}'")
        
        with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as sf:
            json.dump(script_json, sf, ensure_ascii=False, indent=2)
        
        return script_json
        
    except Exception as e:
        logger.error(f"Brain execution failed: {e}")
        fallback_script = {
            "thumbnail_text": "यह 1 राज़ जान लो!",
            "script_text": "क्या आपको पता है कि भारत में हर महीने लाखों लोग सिर्फ AI टूल्स से पैसे कमा रहे हैं? बिना ऑफिस, बिना बॉस, सिर्फ अपने फोन से। एक बार शुरू करो, फिर ज़िंदगी बदल जाएगी। पर एक गलती है जो सब करते हैं — और वो गलती शुरू में होती है। क्या आप जानना चाहते हैं? पहले से शुरू करते हैं।",
            "pexels_keywords": [
                "indian man using smartphone working from home", "money and coins on table india",
                "laptop screen showing charts and graphs", "young indian entrepreneur success",
                "ai robot futuristic technology", "person typing on computer late night india",
                "financial freedom sunrise india", "digital nomad working cafe india",
                "mobile phone showing notifications money", "success celebration india office"
            ],
            "instagram_caption": "यह 1 गलती मत करना! 🚨 अगर आप भी घर से पैसे कमाना चाहते हो तो इसे Save करो। अपने उस दोस्त को Tag करो जिसे यह जानना चाहिए! 👇",
            "instagram_hashtags": ["#GharSeKamao", "#AIIndia", "#DigitalIndia2026", "#PaiseKaRaaz", "#IndianCreator"],
            "youtube_title": "यह राज़ जो कोई नहीं बताता — AI से पैसे कैसे कमाएं",
            "youtube_tags": ["ai tools india", "ghar se paise kaise kamaye", "passive income india 2026", "hindi motivation", "digital india"]
        }
        with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as sf:
            json.dump(fallback_script, sf, ensure_ascii=False, indent=2)
        return fallback_script

def run():
    script_data = build_hindi_script()
    
    # Randomly pick male or female voice for maximum variety and anti-bot detection
    voice_choice = random.choice(VOICES)
    logger.info(f"Voice Engine: Selecting {voice_choice['gender']} voice '{voice_choice['name']}' for this video.")
    
    asyncio.run(generate_narration_and_subtitles(script_data["script_text"], voice_choice["name"]))

if __name__ == "__main__":
    run()
