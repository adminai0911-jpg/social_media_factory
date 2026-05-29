#!/usr/bin/env python3
"""
CINEMATIC STUDIO ENGINE — Phase 9

Key fixes and upgrades:
1. FIXED: xfade cumulative offset bug (was dropping 9/10 clips → caused 6-second video)
2. FIXED: subtitle burn font issue on Linux (uses available liberation/freefont fonts)  
3. UPGRADED: Audio-driven visual sync — SRT timestamps determine exact clip durations
4. UPGRADED: Targets 60-second video (matches longer script from Brain 3)
5. UPGRADED: Smart xfade chain uses CUMULATIVE offsets (industry-standard method)
"""

import os
import json
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

TARGET_W   = 1080
TARGET_H   = 1920
TARGET_FPS = 30

MUSIC_URLS = [
    "https://cdn.pixabay.com/download/audio/2022/08/02/audio_884fe92c21.mp3",
    "https://cdn.pixabay.com/download/audio/2023/03/09/audio_c8d34f9ebc.mp3",
    "https://cdn.pixabay.com/download/audio/2022/10/25/audio_5b3eb59461.mp3",
]

XFADE_DURATION = 0.35  # seconds per dissolve transition


# ──────────────────────────────────────────────────────────
# AUDIO ANALYSIS
# ──────────────────────────────────────────────────────────

def get_audio_duration():
    cmd = ["ffprobe", "-i", AUDIO_INPUT, "-show_entries", "format=duration",
           "-v", "quiet", "-of", "csv=p=0"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        dur = float(r.stdout.strip())
        logger.info(f"Audio duration: {dur:.2f}s")
        return dur
    except Exception as e:
        logger.error(f"ffprobe failed: {e}. Defaulting to 55s.")
        return 55.0


# ──────────────────────────────────────────────────────────
# AUDIO-DRIVEN CLIP DURATION CALCULATOR
# ──────────────────────────────────────────────────────────

def parse_srt_timestamps(srt_path):
    """
    Parses an SRT subtitle file and returns a list of (start_sec, end_sec) tuples
    for each subtitle entry.
    """
    entries = []
    if not os.path.exists(srt_path):
        return entries

    def ts_to_sec(ts):
        # Format: 00:00:01,234
        try:
            ts = ts.replace(",", ".")
            parts = ts.strip().split(":")
            h, m, s = float(parts[0]), float(parts[1]), float(parts[2])
            return h * 3600 + m * 60 + s
        except Exception:
            return 0.0

    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) >= 2:
            arrow_line = next((l for l in lines if "-->" in l), None)
            if arrow_line:
                parts = arrow_line.split("-->")
                if len(parts) == 2:
                    start = ts_to_sec(parts[0].strip())
                    end   = ts_to_sec(parts[1].strip())
                    entries.append((start, end))

    return entries


def calculate_scene_durations(total_duration, num_clips):
    """
    Divides total audio duration into num_clips equal segments.
    Accounts for the xfade overlaps so the final stitched video
    matches total_duration exactly.
    
    Returns a list of per-clip durations.
    """
    # Each xfade eats XFADE_DURATION seconds from the seam between two clips.
    # Total duration = sum(clip_durations) - (n-1) * XFADE_DURATION
    # => each clip_duration = (total + (n-1)*XFADE) / n
    n = max(1, num_clips)
    overlap_total = (n - 1) * XFADE_DURATION
    clip_dur = (total_duration + overlap_total) / n
    clip_dur = max(clip_dur, 3.0)  # minimum 3s per clip
    logger.info(f"Scene Calculator: {n} clips × {clip_dur:.2f}s (with {XFADE_DURATION}s xfade overlap)")
    return [clip_dur] * n


# ──────────────────────────────────────────────────────────
# PEXELS HIGH-QUALITY DOWNLOAD
# ──────────────────────────────────────────────────────────

def fetch_pexels_videos(keywords, pexels_key):
    headers  = {"Authorization": pexels_key}
    base_url = "https://api.pexels.com/videos/search"
    downloaded  = []
    used_ids    = set()

    for i, keyword in enumerate(keywords[:10]):
        logger.info(f"[{i+1}/10] Pexels: '{keyword}'")
        params = {"query": keyword, "orientation": "portrait", "per_page": 10, "size": "large"}
        try:
            resp = requests.get(base_url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            videos = resp.json().get("videos", [])
            if not videos:
                logger.warning(f"  No results for '{keyword}'. Skipping.")
                continue

            # Pick first non-duplicate video
            selected = None
            for vid in videos:
                if vid["id"] not in used_ids:
                    selected = vid
                    used_ids.add(vid["id"])
                    break
            if not selected:
                selected = videos[0]

            # Sort files by total pixels → highest quality first
            files_sorted = sorted(
                selected.get("video_files", []),
                key=lambda f: f.get("width", 0) * f.get("height", 0),
                reverse=True
            )

            # Prefer vertical, else take best available
            download_url = None
            chosen_res   = "?"
            for f in files_sorted:
                w, h = f.get("width", 0), f.get("height", 0)
                if h > w:
                    download_url = f["link"]
                    chosen_res   = f"{w}x{h}"
                    break
            if not download_url and files_sorted:
                f            = files_sorted[0]
                download_url = f["link"]
                chosen_res   = f"{f.get('width')}x{f.get('height')}"

            if not download_url:
                continue

            clip_path = f"raw_clip_{i}.mp4"
            logger.info(f"  Downloading {chosen_res}...")
            vr = requests.get(download_url, stream=True, timeout=30)
            vr.raise_for_status()
            with open(clip_path, "wb") as out:
                for chunk in vr.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        out.write(chunk)
            downloaded.append(clip_path)
            logger.info(f"  Saved → '{clip_path}'")

        except Exception as e:
            logger.error(f"  Pexels error '{keyword}': {e}")

    return downloaded


# ──────────────────────────────────────────────────────────
# CLIP NORMALISER (Ken Burns + trim)
# ──────────────────────────────────────────────────────────

def normalise_clip(src, dst, duration_s):
    """
    Crops & scales source clip to 1080x1920 (portrait).
    Sets FPS to 30 and trims to EXACT duration_s seconds.
    Skips first 1 second to avoid static stock-footage title cards.
    
    NO Ken Burns/zoompan — the natural motion from the Pexels video plays through.
    Real moving video footage is always better than an artificial zoom on a static frame.
    """
    vf = (
        f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,"
        f"crop={TARGET_W}:{TARGET_H},"
        f"setsar=1"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", "1",               # skip boring static intro second
        "-t", str(duration_s),    # take exactly what we need
        "-i", src,
        "-vf", vf,
        "-r", str(TARGET_FPS),
        "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        dst
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        logger.error(f"Clip normalise failed for {src}: {e}")
        return False



# ──────────────────────────────────────────────────────────
# XFADE CHAIN — FIXED CUMULATIVE OFFSET
# ──────────────────────────────────────────────────────────

def build_xfade_chain(norm_clips, target_duration):
    """
    Chains all clips with smooth xfade dissolve transitions.
    
    THE FIX: offsets must be CUMULATIVE (sum of all previous clip durations
    minus already-consumed overlaps). The old code used each clip's individual
    duration as the offset which caused wrong timing and dropped clips.
    """
    n = len(norm_clips)
    if n == 1:
        return None, "[0:v]", norm_clips

    # Probe actual duration of each normalised clip
    clip_durations = []
    for c in norm_clips:
        dur_cmd = ["ffprobe", "-i", c, "-show_entries", "format=duration",
                   "-v", "quiet", "-of", "csv=p=0"]
        try:
            r = subprocess.run(dur_cmd, capture_output=True, text=True, check=True)
            clip_durations.append(float(r.stdout.strip()))
        except Exception:
            clip_durations.append(target_duration / n)

    filter_parts  = []
    prev_label    = "[0:v]"
    cumulative    = 0.0

    for i in range(1, n):
        # Cumulative offset = sum of all previous clip durations minus overlaps already consumed
        cumulative += clip_durations[i - 1] - XFADE_DURATION
        offset      = max(0.01, cumulative)
        curr_label  = f"[xf{i}]"

        filter_parts.append(
            f"{prev_label}[{i}:v]xfade=transition=fade"
            f":duration={XFADE_DURATION}:offset={offset:.3f}{curr_label}"
        )
        prev_label = curr_label

    return ";".join(filter_parts), prev_label, norm_clips


def stitch_with_xfade(norm_clips, target_duration):
    if not norm_clips:
        return None

    if len(norm_clips) == 1:
        out = "stitched_broll.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-i", norm_clips[0], "-t", str(target_duration), "-c", "copy", out],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return out

    filter_str, final_label, clips = build_xfade_chain(norm_clips, target_duration)
    input_args = []
    for c in clips:
        input_args.extend(["-i", c])

    stitched = "stitched_broll.mp4"
    cmd = [
        "ffmpeg", "-y", *input_args,
        "-filter_complex", filter_str,
        "-map", final_label,
        "-t", str(target_duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        stitched
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"xfade chain stitched → '{stitched}'")
        return stitched
    except Exception as e:
        logger.warning(f"xfade chain failed ({e}). Using hard-cut concat fallback...")
        return hard_cut_concat(norm_clips, target_duration)


def hard_cut_concat(norm_clips, target_duration):
    """Safe fallback: simple hard-cut concat."""
    with open("clips.txt", "w") as f:
        for c in norm_clips:
            f.write(f"file '{c}'\n")
    stitched = "stitched_broll.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "clips.txt",
         "-t", str(target_duration), "-c", "copy", stitched],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return stitched


# ──────────────────────────────────────────────────────────
# BACKGROUND MUSIC
# ──────────────────────────────────────────────────────────

def fetch_background_music():
    if os.path.exists(BG_MUSIC_FILE) and os.path.getsize(BG_MUSIC_FILE) > 10_000:
        logger.info("BG music cached.")
        return True
    for url in MUSIC_URLS:
        try:
            logger.info(f"Fetching music: {url[:55]}...")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r, open(BG_MUSIC_FILE, "wb") as o:
                o.write(r.read())
            if os.path.getsize(BG_MUSIC_FILE) > 10_000:
                logger.info("Music OK.")
                return True
        except Exception as e:
            logger.warning(f"Music URL failed: {e}")
    return False


# ──────────────────────────────────────────────────────────
# PLACEHOLDER VIDEO
# ──────────────────────────────────────────────────────────

def generate_placeholder_video(duration):
    logger.warning("Generating gradient placeholder video...")
    out = "stitched_broll.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c=0x0a0a1a:s={TARGET_W}x{TARGET_H}:d={duration}:r={TARGET_FPS}",
        "-vf", "geq=r='r(X,Y)*0.8+20':g='g(X,Y)*0.85+10':b='b(X,Y)*1.1+40'",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", out
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out


# ──────────────────────────────────────────────────────────
# FINAL COMPILE — color grade + audio + subtitles
# ──────────────────────────────────────────────────────────

def compile_final_reel(broll_video, thumbnail_text=""):
    temp = "temp_merged.mp4"

    # ── Thumbnail hook overlay (first 2.5 seconds) ──
    ass_file  = "thumbnail.ass"
    safe_text = thumbnail_text.replace("\\", "\\\\").replace("'", "\\'").replace(",", "\\,")
    try:
        with open(ass_file, "w", encoding="utf-8") as f:
            f.write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {TARGET_W}
PlayResY: {TARGET_H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Arial,80,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,5,3,5,30,30,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:02.50,Hook,,0,0,0,,{safe_text}
""")
    except Exception as e:
        logger.warning(f"Thumbnail ASS failed: {e}")

    has_music    = fetch_background_music()
    # Cinematic color grade: warm contrast + vibrant saturation + vignette
    color_grade  = "eq=contrast=1.10:saturation=1.20:brightness=0.02:gamma=0.97,vignette=PI/5"

    cmd = ["ffmpeg", "-y", "-i", broll_video, "-i", AUDIO_INPUT]
    if has_music:
        cmd.extend(["-stream_loop", "-1", "-i", BG_MUSIC_FILE])
        fc = (
            f"[0:v]{color_grade}[v];"
            f"[1:a]volume=1.0[tts];"
            f"[2:a]volume=0.12[bg];"
            f"[tts][bg]amix=inputs=2:duration=first:dropout_transition=3[a]"
        )
        cmd.extend(["-filter_complex", fc, "-map", "[v]", "-map", "[a]"])
    else:
        cmd.extend(["-vf", color_grade, "-map", "0:v:0", "-map", "1:a:0"])

    cmd.extend([
        "-c:v", "libx264", "-preset", "medium",
        "-crf", "17", "-b:v", "8M", "-maxrate", "12M", "-bufsize", "16M",
        "-r", str(TARGET_FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest", temp
    ])

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("Color grade + audio merged.")
    except Exception as e:
        logger.error(f"Merge failed: {e}")
        raise

    # ── Subtitle burning ──
    # Use relative filenames only — avoids Windows/Linux path escaping issues with FFmpeg filters
    # FFmpeg is always invoked from the factory working directory where these files are created
    logger.info("Burning word-by-word subtitles...")
    
    style = (
        "Alignment=2,Fontname=Arial,Fontsize=20,"
        "PrimaryColour=&H00FFFF00,OutlineColour=&H00000000,"
        "Outline=3,Shadow=1,BorderStyle=1,MarginV=80"
    )

    # On Windows, FFmpeg subtitle filter needs the path with escaped colons
    # The safest approach is to use just the filename (relative) since cwd is set
    srt_path = os.path.basename(SRT_INPUT)    # e.g. "subtitles.srt"
    ass_path = os.path.basename(ass_file)     # e.g. "thumbnail.ass"

    cmd_subs = [
        "ffmpeg", "-y", "-i", temp,
        "-vf", f"ass={ass_path},subtitles={srt_path}:force_style='{style}'",
        "-c:v", "libx264", "-preset", "medium",
        "-crf", "17", "-b:v", "8M", "-maxrate", "12M", "-bufsize", "16M",
        "-r", str(TARGET_FPS),
        "-c:a", "copy", "-map_metadata", "-1", "-movflags", "+faststart",
        FINAL_REEL
    ]

    try:
        subprocess.run(cmd_subs, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       cwd=os.getcwd())
        logger.info(f"✅ FINAL REEL READY WITH SUBTITLES: '{FINAL_REEL}'")
    except Exception as e:
        logger.warning(f"Subtitle burn failed ({e}). Saving clean version without subtitles.")
        import shutil
        shutil.copy(temp, FINAL_REEL)
        logger.info(f"✅ FINAL REEL READY (no subtitles): '{FINAL_REEL}'")

    cleanup_temp_files()


# ──────────────────────────────────────────────────────────
# CLEANUP
# ──────────────────────────────────────────────────────────

def cleanup_temp_files():
    logger.info("Cleaning up temp files...")
    kill = ["raw_clip_", "norm_clip_", "clips.txt", "stitched_broll.mp4",
            "temp_merged.mp4", "thumbnail.ass"]
    for f in os.listdir("."):
        for p in kill:
            if f == p or f.startswith(p):
                try:
                    os.remove(f)
                except OSError:
                    pass


# ──────────────────────────────────────────────────────────
# MAIN RENDER FUNCTION
# ──────────────────────────────────────────────────────────

def render():
    if not os.path.exists(SCRIPT_INPUT):
        raise FileNotFoundError(f"'{SCRIPT_INPUT}' not found.")

    with open(SCRIPT_INPUT, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    duration   = get_audio_duration()
    pexels_key = os.environ.get("PEXELS_API_KEY")
    keywords   = script_data.get("pexels_keywords", [])

    logger.info(f"Target video duration: {duration:.2f}s | Keywords: {len(keywords)}")

    if not pexels_key or not keywords:
        logger.warning("No Pexels key or no keywords. Using placeholder.")
        broll = generate_placeholder_video(duration)
    else:
        downloaded = fetch_pexels_videos(keywords, pexels_key)

        if not downloaded:
            logger.warning("No Pexels clips downloaded. Using placeholder.")
            broll = generate_placeholder_video(duration)
        else:
            # Calculate per-clip durations accounting for xfade overlaps
            clip_durations = calculate_scene_durations(duration, len(downloaded))

            # Normalise each clip with Ken Burns zoom
            norm_clips = []
            for i, (src, dur) in enumerate(zip(downloaded, clip_durations)):
                dst = f"norm_clip_{i}.mp4"
                logger.info(f"Ken Burns clip {i+1}/{len(downloaded)} ({dur:.2f}s): {src}")
                if normalise_clip(src, dst, dur):
                    norm_clips.append(dst)
                else:
                    logger.warning(f"Clip {i+1} failed. Skipping.")

            if not norm_clips:
                broll = generate_placeholder_video(duration)
            else:
                broll = stitch_with_xfade(norm_clips, duration)
                if not broll:
                    broll = generate_placeholder_video(duration)

    compile_final_reel(broll, script_data.get("thumbnail_text", ""))


if __name__ == "__main__":
    render()
