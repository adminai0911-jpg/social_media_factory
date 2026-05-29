#!/usr/bin/env python3
"""
THE CINEMATIC STUDIO ENGINE — Phase 8

Deep Technical Reality:
- Instagram Reels, Facebook Reels, and YouTube Shorts all cap vertical video at 1080x1920.
  Uploading "True 4K" is re-compressed anyway. The REAL quality lever is:
  HIGH BITRATE 1080p (8-12 Mbps) with CRF-quality encoding + cinematic filters.
  This produces crystal-sharp, platform-ready video that looks WAY better than 4K
  that gets mangled by platform compression codecs.

Features:
- Downloads highest-res Pexels source, then normalizes to crisp 1080x1920 FullHD
- Ken Burns cinematic zoom at 1080p (fast render + visually premium)
- Smooth xfade crossfade dissolve transitions between every clip
- Cinematic color grade: warm contrast, vibrant saturation, vignette
- word-by-word yellow subtitle engine with heavy black stroke
- Royalty-free background music mixed at 12% volume (3 CDN fallbacks)
- High-bitrate CRF-17 encoding (visually lossless quality)
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

# Platform target: 1080x1920 @ 30fps (Instagram/Facebook/YouTube Shorts native max)
TARGET_W = 1080
TARGET_H = 1920
TARGET_FPS = 30

# Royalty-free cinematic background music — 3 CDN fallbacks
MUSIC_URLS = [
    "https://cdn.pixabay.com/download/audio/2023/03/09/audio_c8d34f9ebc.mp3",
    "https://cdn.pixabay.com/download/audio/2022/08/02/audio_884fe92c21.mp3",
    "https://cdn.pixabay.com/download/audio/2022/10/25/audio_5b3eb59461.mp3",
]

# Crossfade transition duration in seconds between clips
XFADE_DURATION = 0.4


# ──────────────────────────────────────────────────────────
# STEP 1: Audio Analysis
# ──────────────────────────────────────────────────────────

def get_audio_duration():
    logger.info("Analysing audio duration via ffprobe...")
    cmd = [
        "ffprobe", "-i", AUDIO_INPUT,
        "-show_entries", "format=duration",
        "-v", "quiet", "-of", "csv=p=0"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        dur = float(result.stdout.strip())
        logger.info(f"Audio duration: {dur:.2f}s")
        return dur
    except Exception as e:
        logger.error(f"ffprobe failed: {e}. Using 45s default.")
        return 45.0


# ──────────────────────────────────────────────────────────
# STEP 2: Pexels High-Quality Source Download
# ──────────────────────────────────────────────────────────

def fetch_pexels_videos(keywords, pexels_key):
    """
    For each keyword, queries Pexels and downloads the highest-resolution
    vertical clip available. Tries up to 5 results per keyword to maximise
    variety and avoid duplicates.
    """
    headers   = {"Authorization": pexels_key}
    base_url  = "https://api.pexels.com/videos/search"
    downloaded = []

    used_video_ids = set()  # prevent duplicate downloads

    for i, keyword in enumerate(keywords[:10]):
        logger.info(f"[{i+1}/10] Pexels search: '{keyword}'")
        params = {"query": keyword, "orientation": "portrait", "per_page": 10, "size": "large"}

        try:
            resp = requests.get(base_url, headers=headers, params=params, timeout=15)
            resp.raise_for_status()
            videos = resp.json().get("videos", [])

            if not videos:
                logger.warning(f"  No results for '{keyword}'. Skipping.")
                continue

            selected = None
            for vid in videos:
                if vid["id"] not in used_video_ids:
                    selected = vid
                    used_video_ids.add(vid["id"])
                    break

            if not selected:
                selected = videos[0]  # fallback to first even if duplicate

            # Sort all file variants by total pixels (descending) to get highest quality
            files_sorted = sorted(
                selected.get("video_files", []),
                key=lambda f: f.get("width", 0) * f.get("height", 0),
                reverse=True
            )

            # Prefer a vertical file, otherwise take the highest-res available
            download_url = None
            chosen_res   = "?"
            for f in files_sorted:
                w, h = f.get("width", 0), f.get("height", 0)
                if h > w:
                    download_url = f["link"]
                    chosen_res   = f"{w}x{h}"
                    break
            if not download_url and files_sorted:
                f = files_sorted[0]
                download_url = f["link"]
                chosen_res   = f"{f.get('width')}x{f.get('height')}"

            if not download_url:
                continue

            clip_path = f"raw_clip_{i}.mp4"
            logger.info(f"  Downloading {chosen_res} clip...")
            vr = requests.get(download_url, stream=True, timeout=30)
            vr.raise_for_status()
            with open(clip_path, "wb") as out:
                for chunk in vr.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        out.write(chunk)
            downloaded.append(clip_path)
            logger.info(f"  Saved → '{clip_path}'")

        except Exception as e:
            logger.error(f"  Pexels error for '{keyword}': {e}")

    return downloaded


# ──────────────────────────────────────────────────────────
# STEP 3: Intelligent Rapid-Cut + Ken Burns Normaliser
# ──────────────────────────────────────────────────────────

def normalise_clip(src, dst, duration_s):
    """
    Crops & scales to 1080x1920, applies Ken Burns zoom (1.00→1.08 over clip),
    sets 30fps, trims to exact duration.
    The 1-second skip at the start removes boring static title-card intros
    that most stock footage has.
    """
    total_frames = int(duration_s * TARGET_FPS)

    # Ken Burns: zoom from 1.00 to 1.08 progressively
    zoom_step = 0.0015  # 0.15% zoom per frame
    zoom_expr = f"'min(zoom+{zoom_step},1.08)'"
    x_expr    = "iw/2-(iw/zoom/2)"
    y_expr    = "ih/2-(ih/zoom/2)"

    vf = (
        f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,"
        f"crop={TARGET_W}:{TARGET_H},"
        f"zoompan=z={zoom_expr}:x={x_expr}:y={y_expr}"
        f":d={total_frames}:s={TARGET_W}x{TARGET_H}:fps={TARGET_FPS},"
        f"setsar=1"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", "00:00:01",          # skip static intro second
        "-t", str(duration_s + 1),  # read a little extra, trim below
        "-i", src,
        "-vf", vf,
        "-t", str(duration_s),      # hard trim to exact duration
        "-an",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",               # visually lossless
        "-pix_fmt", "yuv420p",
        dst
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        logger.warning(f"Ken Burns failed for {src}: {e}. Trying simple crop...")
        # Fallback: simple scale+crop without zoom
        simple_cmd = [
            "ffmpeg", "-y", "-ss", "00:00:01", "-t", str(duration_s), "-i", src,
            "-vf", f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,crop={TARGET_W}:{TARGET_H},setsar=1",
            "-r", str(TARGET_FPS), "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "18", dst
        ]
        try:
            subprocess.run(simple_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception as e2:
            logger.error(f"Simple crop also failed for {src}: {e2}")
            return False


def build_xfade_filter(clips, xfade_dur=XFADE_DURATION):
    """
    Chains xfade dissolve transitions between ALL normalised clips using
    FFmpeg's xfade filter. Returns (filter_complex string, output label).
    """
    if len(clips) == 1:
        return None, "[0:v]"  # single clip, no transition needed

    # Calculate cumulative offsets for each xfade
    # offset = sum of all previous clip durations minus overlap already consumed
    filter_parts = []
    prev_label    = "[0:v]"

    for i in range(1, len(clips)):
        # Probe the actual duration of each normalised clip
        curr_label = f"[xf{i}]"
        dur_cmd    = [
            "ffprobe", "-i", clips[i - 1],
            "-show_entries", "format=duration",
            "-v", "quiet", "-of", "csv=p=0"
        ]
        try:
            r = subprocess.run(dur_cmd, capture_output=True, text=True, check=True)
            clip_dur = float(r.stdout.strip())
        except Exception:
            clip_dur = XFADE_DURATION + 1  # safe fallback

        # xfade offset = duration of left clip - fade duration
        offset = max(0.0, clip_dur - xfade_dur)

        filter_parts.append(
            f"{prev_label}[{i}:v]xfade=transition=fade:duration={xfade_dur}:offset={offset:.3f}{curr_label}"
        )
        prev_label = curr_label

    return ";".join(filter_parts), prev_label


def stitch_clips_with_transitions(downloaded_clips, target_duration):
    """
    Main rapid-cut engine:
    1. Divides total audio duration equally across all clips.
    2. Normalises each clip with Ken Burns zoom to its exact slice.
    3. Chains all clips together with smooth xfade dissolve transitions.
    """
    if not downloaded_clips:
        return generate_placeholder_video(target_duration)

    n         = len(downloaded_clips)
    # Account for xfade overlaps in per-clip duration so total ≈ target_duration
    # Each transition eats XFADE_DURATION seconds from the join point
    total_fade_time  = XFADE_DURATION * (n - 1)
    raw_clip_dur     = (target_duration + total_fade_time) / n
    clip_dur         = round(max(raw_clip_dur, 2.0), 3)  # minimum 2s per clip

    logger.info(f"Rapid-Cut: {n} clips × {clip_dur:.2f}s each (with {XFADE_DURATION}s xfade transitions)")

    norm_clips = []
    for i, src in enumerate(downloaded_clips):
        dst = f"norm_clip_{i}.mp4"
        logger.info(f"  Ken Burns normalising clip {i+1}/{n}...")
        if normalise_clip(src, dst, clip_dur):
            norm_clips.append(dst)
        else:
            logger.warning(f"  Clip {i+1} failed. Skipping.")

    if not norm_clips:
        logger.error("All clips failed. Using placeholder.")
        return generate_placeholder_video(target_duration)

    if len(norm_clips) == 1:
        # Only 1 clip — simple trim to exact duration
        out = "final_broll.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-i", norm_clips[0], "-t", str(target_duration), "-c", "copy", out],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return out

    # ── Build xfade filter_complex for smooth dissolve between every clip ──
    logger.info("Applying smooth xfade dissolve transitions between all clips...")
    filter_str, final_label = build_xfade_filter(norm_clips)

    input_args = []
    for c in norm_clips:
        input_args.extend(["-i", c])

    stitched = "stitched_transitions.mp4"
    xfade_cmd = [
        "ffmpeg", "-y", *input_args,
        "-filter_complex", filter_str,
        "-map", final_label,
        "-t", str(target_duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        stitched
    ]

    try:
        subprocess.run(xfade_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Transitions applied → '{stitched}'")
        return stitched
    except Exception as e:
        logger.warning(f"xfade chain failed ({e}). Falling back to hard-cut concat...")
        return hard_cut_concat(norm_clips, target_duration)


def hard_cut_concat(norm_clips, target_duration):
    """Fallback: plain concat without transitions."""
    concat_list = "clips.txt"
    with open(concat_list, "w") as f:
        for c in norm_clips:
            f.write(f"file '{c}'\n")

    stitched = "stitched_broll.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", stitched],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    out = "final_broll.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-stream_loop", "-1", "-i", stitched, "-t", str(target_duration), "-c", "copy", out],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    return out


def generate_placeholder_video(duration):
    logger.warning("Generating premium gradient fallback video...")
    out = "final_broll.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c=0x0a0a1a:s={TARGET_W}x{TARGET_H}:d={duration}:r={TARGET_FPS}",
        "-vf", "geq=r='r(X,Y)*0.8+20':g='g(X,Y)*0.85+10':b='b(X,Y)*1.1+40'",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", out
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return out


# ──────────────────────────────────────────────────────────
# STEP 4: Background Music
# ──────────────────────────────────────────────────────────

def fetch_background_music():
    if os.path.exists(BG_MUSIC_FILE) and os.path.getsize(BG_MUSIC_FILE) > 10_000:
        logger.info("BG music already cached.")
        return True
    for url in MUSIC_URLS:
        try:
            logger.info(f"Fetching BG music: {url[:55]}...")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r, open(BG_MUSIC_FILE, "wb") as o:
                o.write(r.read())
            if os.path.getsize(BG_MUSIC_FILE) > 10_000:
                logger.info("BG music downloaded OK.")
                return True
        except Exception as e:
            logger.warning(f"  Music URL failed: {e}")
    logger.warning("All BG music URLs failed. Continuing without music.")
    return False


# ──────────────────────────────────────────────────────────
# STEP 5: Final Compile — Color Grade + Audio + Subtitles
# ──────────────────────────────────────────────────────────

def compile_final_reel(broll_video, thumbnail_text=""):
    temp = "temp_merged.mp4"

    # ── Generate thumbnail hook ASS overlay (first 2.5 seconds) ──
    ass_file = "thumbnail.ass"
    safe_thumb = thumbnail_text.replace("\\", "\\\\").replace("'", "\\'").replace(",", "\\,")
    try:
        with open(ass_file, "w", encoding="utf-8") as f:
            f.write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {TARGET_W}
PlayResY: {TARGET_H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Noto Sans,90,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,5,3,5,30,30,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:02.50,Hook,,0,0,0,,{safe_thumb}
""")
    except Exception as e:
        logger.warning(f"Thumbnail ASS failed: {e}")

    # ── Fetch music ──
    has_music = fetch_background_music()

    # ── Cinematic Color Grade ──
    # Warm contrast + vibrant saturation + very subtle vignette
    color_grade = (
        "eq=contrast=1.10:saturation=1.20:brightness=0.02:gamma=0.97,"
        "vignette=PI/5"   # subtle vignette for cinema depth
    )

    # ── Build FFmpeg audio+video merge ──
    cmd = ["ffmpeg", "-y", "-i", broll_video, "-i", AUDIO_INPUT]
    if has_music:
        cmd.extend(["-stream_loop", "-1", "-i", BG_MUSIC_FILE])
        filter_complex = (
            f"[0:v]{color_grade}[v];"
            f"[1:a]volume=1.0[tts];"
            f"[2:a]volume=0.12[bg];"
            f"[tts][bg]amix=inputs=2:duration=first:dropout_transition=3[a]"
        )
        cmd.extend(["-filter_complex", filter_complex, "-map", "[v]", "-map", "[a]"])
    else:
        cmd.extend(["-vf", color_grade, "-map", "0:v:0", "-map", "1:a:0"])

    cmd.extend([
        "-c:v", "libx264", "-preset", "medium",
        "-crf", "17",                   # visually lossless for platform
        "-b:v", "8M", "-maxrate", "12M", "-bufsize", "16M",
        "-r", str(TARGET_FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        "-shortest", temp
    ])

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("Color grade + audio merge complete.")
    except Exception as e:
        logger.error(f"Merge failed: {e}")
        raise

    # ── Burn subtitles + thumbnail hook ──
    logger.info("Burning word-by-word subtitles...")

    # Subtitle style: large yellow text, heavy black outline, positioned bottom-center
    style = (
        "Alignment=2,"
        "Fontname=Noto Sans,"
        "Fontsize=22,"
        "PrimaryColour=&H00FFFF00,"   # bright yellow
        "OutlineColour=&H00000000,"   # pure black outline
        "Outline=3,"
        "Shadow=1,"
        "BorderStyle=1,"
        "MarginV=80"
    )

    srt_path = SRT_INPUT.replace("\\", "/").replace(":", "\\:")
    ass_path = ass_file.replace("\\", "/").replace(":", "\\:")

    cmd_subs = [
        "ffmpeg", "-y", "-i", temp,
        "-vf", f"ass={ass_path},subtitles={srt_path}:force_style='{style}'",
        "-c:v", "libx264", "-preset", "medium",
        "-crf", "17",
        "-b:v", "8M", "-maxrate", "12M", "-bufsize", "16M",
        "-r", str(TARGET_FPS),
        "-c:a", "copy",
        "-map_metadata", "-1",
        "-movflags", "+faststart",
        FINAL_REEL
    ]

    try:
        subprocess.run(cmd_subs, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"✅ CINEMATIC REEL READY: '{FINAL_REEL}'")
    except Exception as e:
        logger.warning(f"Subtitle burn failed ({e}). Saving without subtitles.")
        import shutil
        shutil.copy(temp, FINAL_REEL)

    cleanup_temp_files()


# ──────────────────────────────────────────────────────────
# CLEANUP
# ──────────────────────────────────────────────────────────

def cleanup_temp_files():
    logger.info("Cleaning up temp files...")
    kill = [
        "raw_clip_", "norm_clip_", "clips.txt",
        "stitched_broll.mp4", "stitched_transitions.mp4",
        "final_broll.mp4", "temp_merged.mp4", "thumbnail.ass"
    ]
    for f in os.listdir("."):
        for p in kill:
            if f == p or f.startswith(p):
                try:
                    os.remove(f)
                except OSError:
                    pass


# ──────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────

def render():
    if not os.path.exists(SCRIPT_INPUT):
        raise FileNotFoundError(f"'{SCRIPT_INPUT}' not found.")

    with open(SCRIPT_INPUT, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    duration   = get_audio_duration()
    pexels_key = os.environ.get("PEXELS_API_KEY")

    if not pexels_key:
        logger.warning("No PEXELS_API_KEY. Using placeholder.")
        broll = generate_placeholder_video(duration)
    else:
        downloaded = fetch_pexels_videos(script_data.get("pexels_keywords", []), pexels_key)
        broll      = stitch_clips_with_transitions(downloaded, duration) if downloaded else generate_placeholder_video(duration)

    compile_final_reel(broll, script_data.get("thumbnail_text", ""))


if __name__ == "__main__":
    render()
