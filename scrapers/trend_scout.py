#!/usr/bin/env python3
"""
Brain 1: The ULTIMATE Trend Analyzer 🧠
Covers 5 high-earning niches: Wealth/Finance, AI/Tech, Motivation/Mindset, Mystery/Dark Truth, Desi Humor/Culture.
Generates 10 viral content angles, scores them by virality potential, and picks the best.
Rotates through all niches to ensure algorithm-safe content variance (prevents shadow-banning).
"""

import os
import json
import random
import logging
from datetime import datetime
from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Brain_1_TrendAnalyzer")

OUTPUT_FILE = "current_trend.json"

# 5 powerful niches that drive massive traffic in India
NICHES = [
    "Wealth Building, Side Hustles, and Passive Income in India",
    "Artificial Intelligence Tools and Career Growth for Indians",
    "Mindset, Motivation, and Success Habits of Top Performers",
    "Dark Truths, Hidden Secrets, and Mystery (clickbait curiosity)",
    "Relatable Desi Humor, Indian Culture, and Viral Challenges"
]

def scout_top_trend():
    logger.info("Initializing Brain 1 (The Ultimate Trend Analyzer)...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not set! Using fallback.")
        return fallback_trend()
        
    client = genai.Client()
    
    # Rotate through all 5 niches. Use day-of-week to ensure full weekly rotation.
    niche_index = datetime.utcnow().weekday() % len(NICHES)
    selected_niche = NICHES[niche_index]
    logger.info(f"Brain 1 Niche Rotation: Today's niche is '{selected_niche}'")
    
    prompt = f"""
You are Brain 1 (The Viral Trend Analyzer). You analyze the highest-performing content across Instagram, YouTube Shorts, and Reddit in India.

Today's focus niche: {selected_niche}
Today's date context: {datetime.utcnow().strftime('%B %Y')}

Your task:
1. Identify the 10 most VIRAL content angles in this niche RIGHT NOW in India.
2. For each angle, assign a virality score from 1 to 10 based on: Emotional Trigger, Shock Value, Shareability, and Search Volume.
3. Consider current events, seasonal trends, and what people in India are searching and sharing.

Return response ONLY in this exact JSON schema:
{{
  "angles": [
    {{
      "topic": "Title of the Angle",
      "virality_score": 9,
      "emotional_trigger": "Fear/Greed/Curiosity/Ego/Humor",
      "summary": "Why this works algorithmically and what makes Indians share it.",
      "news_snippets": ["Example viral hook in Hindi", "Another hook"]
    }}
  ]
}}
Provide exactly 10 objects in the "angles" array, sorted by virality_score descending.
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        data = json.loads(response.text)
        angles = data.get("angles", [])
        
        if not angles:
            raise ValueError("No angles returned.")
        
        # Sort by virality score and pick the highest
        angles_sorted = sorted(angles, key=lambda x: x.get("virality_score", 0), reverse=True)
        selected = angles_sorted[0]
        
        logger.info(f"Brain 1 Selected: '{selected['topic']}' (Virality Score: {selected.get('virality_score', 'N/A')}/10, Trigger: {selected.get('emotional_trigger', 'N/A')})")
        
        trend_data = {
            "topic": selected["topic"],
            "virality_score": selected.get("virality_score", 9),
            "emotional_trigger": selected.get("emotional_trigger", "Curiosity"),
            "summary": selected["summary"],
            "news_snippets": selected.get("news_snippets", []),
            "niche": selected_niche,
            "timestamp": datetime.utcnow().isoformat(),
            "region": "IN"
        }
        
    except Exception as e:
        logger.error(f"Brain 1 Gemini API failed: {e}")
        return fallback_trend()
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(trend_data, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Trend exported to '{OUTPUT_FILE}'")
    return trend_data

def fallback_trend():
    topics = [
        {"topic": "The Hidden AI Matrix", "summary": "A dark mystery about how AI is secretly reshaping India's economy and what the 1% knows.", "trigger": "Mystery"},
        {"topic": "Zero to 1 Lakh Monthly Income", "summary": "How ordinary Indians are building online income using free tools and AI in 2026.", "trigger": "Greed"},
        {"topic": "The Mindset of India's Self-Made Billionaires", "summary": "3 brutal psychological truths about wealth that schools never teach.", "trigger": "Ego"}
    ]
    chosen = random.choice(topics)
    trend_data = {
        "topic": chosen["topic"],
        "virality_score": 9,
        "emotional_trigger": chosen["trigger"],
        "summary": chosen["summary"],
        "news_snippets": ["क्या आपको पता है...", "यह सच जानकर आप हैरान हो जाएंगे!"],
        "niche": "General Viral",
        "timestamp": datetime.utcnow().isoformat(),
        "region": "IN"
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(trend_data, f, ensure_ascii=False, indent=2)
    return trend_data

if __name__ == "__main__":
    scout_top_trend()
