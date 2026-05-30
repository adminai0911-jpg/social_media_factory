#!/usr/bin/env python3
"""
THE VIRAL PSYCHOLOGY ENGINE — Phase 12.1
"Middle Class India ka Financial Awakening"

The science behind every viral Hindi reel that reached millions:

1. PATTERN INTERRUPT (0-3s)   — Breaks auto-scroll with shock/contrast
2. IDENTITY MIRROR (3-8s)     — "This is about YOU specifically"
3. PAIN AMPLIFICATION (8-20s) — Make the struggle feel real and personal
4. CURIOSITY GAP (20-35s)     — Build towards answer but don't give it yet
5. THE REVEAL (35-50s)        — Drop the insight/value
6. LOOP BAIT (50-60s)         — End with unanswered question = rewatch

Instagram Algorithm Signals this maximizes:
- Watch Time (suspense keeps them till the end)
- Replays (loop bait makes them rewatch)
- Saves (value makes them save)
- Comments (identity question triggers response)
- Shares (relatable pain triggers "tag karo")

Target: Middle Class India (300M+ people)
  - Earn ₹20,000–₹80,000/month
  - Feel STUCK between poverty and real wealth
  - Family pressure, EMI, job insecurity
  - Secretly dream of financial freedom
  - This is the most emotionally charged audience in India
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
logger = logging.getLogger("ViralPsychologyEngine")

TREND_FILE    = "current_trend.json"
SCRIPT_OUTPUT = "script_output.json"
AUDIO_OUTPUT  = "audio_narration.mp3"
SRT_OUTPUT    = "subtitles.srt"

# Alternate male/female voice by day for variety
VOICES = [
    {"name": "hi-IN-MadhurNeural",  "gender": "Male"},
    {"name": "hi-IN-SwaraNeural",   "gender": "Female"},
]

VALID_TAGS   = ["HOOK", "STRUGGLE", "SCHOOL_LIE", "WORK", "MONEY", "SUCCESS",
                "INDIA_LIFE", "TECH", "FREEDOM", "LOOP"]
TAG_TO_FOLDER = {
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

# ─── 7 VIRAL HOOK ARCHETYPES (rotates by day of week) ───────────────────────
# Each activates a different deep psychological trigger

HOOK_TEMPLATES = {
    0: "FORBIDDEN_KNOWLEDGE",  # Monday
    1: "IDENTITY_ATTACK",      # Tuesday
    2: "REAL_STORY_OPEN",      # Wednesday
    3: "SHOCKING_CONTRAST",    # Thursday
    4: "THE_CHALLENGE",        # Friday
    5: "EMOTIONAL_MIRROR",     # Saturday
    6: "CONSPIRACY_EXPOSE",    # Sunday
}

HOOK_PSYCHOLOGY = {
    "FORBIDDEN_KNOWLEDGE": {
        "trigger": "Rich people don't WANT you to know this",
        "hook_examples": [
            "Woh cheez jo ameer log apne bacchon ko sikhate hain — tumhare bacchon ko kabhi nahi sikhate",
            "Ek secret jo India ke top 1% log apne andar hi rakhte hain",
            "Bade log chahte hain tum yeh kabhi mat jaano",
        ],
        "instruction": """
Hook type: FORBIDDEN KNOWLEDGE
Psychological trigger: Exclusivity + Betrayal by the system
The viewer feels they are about to learn something "they weren't supposed to know."
This creates IMMEDIATE attention because humans are hardwired to seek forbidden information.
Start with: A statement that implies rich/powerful people are hiding something from ordinary Indians.
NEVER use "Kya aapko pata hai" — use direct statement as if sharing a secret.
Example: "Ek baat hai jo ameer baap apne bacchon ko sikhata hai — jo school kabhi nahi sikhata..."
"""
    },
    "IDENTITY_ATTACK": {
        "trigger": "You specifically are making this mistake",
        "hook_examples": [
            "Agar tu sach mein middle class mein hai — yeh video tere liye hai",
            "Jo tum abhi kar rahe ho — wahi cheez tumhe ameer hone se rok rahi hai",
            "Tum yeh video dekh rahe ho — iska matlab tum abhi bhi yahi galti kar rahe ho",
        ],
        "instruction": """
Hook type: IDENTITY ATTACK
Psychological trigger: Direct personal accusation that makes viewer self-conscious
The viewer feels PERSONALLY called out — they can't look away because their ego is involved.
Start by directly addressing the viewer's current behavior or identity as a mistake.
Make them feel: "Wait — am I doing this wrong?"
Example: "Jo tum abhi kar rahe ho paison ke saath — wahi cheez hai jo tum kabhi ameer nahi banegi..."
"""
    },
    "REAL_STORY_OPEN": {
        "trigger": "Real human emotional story",
        "hook_examples": [
            "2023 mein meri salary 18,000 thi. EMI 14,000. Bachte the sirf 4,000 rupaye.",
            "Ek baar maine apni wife se jhooth bola ki main office ja raha hoon — lekin gaya tha job dhundne",
            "Mujhe wo raat yaad hai jab mere account mein 237 rupaye the aur salary aane mein 12 din",
        ],
        "instruction": """
Hook type: REAL STORY OPEN
Psychological trigger: Raw emotional authenticity — immediate empathy
Start with a hyper-specific real moment: year, exact rupee amount, specific detail.
The specificity is what makes it FEEL real. Vague stories are ignored. Specific stories stop scrolls.
Example: "December 2022. Mere account mein sirf 847 rupaye the. Wife pregnant thi. Salary aane mein 3 hafte."
This is NOT about being dramatic — it's about being painfully real and specific.
"""
    },
    "SHOCKING_CONTRAST": {
        "trigger": "Reality is opposite of what you believe",
        "hook_examples": [
            "Tumhare ghar mein jo sabse zyada padhne wala hai — woh sabse garib retire hoga",
            "Jo cheez tum savings samajhte ho — woh actually tumhara paise chura rahi hai",
            "India mein hardest working log sab se garib kyun hote hain?",
        ],
        "instruction": """
Hook type: SHOCKING CONTRAST
Psychological trigger: Cognitive dissonance — what you believe vs disturbing reality
Start with a statement that DIRECTLY CONTRADICTS a commonly held Indian belief about money.
The brain cannot ignore information that conflicts with its existing beliefs.
Example: "Tumhare ghar ka sabse mehnat karne wala insaan — woh retire hoga sabse zyada gareebi mein."
Make it feel like a slap of cold water on the face.
"""
    },
    "THE_CHALLENGE": {
        "trigger": "Test your courage/intelligence RIGHT NOW",
        "hook_examples": [
            "Ek kaam karo abhi — apna bank balance dekho. Jo number hai woh 5 saal baad bhi wahi hoga.",
            "Agar tum mujhse agree karte ho — comment mein sirf 'HAAN' likho.",
            "Main ek sawaal poochhunga — agar tumhara jawab 'haan' hai to yeh video tumhari zindagi badal sakti hai.",
        ],
        "instruction": """
Hook type: THE CHALLENGE
Psychological trigger: Ego involvement — viewer must prove themselves
Give the viewer an immediate action or mental challenge in the first 3 seconds.
When someone is given a challenge, their brain CANNOT disengage until they complete it.
Example: "Ek kaam karo — abhi apna phone uthao. Apna bank balance dekho. Jo number hai..."
"""
    },
    "EMOTIONAL_MIRROR": {
        "trigger": "Someone finally understands your exact pain",
        "hook_examples": [
            "Pata hai sabse bura kya lagta hai — jab mahine ke aakhri hafte sirf 200-300 rupaye bachte hain",
            "Woh feeling — jab dost ke saamne paise ke liye mana karna pade",
            "Yeh baat sirf woh samjhega jo kabhi raat ko neend nahi ayi paison ki chinta mein",
        ],
        "instruction": """
Hook type: EMOTIONAL MIRROR
Psychological trigger: Feeling deeply understood — most powerful emotional bond
Start by describing a very specific emotional pain that middle-class Indians feel but rarely discuss.
The viewer should think: "Yeh exactly wahi hai jo main feel karta hoon — yeh insaan samajhta hai."
Example: "Woh feeling — jab month ke last week mein ATM se 500 nikalte ho aur sochte ho 'bas yahi baccha hai'..."
"""
    },
    "CONSPIRACY_EXPOSE": {
        "trigger": "The system is DESIGNED to keep you poor",
        "hook_examples": [
            "India ka school system tumhein poor rakhne ke liye design kiya gaya hai — main prove karunga.",
            "Banks, companies, aur government — teeno milkar ek kaam karte hain. Aur tum woh target ho.",
            "Jo tumhe financial education nahi di gayi — woh accident nahi tha. Woh plan tha.",
        ],
        "instruction": """
Hook type: CONSPIRACY EXPOSE
Psychological trigger: Anger + validation — "I knew something was wrong"
Start with a bold accusation about how the system (school/bank/government/society) is designed to fail ordinary Indians.
This creates OUTRAGE which is one of the most powerful emotions for watch time and sharing.
Example: "India ka school system deliberately tumhe ek cheez nahi sikhata — aur woh cheez ameer log jaante hain."
"""
    },
}


async def generate_narration_and_subtitles(text, voice):
    logger.info(f"Generating TTS | Voice: {voice}")
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
    logger.info(f"✓ Audio: '{AUDIO_OUTPUT}' | Subtitles: '{SRT_OUTPUT}'")


def extract_scene_sequence(tagged_script):
    tags_found = re.findall(r'\[(' + '|'.join(VALID_TAGS) + r')\]', tagged_script, re.IGNORECASE)
    clean      = re.sub(r'\[(' + '|'.join(VALID_TAGS) + r')\]\s*', '', tagged_script, flags=re.IGNORECASE).strip()
    folders    = []
    for t in tags_found:
        key = t.lower().replace("_", "")
        folders.append(TAG_TO_FOLDER.get(key, "01_hook"))
    while len(folders) < 7:
        folders.append(random.choice(list(TAG_TO_FOLDER.values())))
    return clean, folders[:10]


def build_hindi_script():
    logger.info("=" * 70)
    logger.info("VIRAL PSYCHOLOGY ENGINE: Initializing Content Generation")
    logger.info("=" * 70)

    if not os.path.exists(TREND_FILE):
        trend_data = {"topic": "Middle Class India ka Financial Awakening",
                      "summary": "The hidden rules of money that schools never taught ordinary Indians"}
    else:
        with open(TREND_FILE, "r", encoding="utf-8") as f:
            trend_data = json.load(f)

    api_key     = os.environ.get("GEMINI_API_KEY")
    day_of_week = datetime.now().weekday()
    hook_type   = HOOK_TEMPLATES.get(day_of_week, "EMOTIONAL_MIRROR")
    hook_data   = HOOK_PSYCHOLOGY[hook_type]
    is_promo    = (datetime.now().day % 5 == 0)
    promo_cta   = ' End with: "Aur iska jawab bio mein link mein hai — kal delete ho sakta hai!"' if is_promo else ""

    if not api_key:
        logger.warning("No GEMINI_API_KEY. Using premium fallback.")
        return _premium_fallback(day_of_week)

    try:
        client = genai.Client(api_key=api_key)

        # ── BRAIN 2: Hook Competition — 10 hooks, pick highest scoring ────
        logger.info(f"Brain 2: Generating 10 hooks [{hook_type}]...")
        hook_examples = "\n".join(f"• {h}" for h in hook_data["hook_examples"])
        brain2 = f"""
You are India's most viral Hindi content strategist. You understand the PSYCHOLOGY of middle-class Indians deeply.

TODAY'S HOOK TYPE: {hook_type}
PSYCHOLOGICAL TRIGGER: {hook_data['trigger']}
HOOK STYLE GUIDE: {hook_data['instruction']}

EXAMPLE HOOKS (for inspiration only, don't copy):
{hook_examples}

TOPIC CONTEXT: {trend_data['topic']}

Generate 10 DIFFERENT powerful Hindi hooks for this hook type.

STRICT RULES:
- Write in CASUAL conversational Hindi (how friends talk, not textbooks)
- Maximum 10 words per hook
- Must create INSTANT gut reaction: shock, fear, curiosity, or pain recognition
- NEVER start with "Kya aapko pata hai"
- NEVER be generic — every word must earn its place
- Think about a 22-year-old middle-class Indian scrolling at 11pm after a bad day

Score each hook 1-10 for SCROLL-STOP POWER.

Return ONLY valid JSON:
{{"hooks": [{{"text": "hook in Hindi", "score": 9, "trigger": "emotion it creates"}}]}}
"""
        r2    = client.models.generate_content(model="gemini-2.0-flash", contents=brain2,
                                               config={"response_mime_type": "application/json"})
        hooks = json.loads(r2.text).get("hooks", [])
        hooks.sort(key=lambda h: h.get("score", 0), reverse=True)
        winning_hook = hooks[0]["text"] if hooks else "Ek baat hai jo tum nahi jaante..."
        logger.info(f"✓ Winning Hook [{hook_type}]: {winning_hook}")

        # ── BRAIN 3: Full Viral Script with Scene Architecture ─────────────
        logger.info("Brain 3: Writing psychological masterpiece script...")
        brain3 = f"""
You are the world's best Hindi viral content writer. You write for an Instagram page called "Indian Wealth Secrets" — targeting middle-class Indians who earn ₹20,000-₹80,000/month and secretly want financial freedom but don't know how.

WINNING HOOK (use EXACTLY this to open): {winning_hook}
TOPIC: {trend_data['topic']}
HOOK PSYCHOLOGY: {hook_type} — {hook_data['trigger']}
{promo_cta}

WRITE A MASTERPIECE 60-SECOND SCRIPT using this exact psychological architecture:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[HOOK] — 0 to 5 seconds — PATTERN INTERRUPT
Use the winning hook EXACTLY. Then 1-2 sentences that make this feel PERSONALLY relevant to the viewer.
This section must make a middle-class Indian feel: "Wait — is this about me?"

[STRUGGLE] — 5 to 18 seconds — PAIN AMPLIFICATION  
Describe the specific, real, painful struggle that middle-class Indians feel about money.
Use HYPER-SPECIFIC details: exact rupee amounts, specific time references, relatable Indian scenarios.
(e.g., "mahine ke last 5 din mein ATM se 200 rupaye nikalte hain", "EMI ka darr", "ghar wale ek aur naukri ke liye pressure dete hain")
DO NOT give the solution yet. AMPLIFY the pain. Make them feel it.

[SCHOOL_LIE] or [INDIA_LIFE] — 18 to 30 seconds — THE CONTRADICTION
Show WHY this problem exists — what did school/society teach them that was wrong?
OR show how this is a widespread Indian middle-class reality.
Build TENSION — the viewer should be thinking "to phir kya karna chahiye?"

[WORK] or [TECH] — 30 to 42 seconds — THE SHIFT
Introduce ONE specific, actionable insight. Not vague ("invest karo") but precise ("har mahine salary ka 15% pehle side mein daalo — baaki sab baad mein").
Give them a MOMENT OF REALIZATION — something clicks in their mind.

[MONEY] or [SUCCESS] — 42 to 52 seconds — THE FUTURE PICTURE
Paint a vivid, specific picture of what their life looks like 2-3 years after applying this insight.
Not "ameer ho jaoge" — specific: "ek din aayega jab tum bill pay karte waqt phone nahi dekhoge. Kyunki pata hoga — hoga."

[FREEDOM] or [LOOP] — 52 to 60 seconds — LOOP BAIT ENDING
End with ONE of these loop-bait techniques:
  A) Unanswered question: "Lekin ek aur cheez hai jo main ne abhi nahi bataya..." 
  B) Rewatch trigger: "Dobara dekho — shuru mein maine ek hint diya tha..."
  C) Identity statement: "Agar tune yeh save kiya — tu us 3% mein hai."
  D) Comment bait: "Comment mein likho: '3%' — agar tu sach mein badlna chahta hai."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CRITICAL WRITING RULES:
✅ Write EXACTLY how a real Indian talks — contractions, fillers, real slang ("yaar", "bhai", "suno", "dekho")
✅ Include specific numbers, years, and real Indian scenarios (EMI, chaiwala, naukri, sasural)
✅ Every sentence should either BUILD TENSION or DELIVER VALUE — no filler
✅ Use [SCENE_TAG] markers at each section transition (from: HOOK, STRUGGLE, SCHOOL_LIE, INDIA_LIFE, WORK, TECH, MONEY, SUCCESS, FREEDOM, LOOP)
✅ The script must feel like a real person is confessing something they lived through
✅ Total word count: 110-130 Hindi words (for 55-60 second narration)
✅ Keep sentences SHORT — maximum 12 words each (TTS sounds natural with short sentences)

❌ NEVER write: "Kya aapko pata hai", "Aaj main aapko bataunga", "Dosto"
❌ NEVER be generic: "paisa invest karo" → ALWAYS be specific: "PPF mein 500 rupaye — har mahine, aaj se"
❌ NEVER give advice that requires money to start — assume viewer has ₹0 savings today

Return ONLY this exact JSON (no markdown, no extra text):
{{
  "thumbnail_text": "3-5 Hindi words. Must shock or intrigue. (e.g. '97% log galat hain' or 'School ka biggest jhooth')",
  "tagged_script": "Full 60-second script in casual Hindi WITH [SCENE_TAG] markers embedded at each section transition",
  "instagram_caption": "5-7 lines casual Hindi. Line 1: Hook statement. Line 2-4: Value teaser. Line 5: Question for comments. End with: 'Save karo — kal kaam aayega 💾'",
  "instagram_hashtags": ["#IndianWealthSecrets", "#MiddleClassIndia", "#PaiseKiSacchai", "#HindiMotivation", "#FinancialFreedomIndia", "#GharSePaisa", "#IndiaWealth2026"],
  "youtube_title": "Hindi clickbait title under 60 chars — must create curiosity (e.g. 'School Ne Jo Nahi Bataya | Indian Wealth Secrets')",
  "youtube_tags": ["paise kaise kamaye", "middle class india", "financial freedom hindi", "india wealth secrets", "school ne nahi bataya", "hindi motivation"],
  "facebook_caption": "8-10 lines. More storytelling, longer form. Same topic but written as a personal confession/story. End with a specific question."
}}
"""
        r3   = client.models.generate_content(model="gemini-2.0-flash", contents=brain3,
                                              config={"response_mime_type": "application/json"})
        data = json.loads(r3.text)

        tagged         = data.get("tagged_script", "")
        clean, folders = extract_scene_sequence(tagged)
        logger.info(f"✓ Script generated | Scenes: {folders}")

        result = {
            "thumbnail_text":     data.get("thumbnail_text", "₹50,000 ka Raaz"),
            "script_text":        clean,
            "tagged_script":      tagged,
            "scene_sequence":     folders,
            "instagram_caption":  data.get("instagram_caption", ""),
            "instagram_hashtags": data.get("instagram_hashtags", []),
            "youtube_title":      data.get("youtube_title", ""),
            "youtube_tags":       data.get("youtube_tags", []),
            "facebook_caption":   data.get("facebook_caption", ""),
        }
        with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ Script saved: thumbnail='{result['thumbnail_text']}'")
        return result

    except Exception as e:
        logger.error(f"Brain failed: {e}")
        return _premium_fallback(day_of_week)


def _premium_fallback(day=0):
    """
    7 hand-crafted scripts — one per day of week.
    These are written using the exact viral psychological architecture above.
    They are NOT random fillers — they are masterpieces.
    """
    SCRIPTS = [
        # Monday — FORBIDDEN KNOWLEDGE
        {
            "thumbnail_text": "Ameer Log Chhupate Hain",
            "tagged_script": "[HOOK] Ek baat hai jo ameer baap apne bacchon ko sikhata hai — jo school kabhi nahi sikhata. [STRUGGLE] Hum sab mahine ki 1 tarikh ka wait karte hain — salary aaye, EMI bharo, kharcho, aur phir ek hafte mein zero. Aur yeh cycle chalti rehti hai — 25 saal se, 45 saal tak. [SCHOOL_LIE] School ne bataya — mehnat karo, naukri pakdo, save karo. Lekin save kahan? Bank mein? Jahan inflation 7% se zyada kha jaata hai? [WORK] Ameer log ek kaam karte hain jo hum nahi karte — woh pehle apne future-self ko pay karte hain. Salary aate hi — 15% side mein. Baki sab baad mein. [MONEY] 3 saal mein — woh 15% ek emergency fund ban jaata hai. Phir ek investment. Phir ek income source. [FREEDOM] Aur ek din aata hai — jab bill pay karte waqt tum phone nahi dekhte. Kyunki pata hota hai. [LOOP] Lekin ek cheez hai jo maine abhi bhi nahi bataya — dobara dekho — shuru mein ek hint tha.",
            "scene_sequence": ["01_hook", "02_struggle", "03_school_lie", "04_work", "05_money", "09_freedom", "10_loop"],
            "instagram_caption": "Ameer baap ek cheez sikhata hai — jo school kabhi nahi sikhata 🤫\n\nHar mahine ka cycle khatam nahi hota — salary, EMI, kharcha, zero.\n\nSirf ek rule ne yeh badla — 15% pehle, baaki baad mein.\n\n3 saal mein zindagi alag hoti hai. 💰\n\nKya tum yeh rule follow karte ho? Comment mein batao 👇\n\nSave karo — kal kaam aayega 💾",
            "youtube_title": "Ameer Log Jo Secret Rakhte Hain | School Ne Nahi Bataya",
            "facebook_caption": "Doston, ek baat share karna chahta hoon jo bahut mushkil se samjhi...\n\nMere papa mehnat karte the — poori zindagi. Lekin retire hote waqt loan tha. Kyun?\n\nKyunki school ne sikhaya 'save karo' — lekin kahan save karo yeh nahi bataya.\n\nBank mein rakha paisa har saal 7% inflation se chhota hota jaata hai.\n\nAmeer log jo karte hain: pehle 15% apne future ke liye — baki sab baad mein.\n\nYeh simple rule — 3-5 saal mein zindagi badal deta hai.\n\nKya aapne kabhi yeh try kiya? Comment mein zaroor batao. 👇",
        },
        # Tuesday — IDENTITY ATTACK
        {
            "thumbnail_text": "Tum Yeh Galti Kar Rahe Ho",
            "tagged_script": "[HOOK] Jo tum abhi paison ke saath kar rahe ho — wahi cheez hai jo tumhe kabhi ameer nahi banegi. [STRUGGLE] Main jaanta hoon — tum mehnat karte ho. Late tak kaam karte ho. Overtime karte ho. Phir bhi mahine ke aakhir mein 200-300 rupaye bachte hain. Aur tum sochte ho — 'thodi aur salary hoti to sab theek hota.' [INDIA_LIFE] Lekin bhai — India mein jo 50,000 kamata hai, woh bhi yahi kehta hai. Jo 1 lakh kamata hai, woh bhi. Yeh salary ka problem nahi hai. [WORK] Yeh ek cheez ka problem hai — sequence ka. Tum pehle kharche karte ho, phir bachate ho. Ameer log ulta karte hain — pehle bachaate hain, phir kharche karte hain. [MONEY] Sirf yeh sequence badlo — pehle 10% apne liye, baaki sab pe zindagi chalaao. 6 mahine mein fark dikhai dega. [SUCCESS] Ek din aayega — jab ATM pe 500 nikalte waqt tumhara dil nahi dhadkta. [LOOP] Comment mein likho sirf '10%' — agar tu aaj se yeh shuru karna chahta hai.",
            "scene_sequence": ["01_hook", "02_struggle", "07_india_life", "04_work", "05_money", "06_success", "10_loop"],
            "instagram_caption": "Jo tum abhi paison ke saath kar rahe ho — yahi galti hai 😬\n\nMehnat tum karte ho. Overtime bhi. Phir bhi zero kyun?\n\nSequence galat hai — pehle kharcho, phir bacho? Ulta karo.\n\nPehle 10% apne liye. Baaki pe zindagi chalaao. 💡\n\nComment mein '10%' likho agar aaj se shuru karna chahte ho 👇\n\nSave karo — kal kaam aayega 💾",
            "youtube_title": "Yeh Ek Galti Jo Tumhe Kabhi Ameer Nahi Banegi | Hindi",
            "facebook_caption": "Seedha poochhhna chahta hoon — kya aap bhi yeh karte ho?\n\nSalary aati hai. EMI jaati hai. Ghar ka kharcha jaata hai. Jo bacha, bachaaya.\n\nYahi galti hai.\n\nAmeer log pehle apne liye 10-20% nikalte hain — uske baad baaki kharcha karte hain.\n\nHum ulta karte hain — isliye hamesha zero pe aate hain.\n\nSirf sequence badlo. Aaj se. Agle mahine fark dikhai dega.\n\nKya aap try karenge? 👇",
        },
        # Wednesday — REAL STORY
        {
            "thumbnail_text": "₹847 Tha Account Mein",
            "tagged_script": "[HOOK] December 2022. Mere account mein sirf 847 rupaye the. Salary aane mein 3 hafte. [STRUGGLE] Main ek private company mein kaam karta tha — 22,000 ki salary. EMI 9,000. Ghar ka kiraaya 6,000. Aur us raat wife ne kaha — 'baby ki shoes leni hain.' Main bathroom mein gaya aur aankhein band kar li. [INDIA_LIFE] Woh raat main soya nahi. Phone pe YouTube scroll karta raha. 2 baje ek video aaya — ek ladke ne bataya ki woh ghar se laptop pe 40,000 kama raha hai. Main hansa. Bakwaas lagaa. [TECH] Lekin phir socha — agar try karke dekhta hoon? Kya jaata hai? Us raat ek free freelancing course liya. 2 hafte tak roz 1 ghanta. [WORK] Teen mahine baad — pehla client. 8,000 rupaye. Aankhon mein aansu aa gaye. [MONEY] Aaj woh 8,000 nahi — 55,000 hai. Har mahine. Ghar se. [LOOP] Aur woh 847 rupaye wali raat — woh meri zindagi ka turning point tha. Kya tumhari bhi ek aisi raat aayi hai? Comment mein batao.",
            "scene_sequence": ["01_hook", "02_struggle", "07_india_life", "08_tech", "04_work", "05_money", "10_loop"],
            "instagram_caption": "December 2022. Account mein ₹847. Salary aane mein 3 hafte. 🥺\n\nWoh raat neend nahi aayi. 2 baje ek video dekha jisne zindagi badal di.\n\n3 mahine mein ₹8,000 kamaaye. Aaj ₹55,000 — har mahine, ghar se.\n\nShuru karne ke liye ₹0 chahiye. Sirf ek raat chahiye.\n\nKya tumhari bhi aisi raat aayi hai? 👇\n\nSave karo — kal kaam aayega 💾",
            "youtube_title": "₹847 Se ₹55,000 Tak | Meri Real Story | Hindi",
            "facebook_caption": "Woh raat main kabhi nahi bhulunga.\n\nDecember 2022. Account mein ₹847. EMI baaki. Ghar ka kiraaya baaki. Aur wife ne kaha baby ki shoes chahiye.\n\nMain bathroom mein gaya aur chup chap roya.\n\nUs raat kuch naya try karne ka decide kiya — ek free freelancing course liya. Roz 1 ghanta.\n\nTeen mahine baad: pehla client — ₹8,000.\n\nAaj: ₹55,000/month — ghar se.\n\nYeh story isliye share ki kyunki bahut log us ₹847 wali feeling se guzar rahe hain abhi bhi.\n\nAgar tum bhi — comment karo. Main bata sakta hoon kaise shuru karein. 👇",
        },
        # Thursday — SHOCKING CONTRAST
        {
            "thumbnail_text": "Padhne Wala Sabse Garib",
            "tagged_script": "[HOOK] Tumhare ghar mein jo sabse zyada padhne wala hai — woh sabse garib retire hoga. Yeh harsh hai. Lekin sach hai. [STRUGGLE] India mein jo baccha A grades laata hai — woh 22 saal mein MBA karta hai. Loan leta hai. 4 lakh ka. Phir ek naukri milti hai — 35,000 ki. Loan, EMI, kiraaya — aur 40 saal tak wahi karta rehta hai. [SCHOOL_LIE] Lekin usi gali mein jo baccha 8th fail hua — usne papa ki dukaan sambhali. Seekha kaise cheezein bikti hain. Seekha customer ko kaise handle karte hain. Aaj uski 3 branches hain. [INDIA_LIFE] School ne grades sikhaye — paisa banana nahi sikhaya. [WORK] Yeh nahi matlab ki school mat jao. Matlab yeh hai ki school ke baad bhi seekhte rehna — sirf woh cheezein jo school ne nahi sikhaya. [MONEY] Financial literacy. Investing. Multiple income. [SUCCESS] Teen saal mein woh insaan kahin aur hota hai — jo yeh seekhta hai. [LOOP] Comment mein likho — 'school ne tumhe kya nahi sikhaya?' Main padhna chahta hoon.",
            "scene_sequence": ["01_hook", "02_struggle", "03_school_lie", "07_india_life", "04_work", "05_money", "10_loop"],
            "instagram_caption": "Jo sabse zyada padha-likha hai — woh retire hoga sabse garib 😶\n\n22 saal padhai. Loan. Naukri. EMI. 40 saal. Retire.\n\nVs: 8th fail. Dukaan. 3 branches. Financial freedom.\n\nSchool ne grades sikhaye — paisa banana nahi sikhaya. 📚\n\nComment mein batao — 'school ne tujhe kya nahi sikhaya?' 👇\n\nSave karo — kal kaam aayega 💾",
            "youtube_title": "Sabse Padhne Wala Sabse Garib Kyun Hota Hai | Hard Truth",
            "facebook_caption": "Ek baat batao — kya yeh aapke ghar mein bhi hua?\n\nSabse zyada padhne wala baccha — highest grades. Best college. Highest loan. Best naukri.\n\nAur 40 saal baad? Retire kiya — loan ke saath, savings ke bina.\n\nLekin padhai chhodne wale ki dukaan? 3 branches.\n\nMaine bahut sochha iss pe. School ne sirf ek cheez nahi sikhaya — paisa kaise kaam karta hai.\n\nGrades sikh gaye. Interviews sikh gaye. Presentation sikh gaye. Investing? Zero.\n\nYeh fix karna ho sakta hai — magar school ke baad. Khud se seekhna hoga.\n\nKya aap agree karte hain? Comment karein. 👇",
        },
        # Friday — THE CHALLENGE
        {
            "thumbnail_text": "Himmat Hai To Dekho",
            "tagged_script": "[HOOK] Ek kaam karo — abhi, is second. Apna bank balance dekho. Jo number hai — kya 5 saal baad bhi wahi hoga? [STRUGGLE] Agar kuch nahi badla — haan. Exactly wahi hoga. Thoda aur kam, actually. Kyunki inflation har saal 6-7% tumhara paisa kha jaata hai. Jo ₹10,000 aaj hain — 5 saal baad woh ₹7,000 ki value ke hain. [INDIA_LIFE] India mein 80% log bank mein paisa rakhte hain — savings account mein. 3-4% interest milta hai. Inflation 7%. Net loss: har saal 3-4%. Yeh savings nahi — slow poison hai. [WORK] Ek kaam karo — is mahine ki salary ka sirf 10%, koi bhi index fund mein daalo. Zerodha, Groww — 5 minute mein shuru hota hai. Sirf 10%. [MONEY] 10 saal mein woh 10% — agar market ka average return bhi mila — 4x ho jaata hai. [SUCCESS] Matlab: aaj ke ₹5,000 — 10 saal mein ₹20,000. Bina kuch kiye. [LOOP] Aur agar tum 20% karo? Comment mein calculate karo.",
            "scene_sequence": ["01_hook", "02_struggle", "07_india_life", "04_work", "05_money", "06_success", "10_loop"],
            "instagram_caption": "Ek kaam karo — abhi. Bank balance dekho. 👀\n\nWoh number 5 saal baad bhi wahi hoga — agar kuch nahi badla.\n\nInflation 7% hai. Bank interest 3%. Tum LOSE kar rahe ho — har saal.\n\n10% index fund mein daalo — 10 saal mein 4x. Zerodha pe 5 min. 💹\n\nKitne invest karoge? Comment mein number likho 👇\n\nSave karo — kal kaam aayega 💾",
            "youtube_title": "Bank Mein Paisa Rakhna Matlab Gareebi Ki Taraf Jaana | Proof",
            "facebook_caption": "Ek challenge — aaj apna bank balance dekho.\n\nAb socho — yeh 5 saal baad kitna hoga?\n\nAgar savings account mein rakha — 3-4% interest. Inflation 7%. Net result: har saal ghatta.\n\n₹1 lakh aaj — 5 saal baad ₹85,000 ki purchasing power. Bina kuch kiye.\n\nAlternative: Index fund. Market average 12% return. Same ₹1 lakh — 5 saal mein ₹1.76 lakh.\n\nFark: ₹91,000 — sirf ek decision se.\n\nMaine yeh 3 saal pehle seekha. Kash koi pehle batata.\n\nKya aap invest karte hain? Kahan? Comment mein batao. 👇",
        },
        # Saturday — EMOTIONAL MIRROR
        {
            "thumbnail_text": "Woh Feeling — Sirf Tum Samjhoge",
            "tagged_script": "[HOOK] Woh feeling — jab month ke aakhri hafte mein ATM se 500 nikalte ho aur sochte ho — 'bas yahi baccha hai.' [STRUGGLE] Koi nahi samjhega yeh feeling — jo daily kaam pe jaata hai, poori mehnat karta hai, phir bhi month ke last week mein paani pi ke raat guzaarta hai. Family ko batana nahi. Dost ke saamne normal rehna. Lekin andar se ek darr rehta hai — 'agar koi emergency aayi to?' [INDIA_LIFE] Yeh middle class India ki sabse badi pain hai — itna kamaate hain ki bhukhe nahi rehte. Itna nahi kamaate ki fikr-free ho sakein. [TECH] Main teri baat kar raha hoon — jo yeh video raat ko dekh raha hai, shayad neend nahi aa rahi paison ki chinta mein. [WORK] Ek cheez hai jo yeh cycle todti hai — emergency fund. 3 mahine ka kharcha, side mein. Ek jagah. Sirf isliye ki darr khatam ho. [MONEY] Woh darr khatam hota hai — tab zindagi ke baaki decisions sahi hone lagte hain. [LOOP] Agar tune yeh save kiya — tu samajh gaya ki kya kehna chahta tha. Comment mein likho: 'samajh gaya'.",
            "scene_sequence": ["01_hook", "02_struggle", "07_india_life", "08_tech", "04_work", "05_money", "10_loop"],
            "instagram_caption": "Woh feeling — ATM pe 500 nikalte ho, sochte ho 'bas yahi baccha hai' 😔\n\nFamily ko batao nahi. Dost ke saamne normal raho. Andar darr.\n\nYeh middle class India ki sabse real pain hai.\n\nEk cheez yeh cycle todti hai — emergency fund. 3 mahine ka kharcha, side mein.\n\nWoh darr khatam ho — baaki sab theek hota hai. 💙\n\nKya tune kabhi yeh feel kiya? Comment mein 'haan' likho 👇\n\nSave karo — kal kaam aayega 💾",
            "youtube_title": "Middle Class India Ki Sabse Badi Takleef | Emotional Truth",
            "facebook_caption": "Kuch baat karni thi...\n\nWoh feeling jaante ho — mahine ke last week mein ATM se 500 nikaalte ho aur sochte ho 'bas yahi baccha hai'?\n\nFamily ko nahi batate. Dost ke saamne normal rehte ho. Lekin andar ek darr hota hai.\n\nYeh middle class India ki most real pain hai. Itna kamaate hain ki bhukhe nahi rehte. Itna nahi kamaate ki tension free ho sakein.\n\nMaine yeh saalon tak feel kiya.\n\nPhir ek cheez ki — emergency fund. 3 mahine ka kharcha, alag rakha. ₹500/mahine se bhi shuru ho sakta hai.\n\nJab woh darr khatam hua — baaki decisions apne aap sahi hone lage.\n\nKya aap bhi yeh feel karte hain? Akele mat raho — comment mein share karo. 👇",
        },
        # Sunday — CONSPIRACY EXPOSE
        {
            "thumbnail_text": "System Ne Tumhe Trap Kiya",
            "tagged_script": "[HOOK] India ka school system deliberately tumhe ek cheez nahi sikhata — aur woh cheez ameer log jaante hain. Yeh accident nahi tha. [STRUGGLE] Sochte hain — kya sikhaya school ne? Addition, subtraction, history, geography. Kya sikhaya nahi? Compound interest. Tax saving. Investing. Multiple income sources. Kyun? [SCHOOL_LIE] Kyunki agar 140 crore Indians samajh jaayein paisa kaise kaam karta hai — toh kaun factory mein kaam karega? Kaun 20,000 ki naukri pe khush rehega? Kaun credit card ka interest bharta rehega? [INDIA_LIFE] Yeh system tum pe depend karta hai — confused rehne ke liye. Debt mein rehne ke liye. 9-to-5 mein rehne ke liye. [WORK] Lekin ab internet ne sab badal diya. Jo pehle sirf rich families ke bachchon ko pata tha — woh sab YouTube pe, free mein hai. [MONEY] Financial literacy. Index funds. Passive income. Yeh sab seekha ja sakta hai — free mein, ghar pe. [LOOP] System ne tumhein trap kiya — lekin trap se bahar nikalna bhi tumhare haath mein hai. Comment mein likho: 'Main niklungaa'.",
            "scene_sequence": ["01_hook", "02_struggle", "03_school_lie", "07_india_life", "08_tech", "05_money", "10_loop"],
            "instagram_caption": "School system ne deliberately yeh nahi sikhaya — kyunki unhe tumhara confused rehna zaroori tha 🔥\n\nCompound interest? Nahi. Investing? Nahi. Multiple income? Nahi.\n\nKyunki 140 crore samajh jaate — factories mein kaun kaam karta?\n\nLekin ab internet free hai. Woh sab seekha ja sakta hai — ghar pe. 💻\n\nComment mein likho: 'Main niklungaa' — agar tu ready hai 👇\n\nSave karo — kal kaam aayega 💾",
            "youtube_title": "School Ne Tumhein Trap Kyun Kiya | Dark Truth India",
            "facebook_caption": "Yeh baat sunne mein conspiracy theory lagti hai — lekin sach hai.\n\nSchool ne tumhe addition, history, geography sikhaya.\n\nKya nahi sikhaya? Paisa kaise kaam karta hai.\n\nCompound interest? Zero. Tax saving? Zero. Passive income? Zero.\n\nKyun? Ek simple reason: agar 140 crore Indians yeh samajh jaayein — 20,000 wali naukri pe kaun khush rahega? Credit card ka 36% interest kaun bharta rahega?\n\nSystem ko tumhara confused rehna ZAROORI hai.\n\nLekin internet ne game badal diya. Jo pehle sirf rich families ke bacchon ko pata tha — woh sab free mein available hai.\n\nQuestion: kya aap seekhne ke liye ready hain?\n\nComment mein batao — aap kahan se shuru karna chahenge? 👇",
        },
    ]

    script = SCRIPTS[day % len(SCRIPTS)]
    clean, folders = extract_scene_sequence(script["tagged_script"])
    result = {
        "thumbnail_text":     script["thumbnail_text"],
        "script_text":        clean,
        "tagged_script":      script["tagged_script"],
        "scene_sequence":     script.get("scene_sequence", folders),
        "instagram_caption":  script["instagram_caption"],
        "instagram_hashtags": ["#IndianWealthSecrets", "#MiddleClassIndia", "#PaiseKiSacchai",
                               "#HindiMotivation", "#FinancialFreedomIndia", "#GharSePaisa", "#IndiaWealth2026"],
        "youtube_title":      script["youtube_title"],
        "youtube_tags":       ["paise kaise kamaye", "middle class india", "financial freedom hindi",
                               "india wealth secrets", "school ne nahi bataya", "hindi motivation"],
        "facebook_caption":   script["facebook_caption"],
    }
    with open(SCRIPT_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info(f"✓ Premium fallback (Day {day}): '{result['thumbnail_text']}'")
    return result


def run():
    script = build_hindi_script()
    voice  = VOICES[datetime.now().day % 2]["name"]
    asyncio.run(generate_narration_and_subtitles(script["script_text"], voice))


if __name__ == "__main__":
    run()
