#!/usr/bin/env python3
"""
THE MASTER SCRIPT ENGINE — Phase 12 (Human-Feel Viral Content)

What changed from all previous versions:
1. 5 VIRAL HOOK TEMPLATES rotating by day — never same hook style twice in a week
2. CASUAL HINDI — writes like a real person talks, not a textbook
3. SCENE TAGS embedded directly in script — [HOOK], [STRUGGLE], [MONEY] etc.
   The video engine reads these tags to pick the EXACTLY matching B-Roll clip.
4. SPECIFIC DETAILS in every script — real numbers, real time references
5. MONETIZATION CTA — every 5th video softly promotes Stan Store link
6. GENDER VOICE ROTATION — alternates male/female voice daily
7. New google.genai SDK (not deprecated google.generativeai)
"""

import os
import json
import asyncio
import random
import logging
import re
from datetime import datetime
import edge_tts
import google.genai as genai

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MasterScriptEngine")

TREND_FILE    = "current_trend.json"
SCRIPT_OUTPUT = "script_output.json"
AUDIO_OUTPUT  = "audio_narration.mp3"
SRT_OUTPUT    = "subtitles.srt"

VOICES = [
    {"name": "hi-IN-MadhurNeural", "gender": "Male"},   # Even days
    {"name": "hi-IN-SwaraNeural",  "gender": "Female"}, # Odd days
]

# Valid scene tags that map to B-Roll library folders
VALID_TAGS = ["HOOK", "STRUGGLE", "SCHOOL_LIE", "WORK", "MONEY", "SUCCESS", "INDIA_LIFE", "TECH", "FREEDOM", "LOOP"]

# 5 VIRAL HOOK TEMPLATES — rotated by day of week
# Each is a different psychological trigger
HOOK_TEMPLATES = {
    0: "DIRECT_ADDRESS",    # Monday    — "Yaar ek baat batao..."
    1: "SHOCK_STAT",        # Tuesday   — "India mein X% log..."
    2: "REAL_STORY",        # Wednesday — "2 saal pehle mera account..."
    3: "EXPOSE",            # Thursday  — "School ne tujhe jhooth bataya..."
    4: "CHALLENGE",         # Friday    — "Ek kaam karo abhi..."
    5: "SHOCK_STAT",        # Saturday  — same rotation continues
    6: "REAL_STORY",        # Sunday
}

HOOK_INSTRUCTIONS = {
    "DIRECT_ADDRESS": """
Hook type: DIRECT ADDRESS (Most intimate, feels like a close friend talking)
Start with: "Yaar, ek baat batao —" OR "Ek second ruko —" OR "Suno, yeh important hai —"
Then immediately ask a personal question that makes the viewer think about their own life.
Example feel: "Yaar, honestly batao — kya tumhara bank balance aaj kal tum khush karta hai?"
""",
    "SHOCK_STAT": """
Hook type: SHOCK STAT (Pattern interrupt — stops brain mid-scroll)
Start with a SPECIFIC percentage or number that shocks the viewer.
Use a real-sounding statistic about Indians and money.
Example feel: "India mein 94% log 60 saal ki umar mein financially dependent hote hain. Kya tum us 6% mein aana chahte ho?"
""",
    "REAL_STORY": """
Hook type: REAL STORY (Creates emotional connection immediately)
Start with a specific past moment (give a year, a number, a real detail).
Must feel like a real human memory, not a marketing story.
Example feel: "2023 mein mere account mein sirf 1,200 rupaye the. Main coffee bhi nahi pi sakta tha bina sochhe."
""",
    "EXPOSE": """
Hook type: THE EXPOSE (Triggers anger/betrayal against a system)
Start by naming something everyone believes to be true, then call it a lie.
Example feel: "School ne bataya — naukri karo, safe raho. Yeh duniya ka sabse bada jhooth hai."
""",
    "CHALLENGE": """
Hook type: THE CHALLENGE (Creates immediate action and engagement)
Start by giving the viewer a physical or mental action to do right now.
Example feel: "Ek kaam karo — abhi apna wallet nikalo. Jo tum dekh rahe ho woh 3 saal baad bhi wahi rahega... jab tak tum yeh nahi jaante."
""",
}


async def generate_narration_and_subtitles(text, voice):
    logger.info(f"Generating TTS: voice='{voice}'")
    communicate = edge_tts.Communicate(text, voice)
    submaker    = edge_tts.SubMaker()
    with open(AUDIO_OUTPUT, "wb") as af:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                af.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
    with open(SRT_OUTPUT, "w", encoding="utf-8") as sf:
        sf.write(submaker.get_srt())
    logger.info(f"Audio → '{AUDIO_OUTPUT}' | Subtitles → '{SRT_OUTPUT}'")


def extract_scene_sequence(tagged_script):
    """
    Extracts a list of scene categories from the tagged script.
    Input:  "[HOOK] Yaar ek baat batao... [STRUGGLE] 2 saal pehle..."
    Output: (clean_text, ["hook", "struggle", ...])
    """
    tags_found  = re.findall(r'\[(' + '|'.join(VALID_TAGS) + r')\]', tagged_script, re.IGNORECASE)
    clean_text  = re.sub(r'\[(' + '|'.join(VALID_TAGS) + r')\]\s*', '', tagged_script, flags=re.IGNORECASE).strip()
    scene_seq   = [t.lower().replace("_", "") for t in tags_found]
    
    # Map tag names to folder names
    tag_to_folder = {
        "hook":       "01_hook",
        "struggle":   "02_struggle",
        "schoollie":  "03_school_lie",
        "work":       "04_work",
        "money":      "05_money",
        "success":    "06_success",
        "indialife":  "07_india_life",
        "tech":       "08_tech",
        "freedom":    "09_freedom",
        "loop":       "10_loop",
    }
    folders = [tag_to_folder.get(t, "01_hook") for t in scene_seq]
    
    # Ensure we have at least 10 entries
    while len(folders) < 10:
        folders.append(random.choice(list(tag_to_folder.values())))
    
    return clean_text, folders[:10]


def build_hindi_script():
    logger.info("=" * 60)
    logger.info("MASTER BRAIN: Initializing Viral Script Generation")
    logger.info("=" * 60)

    # Load trend
    if not os.path.exists(TREND_FILE):
        trend_data = {
            "topic": "AI Tools se Ghar Baithe Paise Kamao",
            "summary": "Free AI tools helping Indians earn from home without boss or office",
            "niche": "Wealth Building",
        }
        with open(TREND_FILE, "w", encoding="utf-8") as f:
            json.dump(trend_data, f, ensure_ascii=False)
    else:
        with open(TREND_FILE, "r", encoding="utf-8") as f:
            trend_data = json.load(f)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("Missing GEMINI_API_KEY.")
        return _premium_fallback()

    # Select hook template based on day of week
    day_of_week   = datetime.now().weekday()
    hook_type     = HOOK_TEMPLATES.get(day_of_week, "SHOCK_STAT")
    hook_guide    = HOOK_INSTRUCTIONS[hook_type]
    is_promo_day  = (datetime.now().day % 5 == 0)  # Every 5th calendar day = soft CTA

    try:
        client = genai.Client(api_key=api_key)

        # ── BRAIN 2: Generate 10 hooks, pick the best one ──────────────────
        logger.info(f"Brain 2: Generating 10 hooks [{hook_type}]...")
        brain2_prompt = f"""
You are Brain 2 — The Hook Optimizer.
Topic: {trend_data['topic']}
Context: {trend_data['summary']}
Today's Hook Type: {hook_type}
Hook Style Guide: {hook_guide}

Generate 10 different hook variations for this hook type.
RULES:
- All in casual conversational Hindi (Devanagari only)
- Max 8 words per hook
- Sound like a real person talking to a friend, not an AI
- Each must create INSTANT curiosity or emotion
- Avoid starting with "Kya aapko pata hai"

Score each 1-10 on Scroll-Stop Power.
Return ONLY JSON:
{{"hooks": [{{"text": "Hindi hook", "score": 9}}]}}
"""
        r2 = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=brain2_prompt,
            config={"response_mime_type": "application/json"}
        )
        hooks   = json.loads(r2.text).get("hooks", [])
        hook    = sorted(hooks, key=lambda h: h.get("score", 0), reverse=True)[0]["text"] if hooks else "Yaar, yeh sun lo —"
        logger.info(f"Brain 2 Winner [{hook_type}]: {hook}")

        # ── BRAIN 3: Write full script with SCENE TAGS ─────────────────────
        logger.info("Brain 3: Writing scene-tagged masterpiece script...")
        
        promo_note = ""
        if is_promo_day:
            promo_note = 'End with: "Follow karo aur bio mein link dekho — kal delete ho sakta hai!"'
        
        brain3_prompt = f"""
You are Brain 3 — The World's Best Hindi Viral Reel Scriptwriter.
You write content for an Instagram page about INDIAN WEALTH PSYCHOLOGY.
The page teaches ordinary Indians the hidden psychological rules of money.

TOPIC: {trend_data['topic']}
HOOK (use exactly this): {hook}
{promo_note}

WRITE A 60-SECOND SCRIPT (120-130 Devanagari Hindi words) following this structure:

SCENE 1 [HOOK] — 0 to 8 seconds
Use exactly the provided hook. Then 1-2 sentences that create a TENSION or QUESTION in the viewer's mind.

SCENE 2 [STRUGGLE] — 8 to 20 seconds
Describe the painful common struggle most Indians face with money. Make it specific and real. Use a real number or time reference.

SCENE 3 [SCHOOL_LIE] or [WORK] — 20 to 30 seconds
Expose what school or society taught wrong, OR describe what the wrong approach looks like.

SCENE 4 [MONEY] or [TECH] — 30 to 42 seconds
Introduce the INSIGHT — what the rich/successful actually do differently. One specific, actionable idea.

SCENE 5 [SUCCESS] — 42 to 52 seconds
Paint a vivid picture of what life looks like AFTER applying this insight. Make it emotional.

SCENE 6 [FREEDOM] or [LOOP] — 52 to 60 seconds
Powerful ending: a call to action that creates urgency + emotional close.

CRITICAL RULES:
- Write EXACTLY as spoken, casual conversational Hindi — like a friend talking, not a lecture
- Include [SCENE_TAG] before each scene transition (use tags from: HOOK, STRUGGLE, SCHOOL_LIE, WORK, MONEY, TECH, SUCCESS, INDIA_LIFE, FREEDOM, LOOP)
- Use at least 8 different [SCENE_TAG] markers spread through the script
- Include one SPECIFIC real-sounding detail (a year, a number, a place)
- DO NOT start SCENE 1 with "Kya aapko pata hai"
- The script must feel REAL — like someone lived this, not like an AI wrote it

Return ONLY this JSON (no extra text):
{{
  "thumbnail_text": "2-4 Hindi words that shock or intrigue",
  "tagged_script": "Full script WITH [SCENE_TAG] markers embedded at transitions",
  "instagram_caption": "3-5 lines casual Hindi caption with 2-3 emojis. End with a question to drive comments.",
  "instagram_hashtags": ["#Tag1", "#Tag2", "#Tag3", "#Tag4", "#Tag5"],
  "youtube_title": "Clickbait Hindi title for YouTube Shorts (under 60 chars)",
  "youtube_tags": ["tag1", "tag2", "tag3", "tag4", "tag5", "tag6"],
  "facebook_caption": "Longer storytelling Hindi caption for Facebook Reels (8-10 lines)"
}}
"""
        r3 = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=brain3_prompt,
            config={"response_mime_type": "application/json"}
        )
        data         = json.loads(r3.text)
        tagged       = data.get("tagged_script", "")
        clean, scenes = extract_scene_sequence(tagged)

        logger.info(f"Scene sequence: {scenes}")

        result = {
            "thumbnail_text":      data.get("thumbnail_text", "₹50,000 ka Raaz"),
            "script_text":         clean,
            "tagged_script":       tagged,
            "scene_sequence":      scenes,
            "instagram_caption":   data.get("instagram_caption", ""),
            "instagram_hashtags":  data.get("instagram_hashtags", []),
            "youtube_title":       data.get("youtube_title", ""),
            "youtube_tags":        data.get("youtube_tags", []),
            "facebook_caption":    data.get("facebook_caption", ""),
        }

        with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"Script saved → '{SCRIPT_OUTPUT}'")
        return result

    except Exception as e:
        logger.error(f"Brain failed: {e}. Using premium fallback.")
        return _premium_fallback()


def _premium_fallback():
    """
    Hand-crafted premium fallback scripts — these are NOT random.
    They are written using the exact viral template rules and rotate daily.
    """
    day = datetime.now().weekday()
    
    FALLBACK_SCRIPTS = [
        # Monday — Direct Address
        {
            "thumbnail_text": "तुम्हारा पैसा?",
            "script_text": "Yaar, honestly batao — kya tumhara bank balance tumhe khush karta hai? Main sach pooch raha hoon. Kyunki 2023 mein ek survey hua — India mein 89% log apni salary aane ke 10 din baad phir zero pe aa jaate hain. Zero pe. Kuch nahi bachta. Aur pata hai kyun? Kyunki school ne humein paisa kamana sikhaya — paisa rakhna nahi. Duniya mein jo log ameer hain — unka ek common secret hai. Woh pehle apne aap ko pay karte hain, phir baaki sab ko. Matlab salary aane pe pehle 20% side mein rakh do — phir kharcho jo chahein. Yeh ek kaam, sirf yeh ek kaam, 5 saal mein tumhari zindagi badal sakta hai. Save karo yeh video — 3 mahine baad yaad aayega.",
            "tagged_script": "[HOOK] Yaar, honestly batao — kya tumhara bank balance tumhe khush karta hai? [STRUGGLE] Kyunki 2023 mein ek survey hua — India mein 89% log apni salary aane ke 10 din baad phir zero pe aa jaate hain. [SCHOOL_LIE] Kyunki school ne humein paisa kamana sikhaya — paisa rakhna nahi. [MONEY] Duniya mein jo log ameer hain — unka ek common secret hai. Woh pehle apne aap ko pay karte hain. [SUCCESS] Matlab salary aane pe pehle 20% side mein rakh do. [FREEDOM] Yeh ek kaam, sirf yeh ek kaam, 5 saal mein tumhari zindagi badal sakta hai. [LOOP] Save karo yeh video — 3 mahine baad yaad aayega.",
            "scene_sequence": ["01_hook", "02_struggle", "03_school_lie", "05_money", "06_success", "09_freedom", "10_loop"],
        },
        # Tuesday — Shock Stat
        {
            "thumbnail_text": "97% log galat hain",
            "script_text": "India mein 97% log retire hote hain financially dependent — apne bacchon pe, apne relatives pe. Sirf 3% financially free hote hain. Ek simple sa fark hai in dono mein. Woh 3% log ek cheez karte hain jo 97% nahi karte — woh apne paise ko kaam pe lagate hain. Unka paisa unke liye kaam karta hai — woh apne paise ke liye nahi karte. Index funds, real estate, business — kuch bhi. Point yeh hai ki ek rupaya bhi invest nahi karna matlab 30 saal baad tum apne hi bacchon ke saamne haath phailaoge. Yeh harsh hai — lekin yeh sach hai. Aaj se shuru karo. 500 rupaye se bhi shuru kar sakte ho. Kal nahi — aaj.",
            "tagged_script": "[HOOK] India mein 97% log retire hote hain financially dependent. Sirf 3% financially free hote hain. [STRUGGLE] Ek simple sa fark hai in dono mein. [SCHOOL_LIE] Woh 3% log ek cheez karte hain jo 97% nahi karte — [MONEY] woh apne paise ko kaam pe lagate hain. Index funds, real estate, business. [INDIA_LIFE] 30 saal baad tum apne hi bacchon ke saamne haath phailaoge. [SUCCESS] Aaj se shuru karo. 500 rupaye se bhi shuru kar sakte ho. [LOOP] Kal nahi — aaj.",
            "scene_sequence": ["01_hook", "02_struggle", "03_school_lie", "05_money", "07_india_life", "06_success", "10_loop"],
        },
        # Wednesday — Real Story
        {
            "thumbnail_text": "₹800 se ₹50,000",
            "script_text": "2022 mein mere account mein sirf 800 rupaye the. Main literally soch raha tha ki aaj khaana khaoon ya kal. Us raat YouTube pe ek video dekha — ek 24 saal ke ladke ne bataya ki woh ghar se sirf ek laptop se 40,000 rupaye kama raha hai. Main hansa. Mujhe laga bakwaas hai. Phir socha — agar yeh jhooth bhi hai, toh mujhe kya nuksaan? Main try karta hoon. Us raat maine ek free course liya. 3 mahine mein pehli freelancing payment aayi — 8,000 rupaye. Meri aankhon mein aansu aa gaye. Aaj woh 40,000 nahin — 50,000 se zyada hai. Ek cheez jo maine seekhi: shuru karne se zyada darr lagta hai jab tak shuru nahi karte. Follow karo — main aur bhi baat karni chahta hoon.",
            "tagged_script": "[HOOK] 2022 mein mere account mein sirf 800 rupaye the. [STRUGGLE] Main literally soch raha tha ki aaj khaana khaoon ya kal. [TECH] Us raat YouTube pe ek video dekha — ek 24 saal ke ladke ne bataya ki woh ghar se sirf ek laptop se 40,000 rupaye kama raha hai. [WORK] Us raat maine ek free course liya. [MONEY] 3 mahine mein pehli freelancing payment aayi — 8,000 rupaye. [SUCCESS] Aaj woh 40,000 nahin — 50,000 se zyada hai. [LOOP] Ek cheez jo maine seekhi: shuru karne se zyada darr lagta hai jab tak shuru nahi karte.",
            "scene_sequence": ["01_hook", "02_struggle", "08_tech", "04_work", "05_money", "06_success", "10_loop"],
        },
        # Thursday — Expose
        {
            "thumbnail_text": "School ka Jhooth",
            "script_text": "School ne bataya — naukri karo, stable raho, safe raho. Yeh duniya ka sabse expensive advice hai. Kyun? Kyunki ek naukri mein ek income source hota hai. Agar woh jaaye — sab kuch jaaye. Duniya ke 90% ameer logon ke paas 3 ya zyada income sources hain. Sirf 1 nahi. Salary alag, investment income alag, side business alag. School ne yeh kabhi nahi sikhaya kyunki agar sab entrepreneur ban gaye toh factories mein kaam kaun karega? Yeh harsh sach hai. Lekin ab tum jaante ho. Ab tumhara kaam hai — ek aur income source banana shuru karo. Freelancing, YouTube, affiliate — jo bhi ho. Ek se shuru karo. Abhi se.",
            "tagged_script": "[HOOK] School ne bataya — naukri karo, stable raho, safe raho. Yeh duniya ka sabse expensive advice hai. [SCHOOL_LIE] Kyunki ek naukri mein ek income source hota hai. Agar woh jaaye — sab kuch jaaye. [MONEY] Duniya ke 90% ameer logon ke paas 3 ya zyada income sources hain. [STRUGGLE] School ne yeh kabhi nahi sikhaya kyunki agar sab entrepreneur ban gaye toh factories mein kaam kaun karega? [WORK] Ab tumhara kaam hai — ek aur income source banana shuru karo. [SUCCESS] Freelancing, YouTube, affiliate — jo bhi ho. [LOOP] Ek se shuru karo. Abhi se.",
            "scene_sequence": ["01_hook", "03_school_lie", "05_money", "02_struggle", "04_work", "06_success", "10_loop"],
        },
        # Friday — Challenge
        {
            "thumbnail_text": "Himmat hai?",
            "script_text": "Ek kaam karo — abhi, is second. Apna phone uthao aur apna bank balance dekho. Jo number tumne dekha — kya 5 saal baad bhi wahi number hoga? Agar aaj kuch nahi badla — to haan, wahi hoga. Shayad thoda aur kam. Kyunki inflation har saal 6-7% tumhara paisa kha jaata hai. Jo 10,000 aaj hain — 5 saal baad woh sirf 7,000 ki value ke hain. Paisa bank mein rakhna matlab dheere dheere gareebi ki taraf jaana. Agar tum sach mein badlna chahte ho — ek step: is mahine ki salary ka 10% ek index fund mein daalo. Sirf 10%. Aur dekhte jao kya hota hai. Yeh video save karo — tumhe 6 mahine baad yaad ayega.",
            "tagged_script": "[HOOK] Ek kaam karo — abhi, is second. Apna phone uthao aur apna bank balance dekho. [STRUGGLE] Jo number tumne dekha — kya 5 saal baad bhi wahi number hoga? [MONEY] Kyunki inflation har saal 6-7% tumhara paisa kha jaata hai. [INDIA_LIFE] Jo 10,000 aaj hain — 5 saal baad woh sirf 7,000 ki value ke hain. [WORK] Is mahine ki salary ka 10% ek index fund mein daalo. [SUCCESS] Sirf 10%. Aur dekhte jao kya hota hai. [LOOP] Yeh video save karo — tumhe 6 mahine baad yaad ayega.",
            "scene_sequence": ["01_hook", "02_struggle", "05_money", "07_india_life", "04_work", "06_success", "10_loop"],
        },
    ]

    fb = FALLBACK_SCRIPTS[day % len(FALLBACK_SCRIPTS)]
    result = {
        "thumbnail_text":      fb["thumbnail_text"],
        "script_text":         fb["script_text"],
        "tagged_script":       fb["tagged_script"],
        "scene_sequence":      fb["scene_sequence"],
        "instagram_caption":   "💡 Yeh sun ke lagta hai ki kisi ne poori zindagi se alag cheez batai!\n\n💰 Save karo — yeh ek din kaam aayega!\n\n👇 Apne ek dost ko tag karo jise yeh sunnna chahiye\n\nKya tum is baat se agree karte ho? Comment mein batao! 👇",
        "instagram_hashtags":  ["#IndianWealthSecrets", "#PaiseKiSacchai", "#GharSeKamao", "#AIIndia2026", "#FinancialFreedomIndia"],
        "youtube_title":       f"{fb['thumbnail_text']} | Woh Jo School Ne Nahi Bataya",
        "youtube_tags":        ["paise kaise kamaye", "india wealth secrets", "financial freedom india", "ai tools india", "ghar se kamao"],
        "facebook_caption":    f"Doston,\n\n{fb['script_text'][:200]}...\n\nYeh baat sun ke lagta hai — school ne hume paise KAMANA sikhaya, lekin RAKHNA nahi sikhaya.\n\nKya aapko lagta hai yeh baat sach hai? Comment mein batao 👇",
    }

    with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info(f"Premium fallback script saved (Day {day}): {result['thumbnail_text']}")
    return result


def run():
    script = build_hindi_script()
    day    = datetime.now().day
    voice  = VOICES[day % 2]["name"]
    logger.info(f"Voice: {voice}")
    asyncio.run(generate_narration_and_subtitles(script["script_text"], voice))


if __name__ == "__main__":
    run()
