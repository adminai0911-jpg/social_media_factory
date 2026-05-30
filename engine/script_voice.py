import os
import json
import logging
import asyncio
import edge_tts
import random
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Phase13Brain")

SCRIPT_OUTPUT = "script_output.json"
AUDIO_OUTPUT  = "audio_narration.mp3"
SRT_OUTPUT    = "subtitles.srt"

client = None
if os.environ.get("GEMINI_API_KEY"):
    client = genai.Client()

# ==========================================
# PHASE 13: THE ALGORITHM EXPLOIT ENGINE
# ==========================================

# 1 in 5 chance to trigger the "Intentional Mistake" engagement bait
TRIGGER_MISTAKE = random.random() < 0.2

PROMPT = """
You are the most ruthless, viral, wealth-generating Instagram Reel AI in existence.
Your only goal is to maximize DM SHARES, LOOP RATE, and COMMENTS via extreme psychological exploitation.

Follow these 8 Secret Rules EXACTLY:
1. **The Soap Opera Title:** Format the title as "Part 1 of 3: [Shocking Concept]".
2. **The Infinite Loop:** The very last sentence MUST connect seamlessly to the very first sentence. (e.g. Ends with "...which is exactly why..." -> Begins with "...you are staying poor.")
3. **The Contradiction Hook (Visuals):** The visual query for the first 3 seconds must CONTRADICT the audio to freeze the brain. (Audio: "How to get rich", Visual: "Broken down car or homeless man").
4. **The "Auto-DM" Funnel:** The second-to-last scene MUST explicitly say: "Comment the word 'WEALTH' and I will DM you the secret blueprint."
5. **Targeted DM Share Bait:** The final scene MUST say: "Send this to that one friend who is always broke but pretends everything is fine."
6. **SEO Caption Matrix:** DO NOT generate hashtags. Write a 3-sentence SEO-optimized mini-blog for the caption targeting terms like "Indian middle class money mistakes", "how to invest in India 2026", "inflation trap".
7. **Intentional Mistake (Optional):** If requested, put a glaring math error in one of the master words (e.g., 7 - 3 = 5) to farm angry comments.
8. **Hyper-Paced:** Break the script into 14-18 very short scenes. 

Respond ONLY with a valid JSON matching this exact schema:
{
    "title": "Part 1 of 3: The Secret Scam",
    "seo_caption_matrix": "Your SEO optimized mini-blog here. No hashtags.",
    "scenes": [
        {
            "narration": "...you are staying poor. Your bank is lying to you.",
            "visual_query": "broken old bicycle",
            "master_word": "THEY LIE!"
        }
    ]
}
"""

def generate_script():
    logger.info("======================================================================")
    logger.info("PHASE 13: OMNISCIENT ALGORITHM HACKER (Auto-DM & Infinite Loops)")
    logger.info("======================================================================")
    
    if client:
        import time
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info("Brain 3: Exploiting Instagram Algorithm...")
                if TRIGGER_MISTAKE:
                    logger.info("[!] Intentional Mistake Engaged for Comment Baiting.")
                    prompt_append = " REQUIRED: Make an obvious math error in scene 5's master word to bait comments."
                else:
                    prompt_append = ""
                    
                resp = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=PROMPT + prompt_append,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.9
                    ),
                )
                data = json.loads(resp.text)
                logger.info("Script Generated via Gemini!")
                return data
            except Exception as e:
                err_str = str(e).lower()
                if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
                    logger.warning(f"⚠️ 429 Quota Exceeded (Attempt {attempt+1}/{max_retries}). The Sentinel is pausing for 65 seconds...")
                    time.sleep(65)
                else:
                    logger.error(f"Brain failed: {e}")
                    return _premium_fallback()
        logger.error("Max retries exceeded for Gemini Quota. Falling back.")
        return _premium_fallback()
    else:
        return _premium_fallback()

def _premium_fallback():
    # Built-in Phase 13 Fallback (Contains all algorithmic hacks)
    
    mistake_word = "4% LOSS!"
    if TRIGGER_MISTAKE:
        mistake_word = "5% LOSS!" # Math is wrong, will trigger thousands of angry comments
        
    return {
        "title": "Part 1 of 3: The Matrix Trap",
        "seo_caption_matrix": "If you are keeping your money in a savings account in India in 2026, you are actively losing purchasing power. Financial literacy is the only escape from the middle class trap. Learn how to invest in assets to beat inflation and secure generational wealth.",
        "scenes": [
            {
                "narration": "...you will never be rich.", # Loops perfectly with the end
                "visual_query": "old broken car parked", # Contradiction Hook
                "master_word": "NEVER RICH!"
            },
            {
                "narration": "Wake up. The system is designed to keep you poor.",
                "visual_query": "indian man smiling looking foolish",
                "master_word": "WAKE UP!"
            },
            {
                "narration": "You work hard, you sweat, and you save your rupees.",
                "visual_query": "indian man working hard laptop sweat",
                "master_word": "HARD WORK"
            },
            {
                "narration": "But your bank pays you 3% interest.",
                "visual_query": "bank interest rates chart board",
                "master_word": "3% INTEREST"
            },
            {
                "narration": "While real inflation is burning at 7%.",
                "visual_query": "grocery store prices inflation india",
                "master_word": "7% INFLATION"
            },
            {
                "narration": "You are guaranteed to lose money every single year.",
                "visual_query": "indian rupees cash burning fire",
                "master_word": mistake_word # Intentional Mistake Engagement Bait
            },
            {
                "narration": "Your wallet is bleeding invisible cash.",
                "visual_query": "wallet empty indian money",
                "master_word": "VALUE DROPS"
            },
            {
                "narration": "The top 1% don't save money. They buy assets.",
                "visual_query": "rich indian businessman luxury car",
                "master_word": "TOP 1%"
            },
            {
                "narration": "Stocks, real estate, businesses.",
                "visual_query": "stock market graph going up fast",
                "master_word": "BUY ASSETS"
            },
            {
                "narration": "Stop working for money. Make money work for you.",
                "visual_query": "corporate business men shaking hands",
                "master_word": "THE MATRIX"
            },
            {
                "narration": "Comment the word 'WEALTH' and I will DM you my exact blueprint.",
                "visual_query": "smartphone bank app screen checking balance",
                "master_word": "COMMENT WEALTH"
            },
            {
                "narration": "And send this to that one friend who is always broke.", # Targeted Share Bait
                "visual_query": "two friends looking at phone shocked",
                "master_word": "SEND TO FRIEND"
            },
            {
                "narration": "Watch Part 2 on my profile to find out why...", # Soap Opera sequence
                "visual_query": "man pointing to screen",
                "master_word": "GO TO PROFILE"
            }
        ]
    }

async def generate_narration_and_subtitles(text, voice):
    # +50% RATE FOR EXTREME PACING
    logger.info(f"Generating TTS | Voice: {voice} | Rate: +50%")
    communicate = edge_tts.Communicate(text, voice, rate="+50%")
    submaker    = edge_tts.SubMaker()
    with open(AUDIO_OUTPUT, "wb") as af:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                af.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
    with open(SRT_OUTPUT, "w", encoding="utf-8") as sf:
        sf.write(submaker.get_srt())
    logger.info(f"✓ Audio & Subs complete (Hyper Paced)")

def run():
    script_data = generate_script()
    with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=4, ensure_ascii=False)
        
    full_text = " ".join([s["narration"] for s in script_data["scenes"]])
    logger.info(f"Script compiled: {len(script_data['scenes'])} scenes.")
    asyncio.run(generate_narration_and_subtitles(full_text, "hi-IN-MadhurNeural"))

if __name__ == "__main__":
    run()
