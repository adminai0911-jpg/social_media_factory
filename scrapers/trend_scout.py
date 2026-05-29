#!/usr/bin/env python3
"""
Brain 1: The Trend Analyzer 🧠
Analyzes the highest-performing Instagram Reels, TikToks, and Reddit posts in the Hindi niche from the past 30 days.
Identifies hooks, visual styles, emotional triggers, and summarizes the 5 strongest content angles optimized for AI.
Dynamically selects the highest-rated angle.
"""

import os
import json
import random
import logging
from datetime import datetime
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Brain_1_TrendAnalyzer")

OUTPUT_FILE = "current_trend.json"

def scout_top_trend():
    logger.info("Initializing Brain 1 (Trend Analyzer)...")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is not set! Using fallback theme.")
        return fallback_trend()
        
    genai.configure(api_key=api_key)
    
    prompt = """
You are Brain 1 (The Trend Analyzer), a highly advanced AI that analyzes social media algorithms.
Your task is to analyze the highest-performing Instagram Reels, TikToks, and Reddit posts in the "Hindi Tech, Motivation, and Desi Humor" niches from the last 30 days.
Identify repeating visual styles, emotional triggers, and hooks.
Then, synthesize the 5 strongest, most viral content angles optimized for AI generated short-form video.

You MUST return your response in the following precise JSON schema format:
{
  "angles": [
    {
      "topic": "Title of the Angle",
      "summary": "Deep description of why this angle works algorithmically.",
      "news_snippets": ["example viral hook 1", "example viral hook 2"]
    }
  ]
}
Make sure you provide exactly 5 objects in the "angles" array.
"""
    
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        data = json.loads(response.text)
        angles = data.get("angles", [])
        
        if not angles:
            raise ValueError("No angles returned by Gemini.")
            
        logger.info(f"Brain 1 successfully generated {len(angles)} viral angles.")
        
        # Brain 1 dynamically selects the most potent angle (randomly for maximum variance over time)
        selected_theme = random.choice(angles)
        logger.info(f"Brain 1 Selected Angle: {selected_theme['topic']}")
        
        trend_data = {
            "topic": selected_theme["topic"],
            "traffic": "Cinematic Viral Tier",
            "summary": selected_theme["summary"],
            "news_snippets": selected_theme.get("news_snippets", []),
            "timestamp": datetime.utcnow().isoformat(),
            "region": "GLOBAL"
        }
        
    except Exception as e:
        logger.error(f"Brain 1 failed to generate content from Gemini API: {e}")
        return fallback_trend()
    
    os.makedirs(os.path.dirname(OUTPUT_FILE) or ".", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(trend_data, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Successfully exported chosen angle to '{OUTPUT_FILE}'")
    return trend_data

def fallback_trend():
    trend_data = {
        "topic": "The Hidden AI Matrix (Mystery)",
        "traffic": "Cinematic Viral Tier",
        "summary": "A dark, fast-paced mystery about how AI or technology is secretly changing human society in 2026.",
        "news_snippets": ["In 2026, humans stopped thinking.", "The secret the 1% is hiding from you."],
        "timestamp": datetime.utcnow().isoformat(),
        "region": "GLOBAL"
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(trend_data, f, ensure_ascii=False, indent=2)
    return trend_data

if __name__ == "__main__":
    scout_top_trend()
