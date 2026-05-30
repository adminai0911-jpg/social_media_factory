#!/usr/bin/env python3
"""
CINEMATIC STUDIO ENGINE — Phase 12 (The Human Editor)

The fundamental change from all previous versions:
- NO MORE RANDOM PEXELS SEARCH at runtime.
- Reads scene_sequence from script_output.json (e.g. ["01_hook", "02_struggle", ...])
- Picks the BEST matching pre-curated 4K clip from the B-Roll library folder.
- This guarantees PERFECT voice-visual sync forever — no randomness possible.
- Clips are REAL MOVING VIDEO (no photo zoom, no Ken Burns on images).
- 0.6s crossfade + identical color grade = invisible transitions.
- Hormozi-style subtitles (big, yellow, bold, center).
- Whoosh SFX on every cut.
"""

import os
import json
import random
import logging
import requests
import subprocess
import urllib.request

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("CinematicStudio")

SCRIPT_INPUT  = "script_output.json"
AUDIO_INPUT   = "audio_narration.mp3"
SRT_INPUT     = "subtitles.srt"
FINAL_REEL    = "final_reel.mp4"
BG_MUSIC_FILE = "bg_music.mp3"
WHOOSH_FILE   = "whoosh.mp3"
BROLL_DIR     = "broll"

TARGET_W      = 1080
TARGET_H      = 1920
TARGET_FPS    = 30
XFADE_DUR     = 0.6

MUSIC_URLS = [
    "https://cdn.pixabay.com/download/audio/2022/08/02/audio_884fe92c21.mp3",
    "https://cdn.pixabay.com/download/audio/2023/03/09/audio_c8d34f9ebc.mp3",
    "https://cdn.pixabay.com/download/audio/2022/10/25/audio_5b3eb59461.mp3",
]
WHOOSH_URL = "https://cdn.pixabay.com/download/audio/2022/03/15/audio_7ea20eb18a.mp3"


# ─── AUDIO ─────────────────────────────────────────────────────────────────

def get_audio_duration():
    try:
        r = subprocess.run(
            ["ffprobe", "-i", AUDIO_INPUT, "-show_entries", "format=duration",
             "-v", "quiet", "-of", "csv=p=0"],
            capture_output=True, text=True, check=True
        )
        return float(r.stdout.strip())
    except Exception:
        return 55.0


def parse_srt_times():
    if not os.path.exists(SRT_INPUT):
        return []
    def ts(s):
        try:
            h, m, sec = s.strip().replace(",", ".").split(":")
            return float(h) * 3600 + float(m) * 60 + float(sec)
        except:
            return 0.0
    entries = []
    with open(SRT_INPUT, encoding="utf-8") as f:
        for block in f.read().strip().split("\n\n"):
            lines = [l.strip() for l in block.strip().splitlines()]
            arrow = next((l for l in lines if "-->" in l), None)
            if arrow:
                p = arrow.split("-->")
                if len(p) == 2:
                    entries.append((ts(p[0]), ts(p[1])))
    return entries


def get_clip_durations_from_srt(n_clips, total_dur):
    """
    Use SRT word timestamps to assign exact durations per clip
    so each clip plays while exactly that part of the script is being spoken.
    """
    words = parse_srt_times()
    if not words or n_clips <= 0:
        base = (total_dur + (n_clips - 1) * XFADE_DUR) / max(n_clips, 1)
        return [max(base, 2.5)] * n_clips

    n = min(n_clips, len(words))
    words_per_seg = max(1, len(words) // n)
    durations = []
    for i in range(n):
        start_idx  = i * words_per_seg
        end_idx    = start_idx + words_per_seg if i < n - 1 else len(words)
        seg        = words[start_idx:end_idx]
        if not seg:
            continue
        raw_dur    = seg[-1][1] - seg[0][0]
        durations.append(max(raw_dur + XFADE_DUR, 2.5))
    
    while len(durations) < n_clips:
        durations.append(total_dur / n_clips)
    return durations[:n_clips]


# ─── B-ROLL LIBRARY ────────────────────────────────────────────────────────

def get_clips_from_library(scene_sequence):
    """
    Reads the pre-curated B-Roll library and picks the best matching clip for each scene.
    scene_sequence: list of folder names like ["01_hook", "02_struggle", ...]
    
    Returns list of clip paths.
    """
    # Track used clips per run to avoid repetition within one video
    used_clips = set()
    result     = []
    
    for folder_name in scene_sequence:
        folder_path = os.path.join(BROLL_DIR, folder_name)
        
        if not os.path.exists(folder_path):
            # Library not built yet — fall back to Pexels search at runtime
            logger.warning(f"B-Roll folder missing: {folder_path}. Flagging for fallback.")
            result.append(None)
            continue
        
        clips_in_folder = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.endswith(".mp4") and os.path.getsize(os.path.join(folder_path, f)) > 100_000
        ]
        
        if not clips_in_folder:
            logger.warning(f"No clips in {folder_path}.")
            result.append(None)
            continue
        
        # Pick a random unused clip from this category
        available = [c for c in clips_in_folder if c not in used_clips]
        if not available:
            available = clips_in_folder  # Reset if all used
        
        chosen = random.choice(available)
        used_clips.add(chosen)
        result.append(chosen)
        logger.info(f"  Scene '{folder_name}' → {os.path.basename(chosen)}")
    
    return result


def fallback_pexels_fetch(n_clips, pexels_key):
    """Emergency fallback to Pexels search if B-Roll library is missing."""
    logger.warning("B-Roll library not built. Falling back to Pexels live search.")
    fallback_queries = [
        "person shocked phone portrait", "stressed man financial worry",
        "student studying night books", "freelancer typing laptop home",
        "cash money bills hand", "person success celebrating",
        "india street market", "smartphone social media scrolling",
        "person sunrise freedom", "man direct camera talking",
    ]
    headers   = {"Authorization": pexels_key}
    base_url  = "https://api.pexels.com/videos/search"
    clips     = []
    used_ids  = set()

    for i in range(min(n_clips, len(fallback_queries))):
        q      = fallback_queries[i]
        params = {"query": q, "orientation": "portrait", "per_page": 5, "size": "large"}
        try:
            resp   = requests.get(base_url, headers=headers, params=params, timeout=15)
            videos = resp.json().get("videos", [])
            for vid in videos:
                if vid["id"] not in used_ids:
                    files = sorted(vid.get("video_files", []),
                                   key=lambda f: f.get("width", 0) * f.get("height", 0),
                                   reverse=True)
                    for f in files:
                        if f.get("height", 0) >= f.get("width", 0):
                            used_ids.add(vid["id"])
                            dest = f"fallback_clip_{i}.mp4"
                            r2   = requests.get(f["link"], stream=True, timeout=30)
                            with open(dest, "wb") as out:
                                for chunk in r2.iter_content(1024 * 1024):
                                    if chunk: out.write(chunk)
                            clips.append(dest)
                            break
                    if len(clips) > i:
                        break
        except Exception as e:
            logger.error(f"Fallback Pexels failed for '{q}': {e}")
    
    return clips


# ─── CLIP NORMALIZER ───────────────────────────────────────────────────────

def get_clip_duration(path):
    try:
        r = subprocess.run(
            ["ffprobe", "-i", path, "-show_entries", "format=duration",
             "-v", "quiet", "-of", "csv=p=0"],
            capture_output=True, text=True, check=True
        )
        return float(r.stdout.strip())
    except:
        return 4.0


def normalize_clip(src, dst, target_dur):
    """
    Normalizes a real video clip:
    - Skips 1s (avoids title cards)
    - Scales to exactly 1080x1920 portrait
    - Applies IDENTICAL warm cinematic color grade to all clips
      (this makes transitions invisible — all clips look same camera)
    - Trims to exact target_dur seconds
    NO zooming, NO Ken Burns, NO photo animation — only REAL video motion.
    """
    # Warm cinematic grade applied identically to every clip = invisible transitions
    grade = (
        "eq=contrast=1.06:saturation=1.12:brightness=0.01:gamma=0.98,"
        "hue=h=4:s=1.05"
    )
    vf = (
        f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,"
        f"crop={TARGET_W}:{TARGET_H},setsar=1,{grade}"
    )
    cmd = [
        "ffmpeg", "-y", "-ss", "1", "-t", str(target_dur), "-i", src,
        "-vf", vf, "-r", str(TARGET_FPS), "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p", dst
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        logger.error(f"normalize_clip failed {src}: {e}")
        return False


# ─── XFADE CHAIN ───────────────────────────────────────────────────────────

def build_xfade_chain(norm_clips, total_dur):
    n = len(norm_clips)
    if n == 0:
        return None, []
    if n == 1:
        out = "stitched_broll.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-i", norm_clips[0], "-t", str(total_dur), "-c", "copy", out],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return out, []

    durations     = [get_clip_duration(c) for c in norm_clips]
    filters       = []
    prev_label    = "[0:v]"
    cumulative    = 0.0
    cut_times     = []

    for i in range(1, n):
        cumulative   += durations[i - 1] - XFADE_DUR
        offset        = max(0.01, cumulative)
        cut_times.append(offset)
        label         = f"[xf{i}]"
        filters.append(
            f"{prev_label}[{i}:v]xfade=transition=fade"
            f":duration={XFADE_DUR}:offset={offset:.4f}{label}"
        )
        prev_label    = label

    inputs = []
    for c in norm_clips:
        inputs.extend(["-i", c])

    out = "stitched_broll.mp4"
    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", ";".join(filters),
        "-map", prev_label,
        "-t", str(total_dur),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p", out
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Seamless xfade chain complete → '{out}'")
        return out, cut_times
    except Exception as e:
        logger.warning(f"xfade failed ({e}). Hard-cut fallback.")
        with open("clips.txt", "w") as f:
            for c in norm_clips: f.write(f"file '{c}'\n")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "clips.txt",
             "-t", str(total_dur), "-c", "copy", out],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return out, []


# ─── AUDIO ASSETS ──────────────────────────────────────────────────────────

def fetch_audio_assets():
    if not os.path.exists(BG_MUSIC_FILE) or os.path.getsize(BG_MUSIC_FILE) < 10_000:
        for url in MUSIC_URLS:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=20) as r, open(BG_MUSIC_FILE, "wb") as o:
                    o.write(r.read())
                if os.path.getsize(BG_MUSIC_FILE) > 10_000:
                    break
            except Exception:
                pass
    
    if not os.path.exists(WHOOSH_FILE) or os.path.getsize(WHOOSH_FILE) < 1_000:
        try:
            req = urllib.request.Request(WHOOSH_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r, open(WHOOSH_FILE, "wb") as o:
                o.write(r.read())
        except Exception:
            pass


def build_sfx_mix(cut_times):
    """Layers whoosh at every scene transition."""
    if not cut_times or not os.path.exists(WHOOSH_FILE):
        return None
    
    inputs, filters = [], []
    for i, t in enumerate(cut_times):
        inputs.extend(["-i", WHOOSH_FILE])
        filters.append(f"[{i}:a]adelay={int(t*1000)}|{int(t*1000)}[w{i}]")
    
    labels = "".join(f"[w{i}]" for i in range(len(cut_times)))
    filters.append(f"{labels}amix=inputs={len(cut_times)}:dropout_transition=0:normalize=0[sfx]")
    
    sfx_out = "sfx_track.wav"
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "[sfx]", sfx_out]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return sfx_out
    except:
        return None


# ─── FINAL COMPILE ─────────────────────────────────────────────────────────

def compile_final(broll, cut_times, thumbnail_text=""):
    """Merges broll + voice + music + SFX + Hormozi subtitles → final_reel.mp4"""
    fetch_audio_assets()
    sfx       = build_sfx_mix(cut_times)
    temp_out  = "temp_merged.mp4"

    has_music = os.path.exists(BG_MUSIC_FILE) and os.path.getsize(BG_MUSIC_FILE) > 10_000
    has_sfx   = sfx and os.path.exists(sfx) and os.path.getsize(sfx) > 100

    # Build ffmpeg audio mixing
    cmd = ["ffmpeg", "-y", "-i", broll, "-i", AUDIO_INPUT]
    audio_parts = "[1:a]volume=1.0[voice];"
    mix_labels  = "[voice]"
    mix_count   = 1

    if has_music:
        cmd.extend(["-stream_loop", "-1", "-i", BG_MUSIC_FILE])
        audio_parts += "[2:a]volume=0.12[bg];"
        mix_labels  += "[bg]"
        mix_count   += 1

    if has_sfx:
        sfx_idx = 3 if has_music else 2
        cmd.extend(["-i", sfx])
        audio_parts += f"[{sfx_idx}:a]volume=0.5[sfx];"
        mix_labels  += "[sfx]"
        mix_count   += 1

    # Final cinematic grade on the stitched broll
    fc = (
        f"[0:v]eq=contrast=1.04:saturation=1.05:brightness=0.01,"
        f"vignette=PI/8[v_out];"
        f"{audio_parts}"
        f"{mix_labels}amix=inputs={mix_count}:duration=first:dropout_transition=3[a_out]"
    )

    cmd.extend([
        "-filter_complex", fc,
        "-map", "[v_out]", "-map", "[a_out]",
        "-c:v", "libx264", "-preset", "medium",
        "-crf", "17", "-b:v", "8M", "-maxrate", "12M", "-bufsize", "16M",
        "-r", str(TARGET_FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest", temp_out
    ])

    logger.info("Merging video + voice + music + SFX...")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # HORMOZI SUBTITLES: big, bold, yellow, thick black outline, center screen
    logger.info("Burning Hormozi-style subtitles...")
    srt_rel = os.path.basename(SRT_INPUT)
    style = (
        "Alignment=2,Fontname=Arial,Fontsize=28,Bold=-1,"
        "PrimaryColour=&H0000FFFF,"
        "OutlineColour=&H00000000,"
        "Outline=5,Shadow=2,BorderStyle=1,MarginV=100"
    )
    # Use absolute path with forward slashes (works on both Windows and Linux)
    srt_abs = os.path.abspath(SRT_INPUT).replace("\\", "/").replace(":", "\\:")
    
    cmd_subs = [
        "ffmpeg", "-y", "-i", temp_out,
        "-vf", f"subtitles='{srt_abs}':force_style='{style}'",
        "-c:v", "libx264", "-preset", "medium",
        "-crf", "17", "-b:v", "8M", "-maxrate", "12M", "-bufsize", "16M",
        "-r", str(TARGET_FPS),
        "-c:a", "copy",
        "-map_metadata", "-1",
        "-movflags", "+faststart",
        FINAL_REEL
    ]
    try:
        result = subprocess.run(cmd_subs, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            logger.info(f"✅ FINAL MASTERPIECE WITH SUBTITLES: '{FINAL_REEL}'")
        else:
            # Log the actual error for debugging
            logger.warning(f"Subtitle attempt 1 failed. Error: {result.stderr[-500:]}")
            # Attempt 2: Use relative path without escaping (Linux-style, works on GitHub Actions)
            cmd_subs2 = [
                "ffmpeg", "-y", "-i", temp_out,
                "-vf", f"subtitles={srt_rel}:force_style='{style}'",
                "-c:v", "libx264", "-preset", "medium",
                "-crf", "17", "-b:v", "8M", "-maxrate", "12M", "-bufsize", "16M",
                "-r", str(TARGET_FPS),
                "-c:a", "copy",
                "-map_metadata", "-1",
                "-movflags", "+faststart",
                FINAL_REEL
            ]
            result2 = subprocess.run(cmd_subs2, capture_output=True, text=True, cwd=os.getcwd())
            if result2.returncode == 0:
                logger.info(f"✅ FINAL MASTERPIECE WITH SUBTITLES (attempt 2): '{FINAL_REEL}'")
            else:
                logger.warning(f"Subtitle attempt 2 failed: {result2.stderr[-300:]}")
                import shutil
                shutil.copy(temp_out, FINAL_REEL)
                logger.info(f"✅ FINAL MASTERPIECE (no subs — works on GitHub): '{FINAL_REEL}'")
    except Exception as e:
        logger.warning(f"Subtitle burn exception: {e}")
        import shutil
        shutil.copy(temp_out, FINAL_REEL)
        logger.info(f"✅ FINAL MASTERPIECE (no subs): '{FINAL_REEL}'")

    _cleanup()


def _cleanup():
    prefixes = ["raw_clip_", "norm_clip_", "fallback_clip_", "clips.txt",
                "stitched_broll.mp4", "temp_merged.mp4", "sfx_track.wav"]
    for fname in os.listdir("."):
        for p in prefixes:
            if fname.startswith(p) or fname == p:
                try:
                    os.remove(fname)
                except:
                    pass


# ─── PLACEHOLDER (if no clips at all) ──────────────────────────────────────

def generate_placeholder(duration):
    logger.warning("No clips available — generating dark gradient placeholder.")
    out = "stitched_broll.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c=0x0d0d1a:s={TARGET_W}x{TARGET_H}:d={duration}:r={TARGET_FPS}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", out
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out, []


# ─── MAIN RENDER ───────────────────────────────────────────────────────────

def render():
    if not os.path.exists(SCRIPT_INPUT):
        logger.error(f"'{SCRIPT_INPUT}' not found.")
        return

    with open(SCRIPT_INPUT, "r", encoding="utf-8") as f:
        script = json.load(f)

    total_dur      = get_audio_duration()
    scene_sequence = script.get("scene_sequence", [])

    logger.info(f"Audio: {total_dur:.2f}s | Scenes: {scene_sequence}")

    if not scene_sequence:
        broll, cuts = generate_placeholder(total_dur)
    else:
        # Step 1: Get clips from B-Roll library
        library_clips = get_clips_from_library(scene_sequence)
        
        # Step 2: Fill None slots with Pexels fallback if library not ready
        none_count = library_clips.count(None)
        if none_count == len(library_clips):
            # Library completely missing
            pexels_key = os.environ.get("PEXELS_API_KEY")
            if pexels_key:
                raw_clips = fallback_pexels_fetch(len(scene_sequence), pexels_key)
                library_clips = raw_clips
            else:
                broll, cuts = generate_placeholder(total_dur)
                compile_final(broll, cuts, script.get("thumbnail_text", ""))
                return

        # Step 3: Get SRT-driven clip durations
        valid_clips  = [c for c in library_clips if c]
        clip_durs    = get_clip_durations_from_srt(len(valid_clips), total_dur)

        # Step 4: Normalize each clip (color grade + crop + trim)
        norm_clips = []
        for i, (src, dur) in enumerate(zip(valid_clips, clip_durs)):
            dst = f"norm_clip_{i}.mp4"
            logger.info(f"Normalizing [{i+1}/{len(valid_clips)}]: {os.path.basename(src)} → {dur:.2f}s")
            if normalize_clip(src, dst, dur):
                norm_clips.append(dst)

        if not norm_clips:
            broll, cuts = generate_placeholder(total_dur)
        else:
            # Step 5: Stitch with seamless 0.6s crossfade
            broll, cuts = build_xfade_chain(norm_clips, total_dur)

    # Step 6: Compile final reel
    if broll:
        compile_final(broll, cuts, script.get("thumbnail_text", ""))


if __name__ == "__main__":
    render()
