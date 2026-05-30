#!/usr/bin/env python3
"""
B-ROLL LIBRARY BUILDER — One-Time Setup Script

Downloads 100 curated 4K vertical Pexels video clips into 10 emotional category folders.
This runs ONCE on first GitHub Actions startup. After that, the library is permanent.
The video engine reads from this library for perfect voice-visual sync forever.

Categories:
  01_hook        — Shocked faces, intense eye contact, dramatic close-ups
  02_struggle    — Stress, financial worry, tired people, empty wallets
  03_school_lie  — Education, textbooks, classrooms, graduation
  04_work        — Laptops, typing, hustle, late nights, productivity
  05_money       — Cash, bank screens, stock graphs, wealth
  06_success     — Celebration, confidence, achievement, happiness
  07_india_life  — Indian streets, families, real daily Indian life
  08_tech        — Smartphones, apps, digital screens, AI screens
  09_freedom     — Sunrise, mountain tops, open roads, travel
  10_loop        — Direct camera, pointing, sharing, tagging moments
"""

import os
import json
import logging
import requests
import random

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("BRollLibraryBuilder")

MANIFEST_FILE = "broll/manifest.json"
PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"

# ─── CURATED SEARCH QUERIES PER CATEGORY ───────────────────────────────────
# Each query is hand-selected to find the most visually impactful clips.
# 10 queries × 10 categories = 100 clips total.
BROLL_CATEGORIES = {
    "01_hook": [
        "person shocked looking phone portrait",
        "man surprised expression face portrait",
        "close up eyes dramatic portrait",
        "woman shocked reaction face",
        "person serious direct camera",
        "man jaw drop surprised",
        "person amazed disbelief portrait",
        "close up face dramatic lighting",
        "young man intense expression",
        "person dramatic reaction phone",
    ],
    "02_struggle": [
        "man stressed financial problems",
        "person worried counting money",
        "stressed person head down",
        "man sitting floor worried",
        "person financial stress bills",
        "worried man phone bad news",
        "stressed person late night",
        "person holding head stress",
        "man disappointed failure",
        "person sad empty room",
    ],
    "03_school_lie": [
        "student studying books night",
        "classroom lecture education",
        "graduation ceremony diploma",
        "student exam stress face",
        "textbook studying desk lamp",
        "person reading book serious",
        "library studying alone",
        "student tired books night",
        "college university lecture hall",
        "person diploma certificate",
    ],
    "04_work": [
        "person typing laptop home",
        "hands typing keyboard close up",
        "freelancer working laptop coffee",
        "person coding computer night",
        "entrepreneur focused laptop screen",
        "hands writing notebook pen",
        "man working desk productive",
        "woman laptop home office",
        "person phone working business",
        "night worker laptop hustle",
    ],
    "05_money": [
        "cash money bills hand",
        "stock market chart growing",
        "bank transfer phone notification",
        "businessman counting money",
        "investment growth graph",
        "wallet full money cash",
        "person phone financial app",
        "financial success money table",
        "phone screen bank balance",
        "cryptocurrency digital money",
    ],
    "06_success": [
        "man celebrating success arms",
        "person victory fist pump",
        "woman happy achievement smile",
        "man confident suit portrait",
        "person good news phone happy",
        "celebration success business",
        "person proud achievement",
        "winner happy jumping",
        "man success laptop smile",
        "entrepreneur happy confident",
    ],
    "07_india_life": [
        "india street market busy",
        "indian man portrait outdoor",
        "mumbai city life street",
        "young indian man urban",
        "india family home interior",
        "indian street chai tea",
        "india night city lights",
        "delhi busy market crowd",
        "india wedding celebration",
        "indian portrait face close",
    ],
    "08_tech": [
        "smartphone social media scrolling",
        "person phone screen dark room",
        "digital interface technology",
        "phone screen close up app",
        "technology concept futuristic",
        "online payment mobile phone",
        "person video call laptop",
        "dark screen phone glow",
        "social media notification phone",
        "digital data screen",
    ],
    "09_freedom": [
        "person sunrise mountain view",
        "man arms open freedom nature",
        "beach sunset freedom walk",
        "open road travel car",
        "person looking horizon dramatic",
        "sunrise morning sky beautiful",
        "person jump cliff nature",
        "forest freedom nature walk",
        "mountain top person standing",
        "person field open sky",
    ],
    "10_loop": [
        "person pointing camera serious",
        "man direct camera talking",
        "person serious face direct",
        "man camera eye contact portrait",
        "person direct talk camera",
        "man strong confident portrait",
        "person share phone screen",
        "man thinking look camera",
        "person remembering something",
        "man slow nod camera",
    ],
}

CLIPS_PER_CATEGORY = 10


def fetch_one_clip(query, pexels_key, used_ids):
    """Fetches one high-quality vertical clip from Pexels matching the query."""
    headers = {"Authorization": pexels_key}
    params = {"query": query, "orientation": "portrait", "per_page": 15, "size": "large"}
    
    try:
        resp = requests.get(PEXELS_VIDEO_URL, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        videos = resp.json().get("videos", [])
        
        # Pick first non-duplicate
        for vid in videos:
            if vid["id"] not in used_ids:
                # Sort by resolution — pick highest quality vertical
                files = sorted(vid.get("video_files", []),
                               key=lambda f: f.get("width", 0) * f.get("height", 0),
                               reverse=True)
                for f in files:
                    w, h = f.get("width", 0), f.get("height", 0)
                    if h >= w:  # Must be portrait
                        used_ids.add(vid["id"])
                        return f["link"], vid["id"], f"{w}x{h}"
        
        # Fallback: first video even if used
        if videos:
            vid = videos[0]
            files = sorted(vid.get("video_files", []),
                           key=lambda f: f.get("width", 0) * f.get("height", 0),
                           reverse=True)
            if files:
                f = files[0]
                return f["link"], vid["id"], f"{f.get('width')}x{f.get('height')}"
    except Exception as e:
        logger.warning(f"  Pexels error for '{query}': {e}")
    
    return None, None, None


def download_clip(url, save_path):
    try:
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        return True
    except Exception as e:
        logger.error(f"  Download failed: {e}")
        return False


def build_library():
    pexels_key = os.environ.get("PEXELS_API_KEY")
    if not pexels_key:
        logger.error("Missing PEXELS_API_KEY. Cannot build B-Roll library.")
        return

    # Check if already built
    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE) as f:
            manifest = json.load(f)
        if manifest.get("complete") and manifest.get("total_clips", 0) >= 50:
            logger.info(f"B-Roll library already built ({manifest['total_clips']} clips). Skipping.")
            return

    logger.info("=" * 60)
    logger.info("BUILDING B-ROLL LIBRARY — This runs only ONCE")
    logger.info("=" * 60)

    os.makedirs("broll", exist_ok=True)
    manifest = {"categories": {}, "total_clips": 0, "complete": False}
    used_ids = set()
    total = 0

    for category, queries in BROLL_CATEGORIES.items():
        folder = f"broll/{category}"
        os.makedirs(folder, exist_ok=True)
        manifest["categories"][category] = []
        
        logger.info(f"\n📁 Category: {category}")
        
        for i, query in enumerate(queries[:CLIPS_PER_CATEGORY]):
            clip_path = f"{folder}/clip_{i+1:02d}.mp4"
            
            # Skip if already exists and has content
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 100_000:
                logger.info(f"  [{i+1}] Clip exists: {clip_path}")
                manifest["categories"][category].append(clip_path)
                total += 1
                continue

            url, vid_id, res = fetch_one_clip(query, pexels_key, used_ids)
            if url:
                logger.info(f"  [{i+1}] '{query[:40]}' → {res}")
                if download_clip(url, clip_path):
                    manifest["categories"][category].append(clip_path)
                    total += 1
                    logger.info(f"  ✓ Saved: {clip_path}")
            else:
                logger.warning(f"  [{i+1}] No clip found for '{query}'")

    manifest["total_clips"] = total
    manifest["complete"] = True
    os.makedirs("broll", exist_ok=True)
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)

    logger.info(f"\n✅ B-ROLL LIBRARY COMPLETE: {total} clips across {len(BROLL_CATEGORIES)} categories")


if __name__ == "__main__":
    build_library()
