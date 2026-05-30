#!/usr/bin/env python3
"""
CINEMATIC STUDIO ENGINE — Phase 11 (The AI Documentary & Hormozi Editor)

Core upgrades:
1. CUSTOM AI VISUALS: Fetches hyper-realistic 1080x1920 AI images from Pollinations.ai 
   based on exact scene-synchronized prompts. No more random Pexels stock!
2. KEN BURNS PARALLAX: Converts static AI images into cinematic moving video clips.
3. HORMOZI KINETIC TYPOGRAPHY: Big, bold, yellow centered text with thick black outlines.
4. SFX DESIGN: Adds a cinematic "Whoosh" sound effect on every scene transition.
5. SRT TIMING + SEAMLESS XFADE: Clips are timed exactly to the voice, dissolving seamlessly.
"""

import os
import json
import logging
import requests
import subprocess
import urllib.request
import urllib.parse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("CinematicStudio")

SCRIPT_INPUT  = "script_output.json"
AUDIO_INPUT   = "audio_narration.mp3"
SRT_INPUT     = "subtitles.srt"
FINAL_REEL    = "final_reel.mp4"
BG_MUSIC_FILE = "bg_music.mp3"
WHOOSH_FILE   = "whoosh.mp3"

TARGET_W   = 1080
TARGET_H   = 1920
TARGET_FPS = 30

MUSIC_URLS = [
    "https://cdn.pixabay.com/download/audio/2022/08/02/audio_884fe92c21.mp3",
    "https://cdn.pixabay.com/download/audio/2023/03/09/audio_c8d34f9ebc.mp3",
]
# Free whoosh sound effect for transitions
WHOOSH_URL = "https://cdn.pixabay.com/download/audio/2022/03/15/audio_7ea20eb18a.mp3"

XFADE_DURATION = 0.6


# ──────────────────────────────────────────────────────────
# AUDIO TIMING & SRT
# ──────────────────────────────────────────────────────────

def get_audio_duration():
    cmd = ["ffprobe", "-i", AUDIO_INPUT, "-show_entries", "format=duration",
           "-v", "quiet", "-of", "csv=p=0"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(r.stdout.strip())
    except Exception:
        return 55.0

def parse_srt_word_times(srt_path):
    if not os.path.exists(srt_path): return []
    def ts_to_sec(ts):
        try:
            h, m, s = ts.strip().replace(",", ".").split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
        except: return 0.0
    entries = []
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()
    for block in content.strip().split("\n\n"):
        lines = [l.strip() for l in block.strip().splitlines()]
        arrow_line = next((l for l in lines if "-->" in l), None)
        if arrow_line:
            parts = arrow_line.split("-->")
            if len(parts) == 2:
                entries.append((ts_to_sec(parts[0]), ts_to_sec(parts[1])))
    return entries

def calculate_srt_segment_durations(num_clips, total_audio_duration):
    word_times = parse_srt_word_times(SRT_INPUT)
    if not word_times or num_clips <= 0:
        n = max(1, num_clips)
        clip_dur = (total_audio_duration + (n - 1) * XFADE_DURATION) / n
        return [max(clip_dur, 2.5)] * n

    n = min(num_clips, len(word_times))
    words_per_seg = max(1, len(word_times) // n)
    segments = []
    for i in range(n):
        start_idx = i * words_per_seg
        end_idx = start_idx + words_per_seg if i < n - 1 else len(word_times)
        seg_words = word_times[start_idx:end_idx]
        if not seg_words: continue
        raw_dur = seg_words[-1][1] - seg_words[0][0]
        segments.append(max(raw_dur + XFADE_DURATION, 2.5))
    
    if not segments: return [total_audio_duration / num_clips] * num_clips
    logger.info(f"SRT Timing: {len(segments)} clips — {segments}")
    return segments


# ──────────────────────────────────────────────────────────
# PHASE 11: HIGH-RES PHOTO PARALLAX (Pexels)
# ──────────────────────────────────────────────────────────

def fetch_ai_images(prompts):
    """
    Fetches exact-match high-res photography from Pexels Photo API.
    We use Photos instead of Videos because Photo search is 100x more accurate 
    and specific, ensuring the visual perfectly matches the voice script.
    These photos are then animated into cinematic video via Ken Burns Parallax.
    """
    pexels_key = os.environ.get("PEXELS_API_KEY")
    if not pexels_key:
        logger.error("Missing PEXELS_API_KEY")
        return []

    headers = {"Authorization": pexels_key}
    base_url = "https://api.pexels.com/v1/search"
    downloaded = []
    used_ids = set()

    for i, prompt in enumerate(prompts[:10]):
        # Clean prompt for Pexels search (remove long descriptive fluff, keep core subject)
        # Brain 3 prompts are like "Hyper-realistic cinematic photography of a shocked indian man"
        # We simplify it for Pexels search.
        clean_query = prompt.replace("Hyper-realistic cinematic photography of", "").replace("8k resolution", "").replace("photorealistic", "").strip()
        # Take the first 5 words to ensure broad enough search
        search_query = " ".join(clean_query.split()[:6])
        
        logger.info(f"[{i+1}/10] Fetching Photo: '{search_query}'")
        params = {"query": search_query, "orientation": "portrait", "per_page": 5}
        
        try:
            resp = requests.get(base_url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            photos = resp.json().get("photos", [])
            
            if not photos:
                logger.warning(f"  No photo found for '{search_query}'.")
                continue

            # Pick first non-duplicate photo
            selected = None
            for p in photos:
                if p["id"] not in used_ids:
                    selected = p
                    used_ids.add(p["id"])
                    break
            if not selected:
                selected = photos[0]

            # Fetch the highest quality portrait version
            download_url = selected["src"]["portrait"]
            img_path = f"ai_image_{i}.jpg"
            
            logger.info(f"  Downloading image...")
            vr = requests.get(download_url, stream=True, timeout=30)
            vr.raise_for_status()
            with open(img_path, "wb") as out:
                for chunk in vr.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        out.write(chunk)
            downloaded.append(img_path)
            
        except Exception as e:
            logger.error(f"  Photo fetch failed: {e}")
            
    return downloaded


# ──────────────────────────────────────────────────────────
# PARALLAX MOTION (Ken Burns)
# ──────────────────────────────────────────────────────────

def convert_image_to_parallax_video(img_src, dst, duration_s):
    """
    Converts a static AI image into a cinematic moving video using FFmpeg zoompan.
    Slow zoom-in from 1.0 to 1.08 over the clip duration.
    """
    total_frames = int(duration_s * TARGET_FPS)
    zoom_expr = f"'min(zoom+0.001,1.08)'"
    x_expr = "iw/2-(iw/zoom/2)"
    y_expr = "ih/2-(ih/zoom/2)"

    vf = (
        f"zoompan=z={zoom_expr}:x={x_expr}:y={y_expr}"
        f":d={total_frames}:s={TARGET_W}x{TARGET_H}:fps={TARGET_FPS},"
        f"setsar=1"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", img_src,
        "-t", str(duration_s),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        dst
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        logger.error(f"Parallax motion failed for {img_src}: {e}")
        return False


# ──────────────────────────────────────────────────────────
# XFADE CHAIN & AUDIO FX
# ──────────────────────────────────────────────────────────

def get_clip_duration(clip_path):
    cmd = ["ffprobe", "-i", clip_path, "-show_entries", "format=duration",
           "-v", "quiet", "-of", "csv=p=0"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(r.stdout.strip())
    except: return 3.5

def build_xfade_chain(norm_clips, target_duration):
    n = len(norm_clips)
    if n == 1:
        out = "stitched_broll.mp4"
        subprocess.run(["ffmpeg", "-y", "-i", norm_clips[0], "-t", str(target_duration), "-c", "copy", out], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out, []

    clip_durations = [get_clip_duration(c) for c in norm_clips]
    filter_parts = []
    prev_label = "[0:v]"
    cumulative = 0.0
    transition_times = []

    for i in range(1, n):
        cumulative += clip_durations[i - 1] - XFADE_DURATION
        offset = max(0.01, cumulative)
        transition_times.append(offset)
        curr_label = f"[xf{i}]"
        filter_parts.append(f"{prev_label}[{i}:v]xfade=transition=fade:duration={XFADE_DURATION}:offset={offset:.4f}{curr_label}")
        prev_label = curr_label

    input_args = []
    for c in norm_clips:
        input_args.extend(["-i", c])

    stitched = "stitched_broll.mp4"
    cmd = [
        "ffmpeg", "-y", *input_args,
        "-filter_complex", ";".join(filter_parts),
        "-map", prev_label,
        "-t", str(target_duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p", stitched
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Seamless xfade chain → '{stitched}'")
        return stitched, transition_times
    except Exception as e:
        logger.warning(f"xfade failed: {e}. Fallback to hard cut.")
        with open("clips.txt", "w") as f:
            for c in norm_clips: f.write(f"file '{c}'\n")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "clips.txt", "-t", str(target_duration), "-c", "copy", stitched], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return stitched, []

def fetch_audio_assets():
    if not os.path.exists(BG_MUSIC_FILE):
        for url in MUSIC_URLS:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=20) as r, open(BG_MUSIC_FILE, "wb") as o:
                    o.write(r.read())
                break
            except: pass
    if not os.path.exists(WHOOSH_FILE):
        try:
            req = urllib.request.Request(WHOOSH_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r, open(WHOOSH_FILE, "wb") as o:
                o.write(r.read())
        except: pass

def build_sfx_audio(transition_times, total_duration):
    """Layers a whoosh sound effect at every transition time."""
    if not os.path.exists(WHOOSH_FILE) or not transition_times:
        return None
    
    filter_parts = []
    inputs = []
    for i, t in enumerate(transition_times):
        inputs.extend(["-i", WHOOSH_FILE])
        filter_parts.append(f"[{i}:a]adelay={int(t*1000)}|{int(t*1000)}[w{i}]")
    
    amix_inputs = "".join([f"[w{i}]" for i in range(len(transition_times))])
    filter_parts.append(f"{amix_inputs}amix=inputs={len(transition_times)}:dropout_transition=0:normalize=0[sfx_out]")
    
    out_sfx = "sfx_track.wav"
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filter_parts), "-map", "[sfx_out]", out_sfx]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out_sfx
    except: return None


# ──────────────────────────────────────────────────────────
# FINAL COMPILE
# ──────────────────────────────────────────────────────────

def compile_final_reel(broll_video, transition_times, thumbnail_text=""):
    temp = "temp_merged.mp4"
    fetch_audio_assets()
    sfx_track = build_sfx_audio(transition_times, 60)

    # Audio Mixing: Voice (1.0), Music (0.12), SFX (0.5)
    cmd = ["ffmpeg", "-y", "-i", broll_video, "-i", AUDIO_INPUT]
    
    has_music = os.path.exists(BG_MUSIC_FILE) and os.path.getsize(BG_MUSIC_FILE) > 1000
    has_sfx = sfx_track and os.path.exists(sfx_track)

    audio_inputs = "[1:a]volume=1.0[voice];"
    mix_elements = "[voice]"
    mix_count = 1

    if has_music:
        cmd.extend(["-stream_loop", "-1", "-i", BG_MUSIC_FILE])
        audio_inputs += "[2:a]volume=0.12[bg];"
        mix_elements += "[bg]"
        mix_count += 1
    
    if has_sfx:
        sfx_idx = 3 if has_music else 2
        cmd.extend(["-i", sfx_track])
        audio_inputs += f"[{sfx_idx}:a]volume=0.5[sfx];"
        mix_elements += "[sfx]"
        mix_count += 1

    fc = f"{audio_inputs}{mix_elements}amix=inputs={mix_count}:duration=first:dropout_transition=3[a_out]"
    
    # Cinematic Grade
    fc = f"[0:v]eq=contrast=1.05:saturation=1.1,vignette=PI/6[v_out];" + fc

    cmd.extend([
        "-filter_complex", fc, "-map", "[v_out]", "-map", "[a_out]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-b:v", "8M",
        "-r", str(TARGET_FPS), "-c:a", "aac", "-b:a", "192k", "-shortest", temp
    ])

    logger.info("Merging audio, music, and SFX...")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # HORMOZI SUBTITLES: Big, Yellow, Bold, Thick Black Outline, Centered
    logger.info("Burning Hormozi-style kinetic typography...")
    style = (
        "Alignment=2,Fontname=Arial,Fontsize=30,Bold=-1,"
        "PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,"  # Cyan-Yellow format in ASS is AABBGGRR -> 00FFFF is pure Yellow
        "Outline=5,Shadow=3,BorderStyle=1,MarginV=120"
    )
    srt_rel = os.path.basename(SRT_INPUT)

    cmd_subs = [
        "ffmpeg", "-y", "-i", temp,
        "-vf", f"subtitles={srt_rel}:force_style='{style}'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-b:v", "8M",
        "-r", str(TARGET_FPS), "-c:a", "copy", "-movflags", "+faststart", FINAL_REEL
    ]
    try:
        subprocess.run(cmd_subs, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=os.getcwd())
        logger.info(f"✅ FINAL AI DOCUMENTARY READY: '{FINAL_REEL}'")
    except Exception as e:
        logger.warning(f"Subtitle burn failed ({e}).")
        import shutil
        shutil.copy(temp, FINAL_REEL)

    cleanup_temp_files()

def cleanup_temp_files():
    kill_prefixes = ["raw_clip_", "norm_clip_", "ai_image_", "clips.txt",
                     "stitched_broll.mp4", "temp_merged.mp4", "thumbnail.ass", "sfx_track.wav"]
    for fname in os.listdir("."):
        for p in kill_prefixes:
            if fname.startswith(p):
                try: os.remove(fname)
                except: pass

def render():
    if not os.path.exists(SCRIPT_INPUT): return
    with open(SCRIPT_INPUT, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    total_duration = get_audio_duration()
    prompts = script_data.get("ai_image_prompts", [])
    
    if not prompts:
        logger.error("No AI image prompts found.")
        return

    # 1. Fetch AI Images
    images = fetch_ai_images(prompts)
    if not images: return

    # 2. Timing
    clip_durations = calculate_srt_segment_durations(len(images), total_duration)

    # 3. Apply Ken Burns Parallax
    norm_clips = []
    for i, (img, dur) in enumerate(zip(images, clip_durations)):
        dst = f"norm_clip_{i}.mp4"
        logger.info(f"Parallax rendering clip {i+1}/{len(images)} → {dur:.2f}s")
        if convert_image_to_parallax_video(img, dst, dur):
            norm_clips.append(dst)

    # 4. Stitch with Xfade
    broll, transition_times = build_xfade_chain(norm_clips, total_duration)

    # 5. Compile with Hormozi subs + SFX
    compile_final_reel(broll, transition_times, script_data.get("thumbnail_text", ""))

if __name__ == "__main__":
    render()
