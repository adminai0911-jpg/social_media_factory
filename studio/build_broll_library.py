#!/usr/bin/env python3
"""
B-ROLL LIBRARY BUILDER — Phase 12.1 (100% Indian Visuals)

Every single search query is now India-specific.
Indian faces, Indian places, Indian emotions, Indian life.
This creates authentic resonance with the Indian audience.
"""

import os
import json
import logging
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("BRollLibraryBuilder")

MANIFEST_FILE = "broll/manifest.json"
PEXELS_VIDEO_URL = "https://api.pexels.com/videos/search"

# ─── 100% INDIA-SPECIFIC CURATED SEARCHES ──────────────────────────────────
BROLL_CATEGORIES = {
    "01_hook": [
        "shocked indian man face portrait",
        "surprised indian woman expression close up",
        "young indian man intense look camera",
        "indian man jaw drop amazed",
        "india man disbelief phone reaction",
        "shocked indian person close up portrait",
        "indian man serious eye contact camera",
        "india woman surprised dramatic portrait",
        "young indian man dramatic expression",
        "indian man react phone screen night",
    ],
    "02_struggle": [
        "indian man stressed financial problem",
        "india family financial stress home",
        "indian man worried sitting alone",
        "india woman stressed bills money",
        "indian man head down depressed",
        "india family struggling poverty",
        "young indian man unemployed worried",
        "indian person counting money stressed",
        "india man frustrated phone bad news",
        "indian family night worried home",
    ],
    "03_school_lie": [
        "indian students classroom studying",
        "india school children education",
        "indian student exam stressed books",
        "india graduation ceremony diploma",
        "indian college university lecture",
        "india student textbook night lamp",
        "indian school uniform children",
        "india student studying hard night",
        "indian young person reading books",
        "india university campus students",
    ],
    "04_work": [
        "indian man laptop work home office",
        "india woman working computer desk",
        "indian freelancer typing laptop",
        "india man coding computer night",
        "indian entrepreneur focused laptop",
        "india woman professional home laptop",
        "indian man writing notes notebook",
        "india person phone business call",
        "indian man hustle work late night",
        "india young professional desk work",
    ],
    "05_money": [
        "indian rupee notes cash hand",
        "india man counting money rupees",
        "indian phone bank transfer notification",
        "india rupee bills wallet rich",
        "indian man phone financial app success",
        "india stock market phone screen",
        "indian businessman money office",
        "india rupee currency savings",
        "indian man excited phone good news money",
        "india digital payment phone upi",
    ],
    "06_success": [
        "successful indian man smiling confident",
        "india woman achievement happy proud",
        "indian entrepreneur success office",
        "india man celebrating good news phone",
        "indian man fist pump victory",
        "india woman professional confident smile",
        "successful young indian businessman",
        "india man happy laptop success",
        "indian person proud achievement arms up",
        "india man confident winner portrait",
    ],
    "07_india_life": [
        "india street market crowd busy",
        "mumbai city life people street",
        "indian family home dinner together",
        "india chai tea street vendor",
        "young indian man city portrait outdoor",
        "india wedding celebration crowd",
        "indian family living room together",
        "delhi street market india",
        "india rural village life authentic",
        "indian people outdoor daily life",
    ],
    "08_tech": [
        "indian man smartphone scrolling social media",
        "india person phone dark room glow",
        "indian young man phone night bed",
        "india person online payment phone",
        "indian man video call laptop home",
        "india smartphone app notification",
        "young indian man phone serious face",
        "india person laptop technology",
        "indian man phone surprised screen",
        "india technology digital phone person",
    ],
    "09_freedom": [
        "indian man sunrise mountain view",
        "india person open road freedom travel",
        "indian man arms open nature landscape",
        "india beach sunset freedom walk",
        "young indian man looking horizon",
        "india sunrise morning beautiful sky",
        "indian man forest nature freedom",
        "india person standing hill sunrise",
        "young indian man jump freedom outdoor",
        "india beautiful landscape person",
    ],
    "10_loop": [
        "indian man direct camera talking serious",
        "india man pointing camera strong",
        "young indian man eye contact camera",
        "india man slow nod camera portrait",
        "indian man thinking look camera",
        "india man serious face direct camera",
        "young indian man camera strong confident",
        "india man sharing phone screen",
        "indian man remembering camera thoughtful",
        "india man strong confident portrait camera",
    ],
}

CLIPS_PER_CATEGORY = 10


def fetch_one_clip(query, pexels_key, used_ids):
    headers = {"Authorization": pexels_key}
    params  = {"query": query, "orientation": "portrait", "per_page": 15, "size": "large"}
    try:
        resp   = requests.get(PEXELS_VIDEO_URL, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        videos = resp.json().get("videos", [])
        for vid in videos:
            if vid["id"] not in used_ids:
                files = sorted(vid.get("video_files", []),
                               key=lambda f: f.get("width", 0) * f.get("height", 0),
                               reverse=True)
                for f in files:
                    if f.get("height", 0) >= f.get("width", 0):
                        used_ids.add(vid["id"])
                        return f["link"], vid["id"], f"{f.get('width')}x{f.get('height')}"
        if videos:
            vid   = videos[0]
            files = sorted(vid.get("video_files", []),
                           key=lambda f: f.get("width", 0) * f.get("height", 0), reverse=True)
            if files:
                f = files[0]
                return f["link"], vid["id"], f"{f.get('width')}x{f.get('height')}"
    except Exception as e:
        logger.warning(f"  Error '{query}': {e}")
    return None, None, None


def download_clip(url, path):
    try:
        resp = requests.get(url, stream=True, timeout=60)
        resp.raise_for_status()
        with open(path, "wb") as f:
            for chunk in resp.iter_content(1024 * 1024):
                if chunk: f.write(chunk)
        return True
    except Exception as e:
        logger.error(f"  Download failed: {e}")
        return False


def build_library():
    pexels_key = os.environ.get("PEXELS_API_KEY")
    if not pexels_key:
        logger.error("Missing PEXELS_API_KEY.")
        return

    if os.path.exists(MANIFEST_FILE):
        with open(MANIFEST_FILE) as f:
            manifest = json.load(f)
        if manifest.get("complete") and manifest.get("total_clips", 0) >= 50:
            logger.info(f"B-Roll library ready ({manifest['total_clips']} clips). Skipping rebuild.")
            return

    logger.info("=" * 60)
    logger.info("BUILDING INDIA B-ROLL LIBRARY (100% Indian Visuals)")
    logger.info("=" * 60)

    os.makedirs("broll", exist_ok=True)
    manifest = {"categories": {}, "total_clips": 0, "complete": False}
    used_ids = set()
    total    = 0

    for category, queries in BROLL_CATEGORIES.items():
        folder = f"broll/{category}"
        os.makedirs(folder, exist_ok=True)
        manifest["categories"][category] = []
        logger.info(f"\n📁 [{category}]")

        for i, query in enumerate(queries[:CLIPS_PER_CATEGORY]):
            clip_path = f"{folder}/clip_{i+1:02d}.mp4"
            if os.path.exists(clip_path) and os.path.getsize(clip_path) > 100_000:
                manifest["categories"][category].append(clip_path)
                total += 1
                continue
            url, vid_id, res = fetch_one_clip(query, pexels_key, used_ids)
            if url:
                logger.info(f"  [{i+1}] '{query[:45]}' → {res}")
                if download_clip(url, clip_path):
                    manifest["categories"][category].append(clip_path)
                    total += 1
            else:
                logger.warning(f"  [{i+1}] No result: '{query}'")

    manifest["total_clips"] = total
    manifest["complete"]    = True
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)
    logger.info(f"\n✅ INDIA B-ROLL LIBRARY COMPLETE: {total} clips")


if __name__ == "__main__":
    build_library()
