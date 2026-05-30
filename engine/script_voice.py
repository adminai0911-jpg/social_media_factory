#!/usr/bin/env python3
"""
THE ULTIMATE Script & Voice Engine — Phase 11 (AI Documentary Engine)

Brain 2: Generates 10 hook variations, scores each on Scroll-Stop Power (1-10), picks the highest.
Brain 3: Writes a 4-SCENE synchronized script (60s), generates 10 SCENE-SYNCHRONIZED AI Image Prompts
         (Midjourney style) that describe exactly what should be on screen.
TTS:     Alternates randomly between female (SwaraNeural) and male (MadhurNeural) voice.
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

TREND_FILE    = "current_trend.json"
SCRIPT_OUTPUT = "script_output.json"
AUDIO_OUTPUT  = "audio_narration.mp3"
SRT_OUTPUT    = "subtitles.srt"

VOICES = [
    {"name": "hi-IN-SwaraNeural",  "gender": "Female"},
    {"name": "hi-IN-MadhurNeural", "gender": "Male"},
]

async def generate_narration_and_subtitles(text, voice):
    logger.info(f"Generating TTS with voice '{voice}'...")
    communicate = edge_tts.Communicate(text, voice)
    submaker    = edge_tts.SubMaker()

    with open(AUDIO_OUTPUT, "wb") as audio_file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)

    logger.info(f"Audio saved: '{AUDIO_OUTPUT}'")
    with open(SRT_OUTPUT, "w", encoding="utf-8") as srt_file:
        srt_file.write(submaker.get_srt())
    logger.info(f"Subtitles saved: '{SRT_OUTPUT}'")

def build_hindi_script():
    logger.info("Initializing Brains 2 & 3 (AI Documentary Mode)...")

    if not os.path.exists(TREND_FILE):
        logger.warning("No trend file found. Using fallback trend.")
        fallback_trend = {
            "topic": "AI Tools se Ghar Baithe Paise Kamao",
            "virality_score": 9,
            "emotional_trigger": "Greed",
            "summary": "How ordinary Indians are earning 50,000 rupees per month using free AI tools from home without any boss or office.",
            "niche": "Wealth Building"
        }
        with open(TREND_FILE, "w", encoding="utf-8") as f:
            json.dump(fallback_trend, f, ensure_ascii=False, indent=2)

    with open(TREND_FILE, "r", encoding="utf-8") as f:
        trend_data = json.load(f)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY environment variable.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    try:
        # BRAIN 2
        logger.info("Executing Brain 2: Hook Optimizer...")
        brain_2_prompt = f"""
You are Brain 2 (The Hook Optimizer).
Topic: {trend_data['topic']}
Context: {trend_data['summary']}

Generate 10 DEVASTATING scroll-stopping hooks in Hindi (Devanagari only).
Hooks must be 3 to 8 words max. Score each from 1-10.
Return ONLY this JSON:
{{
  "hooks": [
    {{"hook_text": "Hindi hook...", "score": 9}}
  ]
}}
"""
        r2 = model.generate_content(brain_2_prompt, generation_config={"response_mime_type": "application/json"})
        hooks_data = json.loads(r2.text).get("hooks", [])
        if not hooks_data: raise ValueError("Brain 2 returned zero hooks.")
        hooks_sorted = sorted(hooks_data, key=lambda x: x.get("score", 0), reverse=True)
        winning_hook = hooks_sorted[0]["hook_text"]
        logger.info(f"Brain 2 Winner: {winning_hook}")

        # BRAIN 3
        logger.info("Executing Brain 3: Master Scriptwriter & AI Prompt Engineer...")
        is_promo = random.random() < 0.20
        promo_instruction = ""
        if is_promo:
            promo_instruction = """
MONETIZATION MODE:
- End Scene 4 with: "Follow karo abhi, bio mein link hai, kal gayab ho sakta hai!"
- In instagram_caption write: "Bio mein link hai! Kal delete ho sakta hai. Jaldi dekho 🔥 Follow karo!"
"""

        brain_3_prompt = f"""
You are Brain 3 (The Master Viral Scriptwriter & AI Art Director).
Theme: {trend_data['topic']}
Opening Hook: {winning_hook}
{promo_instruction}

SCRIPT STRUCTURE: 4 Scenes (60 seconds total)
SCENE 1 (0-5s) Hook: {winning_hook}
SCENE 2 (5-20s) Tension
SCENE 3 (20-52s) Deep Value
SCENE 4 (52-60s) Loop End

RULES:
1. script_text: Pure Devanagari Hindi. 120-130 words.
2. ai_image_prompts: EXACTLY 10 English image generation prompts for Pollinations AI (Midjourney style).
   CRITICAL: These prompts dictate the visual for each 6-second chunk of the script.
   Make them hyper-detailed, dramatic, 8k cinematic photography, indian context.
   Format: "Hyper-realistic cinematic photography of [subject doing action in setting], dramatic lighting, 8k resolution, photorealistic"
3. instagram_caption: Human-feel Hindi.
4. instagram_hashtags: 5 specific niche hashtags.
5. youtube_title & youtube_tags: For Shorts SEO.
6. facebook_caption: Storytelling format.

Return ONLY JSON:
{{
  "thumbnail_text": "2-4 word Hindi",
  "script_text": "Full script...",
  "ai_image_prompts": [
    "prompt 1", "prompt 2", "prompt 3", "prompt 4", "prompt 5",
    "prompt 6", "prompt 7", "prompt 8", "prompt 9", "prompt 10"
  ],
  "instagram_caption": "...",
  "instagram_hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "youtube_title": "...",
  "youtube_tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
  "facebook_caption": "..."
}}
"""
        r3 = model.generate_content(brain_3_prompt, generation_config={"response_mime_type": "application/json"})
        script_json = json.loads(r3.text)
        
        with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as sf:
            json.dump(script_json, sf, ensure_ascii=False, indent=2)
        return script_json

    except Exception as e:
        logger.error(f"Brain failed: {e}. Using Phase 11 fallback.")
        fallback = {
            "thumbnail_text": "यह 1 राज़",
            "script_text": "क्या आपको पता है कि भारत में हर महीने लाखों लोग सिर्फ AI टूल्स से पैसे कमा रहे हैं? बिना ऑफिस, बिना बॉस, सिर्फ अपने फोन से। सोचो, एक साधारण इंसान घर बैठे पचास हजार रुपये कमा रहा है। पर एक गलती है जो सब करते हैं और वो गलती शुरुआत में होती है। जो लोग यह जानते हैं वो आगे बढ़ते हैं। क्या तुम जानना चाहते हो? शुरुआत से देखो।",
            "ai_image_prompts": [
                "Hyper-realistic cinematic photography of a shocked young indian man looking at a glowing smartphone screen in a dark neon lit room, dramatic lighting, 8k resolution",
                "Cinematic documentary shot of an indian person sitting alone in the shadows looking worried, moody cinematic lighting, highly detailed",
                "Hyper-realistic photography of an indian family looking stressed around a kitchen table with unpaid bills, cinematic shadows, 8k",
                "Cinematic shot of a successful young indian freelancer working on a sleek laptop at home, golden hour sunlight streaming through window",
                "Photorealistic image of a glowing green holographic stock market graph growing exponentially, futuristic finance concept, 8k",
                "Hyper-realistic portrait of a successful confident indian entrepreneur smiling in a modern high-rise luxury office overlooking Mumbai, 8k",
                "Cinematic close up of hands typing rapidly on a glowing keyboard with digital glowing currency floating around, hyper-detailed",
                "Photorealistic extreme close up of a smartphone screen showing a massive bank balance notification, held by an indian hand, neon background",
                "Hyper-realistic dynamic shot of a young indian man celebrating success with a victorious fist pump, golden hour sunlight, cinematic depth of field",
                "Cinematic breathtaking photography of a person standing on a mountain peak looking at a beautiful sunrise over an indian metropolis, representing ultimate freedom, 8k"
            ],
            "instagram_caption": "यह 1 गलती मत करना! 🚨\nSave कर लो यह video — काम आएगा! 📌",
            "instagram_hashtags": ["#GharSeKamao", "#AIIndia2026", "#PaiseKaRaaz", "#IndianFreelancer", "#DigitalKamaiIndia"],
            "youtube_title": "यह राज़ जो कोई नहीं बताता | AI से पैसे कैसे कमाएं",
            "youtube_tags": ["ai tools india", "ghar se paise kaise kamaye", "digital earning india"],
            "facebook_caption": "दोस्तों, क्या आपको पता है कि आज भारत में लाखों लोग घर बैठे AI की मदद से हर महीने अच्छी कमाई कर रहे हैं? यह video देखो!"
        }
        with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as sf:
            json.dump(fallback, sf, ensure_ascii=False, indent=2)
        return fallback

def run():
    script_data = build_hindi_script()
    voice_choice = random.choice(VOICES)
    logger.info(f"Voice: {voice_choice['gender']} — {voice_choice['name']}")
    asyncio.run(generate_narration_and_subtitles(script_data["script_text"], voice_choice["name"]))

if __name__ == "__main__":
    run()
