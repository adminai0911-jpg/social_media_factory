#!/usr/bin/env python3
"""
THE ULTIMATE Script & Voice Engine — Phase 8

Brain 2: Generates 10 hook variations, scores each on Scroll-Stop Power (1-10), picks the highest.
Brain 3: Writes a 4-SCENE synchronized script (42-50s), generates 10 SCENE-SYNCHRONIZED Pexels
         keywords (each keyword maps exactly to what is being said at that moment),
         anti-ban captions, YouTube title/tags, and Facebook-optimized caption.
TTS:     Alternates randomly between female (SwaraNeural) and male (MadhurNeural) voice.
         20% chance of Follow-Gate monetization promo mode.
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

# Two premium voices — random selection prevents "robot account" pattern detection
VOICES = [
    {"name": "hi-IN-SwaraNeural",  "gender": "Female"},
    {"name": "hi-IN-MadhurNeural", "gender": "Male"},
]


# ──────────────────────────────────────────────────────────
# TTS ENGINE
# ──────────────────────────────────────────────────────────

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


# ──────────────────────────────────────────────────────────
# BRAIN 2 + BRAIN 3
# ──────────────────────────────────────────────────────────

def build_hindi_script():
    logger.info("Initializing Brains 2 & 3...")

    # Load trend file
    if not os.path.exists(TREND_FILE):
        logger.warning("No trend file found. Using fallback trend.")
        fallback = {
            "topic": "AI Tools se Ghar Baithe Paise Kamao",
            "virality_score": 9,
            "emotional_trigger": "Greed",
            "summary": "How ordinary Indians are earning 50,000 rupees per month using free AI tools from home without any boss or office.",
            "news_snippets": ["यह सच जानकर आप हैरान हो जाएंगे!", "क्या आप भी यह जानते हैं?"],
            "niche": "Wealth Building",
            "region": "IN"
        }
        with open(TREND_FILE, "w", encoding="utf-8") as f:
            json.dump(fallback, f, ensure_ascii=False, indent=2)

    with open(TREND_FILE, "r", encoding="utf-8") as f:
        trend_data = json.load(f)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY environment variable.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    try:
        # ════════════════════════════════════════════════
        # BRAIN 2 — Hook Optimizer (10 hooks, scored)
        # ════════════════════════════════════════════════
        logger.info("Executing Brain 2: Hook Optimizer...")

        brain_2_prompt = f"""
You are Brain 2 (The Hook Optimizer) for viral Indian short-form content.

Topic: {trend_data['topic']}
Context: {trend_data['summary']}
Emotional Trigger: {trend_data.get('emotional_trigger', 'Curiosity')}

Generate exactly 10 DEVASTATING scroll-stopping hooks in Hindi (Devanagari only).
Rules:
- Each hook must stop someone from scrolling within 0.5 seconds.
- Hooks must be 3 to 8 words maximum. Just a punch, not a sentence.
- Exploit one trigger per hook: Fear, Greed, Ego, Curiosity, Shock, or Belonging.
- Score each from 1 to 10 on Scroll-Stop Power.

Return ONLY this JSON:
{{
  "hooks": [
    {{"trigger": "Fear", "hook_text": "Hindi hook here...", "score": 9}},
    {{"trigger": "Greed", "hook_text": "Hindi hook here...", "score": 8}}
  ]
}}
"""
        r2 = model.generate_content(
            brain_2_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        hooks_data = json.loads(r2.text).get("hooks", [])

        if not hooks_data:
            raise ValueError("Brain 2 returned zero hooks.")

        # Pick the highest-scored hook
        hooks_sorted = sorted(hooks_data, key=lambda x: x.get("score", 0), reverse=True)
        winning_hook = hooks_sorted[0]["hook_text"]
        logger.info(f"Brain 2 Winner (score {hooks_sorted[0].get('score')}/10): {winning_hook}")

        # ════════════════════════════════════════════════
        # BRAIN 3 — Master Scriptwriter (scene-synced)
        # ════════════════════════════════════════════════
        logger.info("Executing Brain 3: Master Scriptwriter...")

        # 20% monetization promo, 80% pure value content
        is_promo = random.random() < 0.20
        promo_instruction = ""
        if is_promo:
            logger.info("Brain 3: PROMO MODE — Follow-Gate script!")
            promo_instruction = """
MONETIZATION MODE (Follow-Gate):
- Pitch a secret AI tool or method that earns money from home.
- NEVER say "link in bio" — Instagram AI flags and suppresses this phrase.
- End Scene 4 with (in natural Hindi): "Follow karo abhi, bio mein link hai, kal gayab ho sakta hai!"
- In instagram_caption write: "Bio mein link hai! Kal delete ho sakta hai. Jaldi dekho 🔥 Follow karo!"
"""

        brain_3_prompt = f"""
You are Brain 3 (The Master Viral Scriptwriter) for premium Indian short-form video content.

Theme: {trend_data['topic']}
Niche: {trend_data.get('niche', 'General')}
Context: {trend_data['summary']}
Emotional Core: {trend_data.get('emotional_trigger', 'Curiosity')}
Opening Hook — use this WORD FOR WORD as the very first sentence: {winning_hook}
{promo_instruction}

SCRIPT STRUCTURE (4 mandatory scenes):
SCENE 1 (0-4s)   — Hook: Use the opening hook exactly. Shock. Freeze the scroll.
SCENE 2 (4-18s)  — Tension: Introduce the problem, pain point, or shocking fact. Create desire.
SCENE 3 (18-40s) — Value: Deliver the secret, twist, or insight. Build deep trust.
SCENE 4 (40-48s) — Loop End: Last line connects back to the hook, forcing a re-watch.

ABSOLUTE RULES:
1. script_text: Pure Devanagari Hindi only. ZERO English letters, ZERO roman numerals, ZERO symbols.
   One continuous flowing spoken narrative. No bullet points. No line breaks inside the text.
   Target 85-100 Hindi words (42-50 seconds when spoken).

2. pexels_keywords: EXACTLY 10 English search queries.
   CRITICAL: Each keyword MUST describe what should appear VISUALLY ON SCREEN at that exact 5-second moment of the script.
   Map them scene by scene: keywords 1-2 for Scene 1, keywords 3-5 for Scene 2, keywords 6-9 for Scene 3, keyword 10 for Scene 4.
   Format: "[specific visual description] vertical cinematic portrait"
   Example: "young indian man shocked looking at phone screen vertical cinematic"

3. instagram_caption: Feel like a REAL human wrote it. Emotionally engaging. Vary length every time.
   CTA must rotate between: "Tag karo ✊", "Save kar lo 📌", "Kaun dekhna chahega yeh? 👇"
   NEVER use: #viral #trending #reels #instagram (these are shadow-banned triggers).

4. instagram_hashtags: EXACTLY 5 unique, NICHE-SPECIFIC hashtags. Never generic ones.

5. youtube_title: Hindi curiosity-gap title. Under 65 characters. Makes someone click immediately.

6. youtube_tags: 5 specific Hindi/English topic tags (not generic words).

7. facebook_caption: Slightly longer than Instagram. More storytelling, less emoji. Warm, trustworthy tone.

Return ONLY valid JSON in this exact schema (no extra text outside the JSON):
{{
  "thumbnail_text": "2-4 word clickbait Hindi phrase",
  "script_text": "Full 85-100 word Devanagari Hindi spoken script...",
  "pexels_keywords": [
    "scene 1 visual — vertical cinematic portrait",
    "scene 1 visual — vertical cinematic portrait",
    "scene 2 visual — vertical cinematic portrait",
    "scene 2 visual — vertical cinematic portrait",
    "scene 2 visual — vertical cinematic portrait",
    "scene 3 visual — vertical cinematic portrait",
    "scene 3 visual — vertical cinematic portrait",
    "scene 3 visual — vertical cinematic portrait",
    "scene 3 visual — vertical cinematic portrait",
    "scene 4 visual — vertical cinematic portrait"
  ],
  "instagram_caption": "Human-feel Hindi caption with emoji and CTA...",
  "instagram_hashtags": ["#NicheTag1", "#NicheTag2", "#NicheTag3", "#NicheTag4", "#NicheTag5"],
  "youtube_title": "Curiosity-gap Hindi title under 65 chars...",
  "youtube_tags": ["specific tag 1", "specific tag 2", "specific tag 3", "specific tag 4", "specific tag 5"],
  "facebook_caption": "Slightly longer, storytelling Hindi caption for Facebook..."
}}
"""
        r3 = model.generate_content(
            brain_3_prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        script_json = json.loads(r3.text)
        logger.info(f"Brain 3 complete. Thumbnail: '{script_json.get('thumbnail_text', 'N/A')}'")

        with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as sf:
            json.dump(script_json, sf, ensure_ascii=False, indent=2)

        return script_json

    except Exception as e:
        logger.error(f"Brain execution failed: {e}. Using high-quality fallback script.")
        fallback = {
            "thumbnail_text": "यह 1 राज़ जान लो",
            "script_text": "क्या आपको पता है कि भारत में हर महीने लाखों लोग सिर्फ AI टूल्स से पैसे कमा रहे हैं? बिना ऑफिस, बिना बॉस, सिर्फ अपने फोन से। सोचो, एक साधारण इंसान घर बैठे पचास हजार रुपये कमा रहा है। पर एक गलती है जो सब करते हैं और वो गलती शुरुआत में होती है। जो लोग यह जानते हैं वो आगे बढ़ते हैं। क्या तुम जानना चाहते हो? शुरुआत से देखो।",
            "pexels_keywords": [
                "shocked young indian man looking at phone vertical cinematic",
                "person sitting alone at night thinking vertical cinematic",
                "indian family struggling financially stressed vertical cinematic",
                "freelancer working on laptop at home india vertical cinematic",
                "money growing graph on computer screen vertical cinematic",
                "successful indian entrepreneur smiling office vertical cinematic",
                "person typing fast on laptop earning money vertical cinematic",
                "smartphone showing bank notification wealth vertical cinematic",
                "young indian celebrating success fist pump vertical cinematic",
                "person looking at horizon sunrise freedom india vertical cinematic"
            ],
            "instagram_caption": "यह 1 गलती मत करना दोस्त! 🚨\n\nजो लोग यह जानते हैं वो आगे हैं, जो नहीं जानते वो पीछे। Save कर लो यह video — काम आएगा! 📌\n\nअपने उस दोस्त को Tag करो जिसे यह जानना चाहिए 👇",
            "instagram_hashtags": ["#GharSeKamao", "#AIIndia2026", "#PaiseKaRaaz", "#IndianFreelancer", "#DigitalKamaiIndia"],
            "youtube_title": "यह राज़ जो कोई नहीं बताता | AI से पैसे कैसे कमाएं",
            "youtube_tags": ["ai tools india", "ghar se paise kaise kamaye", "passive income hindi", "digital earning india", "online business india"],
            "facebook_caption": "दोस्तों, क्या आपको पता है कि आज भारत में लाखों लोग घर बैठे AI की मदद से हर महीने अच्छी कमाई कर रहे हैं? लेकिन एक गलती है जो सब शुरुआत में करते हैं। यह video देखो और अपने दोस्तों को Share करो। 🙏"
        }
        with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as sf:
            json.dump(fallback, sf, ensure_ascii=False, indent=2)
        return fallback


# ──────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────

def run():
    script_data  = build_hindi_script()
    voice_choice = random.choice(VOICES)
    logger.info(f"Voice: {voice_choice['gender']} — {voice_choice['name']}")
    asyncio.run(generate_narration_and_subtitles(script_data["script_text"], voice_choice["name"]))


if __name__ == "__main__":
    run()
