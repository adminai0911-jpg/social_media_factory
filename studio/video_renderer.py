#!/usr/bin/env python3
"""
CINEMATIC STUDIO ENGINE — Phase 10 (The Human Editor)

Core upgrades for perfect voice-visual sync and seamless transitions:

1. SRT-DRIVEN TIMING: Parses subtitles.srt to get actual word timestamps.
   Divides audio into 10 segments based on REAL speech timing, not equal math.
   Each Pexels clip plays for EXACTLY as long as its corresponding speech segment.

2. PER-CLIP COLOR NORMALIZATION: Applies identical warm cinematic grade to EVERY clip
   individually before stitching. All clips look like they come from the same camera.
   This makes clip transitions invisible to the human eye.

3. SEAMLESS 0.6s XFADE: Longer dissolve makes transitions feel like one continuous film.

4. SMART DUPLICATE PREVENTION: Never downloads the same Pexels video twice.

5. SUBTITLE BURN: Uses relative paths (cross-platform: works on Windows & Linux).
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

XFADE_DURATION = 0.6   # longer = more seamless and invisible transitions


# ──────────────────────────────────────────────────────────
# STEP 1: AUDIO ANALYSIS
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
        logger.error(f"ffprobe failed: {e}. Using 55s default.")
        return 55.0


# ──────────────────────────────────────────────────────────
# STEP 2: SRT-DRIVEN CLIP TIMING
# ──────────────────────────────────────────────────────────

def parse_srt_word_times(srt_path):
    """
    Parses the SRT subtitle file and returns a list of (start_sec, end_sec) tuples
    for every subtitle entry (each entry = one word from edge-tts).
    """
    if not os.path.exists(srt_path):
        return []

    def ts_to_sec(ts):
        try:
            ts = ts.strip().replace(",", ".")
            h, m, s = ts.split(":")
            return float(h) * 3600 + float(m) * 60 + float(s)
        except Exception:
            return 0.0

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
    """
    Divides the actual audio into num_clips segments using SRT word timestamps.
    Returns a list of per-clip durations (in seconds) where each duration
    represents exactly how long that clip should play while that part of the
    script is being spoken.
    
    Strategy:
    - Parse SRT word timestamps
    - Split words into num_clips equal groups
    - Each group's duration = last word end time - first word start time
    - Pad slightly to cover xfade overlap
    """
    word_times = parse_srt_word_times(SRT_INPUT)

    if not word_times or num_clips <= 0:
        # Fallback: equal division accounting for xfade overlaps
        n            = max(1, num_clips)
        overlap      = (n - 1) * XFADE_DURATION
        clip_dur     = (total_audio_duration + overlap) / n
        logger.info(f"SRT fallback: {n} equal clips × {clip_dur:.2f}s")
        return [max(clip_dur, 2.5)] * n

    # Split word entries into num_clips groups
    n             = min(num_clips, len(word_times))
    words_per_seg = max(1, len(word_times) // n)
    segments      = []

    for i in range(n):
        start_idx  = i * words_per_seg
        end_idx    = start_idx + words_per_seg if i < n - 1 else len(word_times)
        seg_words  = word_times[start_idx:end_idx]
        if not seg_words:
            continue
        seg_start  = seg_words[0][0]
        seg_end    = seg_words[-1][1]
        raw_dur    = seg_end - seg_start
        # Add xfade overlap so the final stitched total equals the audio duration
        padded_dur = raw_dur + XFADE_DURATION
        segments.append(max(padded_dur, 2.5))

    if not segments:
        segments = [total_audio_duration / num_clips] * num_clips

    logger.info(f"SRT Timing: {len(segments)} clips — durations: {[round(d,2) for d in segments]}")
    return segments


# ──────────────────────────────────────────────────────────
# STEP 3: PEXELS HIGH-QUALITY DOWNLOAD
# ──────────────────────────────────────────────────────────

def fetch_pexels_videos(keywords, pexels_key):
    headers   = {"Authorization": pexels_key}
    base_url  = "https://api.pexels.com/videos/search"
    downloaded = []
    used_ids   = set()

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

            # Sort by total pixels → highest quality first
            files_sorted = sorted(
                selected.get("video_files", []),
                key=lambda f: f.get("width", 0) * f.get("height", 0),
                reverse=True
            )

            # Prefer vertical file
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
# STEP 4: PER-CLIP NORMALIZATION WITH COLOR MATCHING
# ──────────────────────────────────────────────────────────

def normalise_clip(src, dst, duration_s):
    """
    1. Skips first 1 second (avoids static stock title cards).
    2. Scales & crops to exactly 1080x1920 portrait.
    3. Applies a CONSISTENT warm cinematic color grade to ALL clips.
       This is the key to seamless transitions — if every clip has the
       same color temperature and contrast, the human eye cannot see the cut.
    4. Sets to 30 FPS.
    5. Trims to EXACT duration_s seconds.
    """
    # Consistent warm cinematic grade applied to EVERY clip individually
    # eq: slight contrast/warmth boost
    # hue: push slightly warm (yellower/orange)
    per_clip_grade = (
        "eq=contrast=1.08:saturation=1.12:brightness=0.01:gamma=0.98,"
        "hue=h=3:s=1.05"   # 3 degree hue shift toward warmth
    )

    vf = (
        f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,"
        f"crop={TARGET_W}:{TARGET_H},"
        f"setsar=1,"
        f"{per_clip_grade}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-ss", "1",
        "-t", str(duration_s),
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
        logger.error(f"Normalise failed for {src}: {e}")
        return False


# ──────────────────────────────────────────────────────────
# STEP 5: SEAMLESS XFADE CHAIN (CUMULATIVE OFFSETS)
# ──────────────────────────────────────────────────────────

def get_clip_duration(clip_path):
    cmd = ["ffprobe", "-i", clip_path, "-show_entries", "format=duration",
           "-v", "quiet", "-of", "csv=p=0"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(r.stdout.strip())
    except Exception:
        return 3.5


def build_xfade_chain(norm_clips, target_duration):
    """
    Chains all clips with smooth xfade dissolve transitions.
    Uses CUMULATIVE offsets — the correct FFmpeg xfade chaining method.
    offset_N = sum(clip_durations[0..N-1]) - N * XFADE_DURATION
    """
    n = len(norm_clips)
    if n == 1:
        out = "stitched_broll.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-i", norm_clips[0], "-t", str(target_duration), "-c", "copy", out],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return out

    # Probe actual durations of normalized clips
    clip_durations = [get_clip_duration(c) for c in norm_clips]

    filter_parts = []
    prev_label   = "[0:v]"
    cumulative   = 0.0

    for i in range(1, n):
        cumulative  += clip_durations[i - 1] - XFADE_DURATION
        offset       = max(0.01, cumulative)
        curr_label   = f"[xf{i}]"
        filter_parts.append(
            f"{prev_label}[{i}:v]xfade=transition=fade"
            f":duration={XFADE_DURATION}:offset={offset:.4f}{curr_label}"
        )
        prev_label = curr_label

    input_args = []
    for c in norm_clips:
        input_args.extend(["-i", c])

    filter_str = ";".join(filter_parts)
    stitched   = "stitched_broll.mp4"

    cmd = [
        "ffmpeg", "-y", *input_args,
        "-filter_complex", filter_str,
        "-map", prev_label,
        "-t", str(target_duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        stitched
    ]

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Seamless xfade chain → '{stitched}'")
        return stitched
    except Exception as e:
        logger.warning(f"xfade failed ({e}). Using hard-cut fallback.")
        return hard_cut_concat(norm_clips, target_duration)


def hard_cut_concat(norm_clips, target_duration):
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
# STEP 6: BACKGROUND MUSIC
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
                logger.info("BG music downloaded.")
                return True
        except Exception as e:
            logger.warning(f"Music URL failed: {e}")
    return False


# ──────────────────────────────────────────────────────────
# STEP 7: PLACEHOLDER (fallback if Pexels fails)
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
# STEP 8: FINAL COMPILE — final grade + audio + subtitles
# ──────────────────────────────────────────────────────────

def compile_final_reel(broll_video, thumbnail_text=""):
    temp = "temp_merged.mp4"

    # Thumbnail hook overlay (first 2.5 seconds)
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
        logger.warning(f"ASS file failed: {e}")

    has_music = fetch_background_music()

    # Final color grade: slight overall warm boost + vignette on top of per-clip grade
    final_grade = "eq=contrast=1.04:saturation=1.05:brightness=0.01,vignette=PI/6"

    cmd = ["ffmpeg", "-y", "-i", broll_video, "-i", AUDIO_INPUT]
    if has_music:
        cmd.extend(["-stream_loop", "-1", "-i", BG_MUSIC_FILE])
        fc = (
            f"[0:v]{final_grade}[v];"
            f"[1:a]volume=1.0[tts];"
            f"[2:a]volume=0.12[bg];"
            f"[tts][bg]amix=inputs=2:duration=first:dropout_transition=3[a]"
        )
        cmd.extend(["-filter_complex", fc, "-map", "[v]", "-map", "[a]"])
    else:
        cmd.extend(["-vf", final_grade, "-map", "0:v:0", "-map", "1:a:0"])

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

    # Subtitle burn — use relative filenames for cross-platform compatibility
    logger.info("Burning word-by-word subtitles...")
    style = (
        "Alignment=2,Fontname=Arial,Fontsize=20,"
        "PrimaryColour=&H00FFFF00,OutlineColour=&H00000000,"
        "Outline=3,Shadow=1,BorderStyle=1,MarginV=80"
    )
    srt_rel = os.path.basename(SRT_INPUT)
    ass_rel = os.path.basename(ass_file)

    cmd_subs = [
        "ffmpeg", "-y", "-i", temp,
        "-vf", f"ass={ass_rel},subtitles={srt_rel}:force_style='{style}'",
        "-c:v", "libx264", "-preset", "medium",
        "-crf", "17", "-b:v", "8M", "-maxrate", "12M", "-bufsize", "16M",
        "-r", str(TARGET_FPS),
        "-c:a", "copy", "-map_metadata", "-1", "-movflags", "+faststart",
        FINAL_REEL
    ]
    try:
        subprocess.run(cmd_subs, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"✅ FINAL REEL READY WITH SUBTITLES: '{FINAL_REEL}'")
    except Exception as e:
        logger.warning(f"Subtitle burn failed ({e}). Saving without subtitles.")
        import shutil
        shutil.copy(temp, FINAL_REEL)
        logger.info(f"✅ FINAL REEL READY (no subtitles): '{FINAL_REEL}'")

    cleanup_temp_files()


# ──────────────────────────────────────────────────────────
# CLEANUP
# ──────────────────────────────────────────────────────────

def cleanup_temp_files():
    logger.info("Cleaning up temp files...")
    kill_prefixes = ["raw_clip_", "norm_clip_", "clips.txt",
                     "stitched_broll.mp4", "temp_merged.mp4", "thumbnail.ass"]
    for fname in os.listdir("."):
        for p in kill_prefixes:
            if fname == p or fname.startswith(p):
                try:
                    os.remove(fname)
                except OSError:
                    pass


# ──────────────────────────────────────────────────────────
# MAIN RENDER
# ──────────────────────────────────────────────────────────

def render():
    if not os.path.exists(SCRIPT_INPUT):
        raise FileNotFoundError(f"'{SCRIPT_INPUT}' not found.")

    with open(SCRIPT_INPUT, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    total_duration = get_audio_duration()
    pexels_key     = os.environ.get("PEXELS_API_KEY")
    keywords       = script_data.get("pexels_keywords", [])
    num_keywords   = len(keywords)

    logger.info(f"Target duration: {total_duration:.2f}s | Keywords: {num_keywords}")

    if not pexels_key or not keywords:
        logger.warning("No Pexels key or keywords. Using placeholder.")
        broll = generate_placeholder_video(total_duration)
    else:
        # Step A: Download clips
        downloaded = fetch_pexels_videos(keywords, pexels_key)

        if not downloaded:
            logger.warning("No Pexels clips. Using placeholder.")
            broll = generate_placeholder_video(total_duration)
        else:
            # Step B: Calculate SRT-driven clip durations (voice sync)
            clip_durations = calculate_srt_segment_durations(len(downloaded), total_duration)

            # Step C: Normalise each clip with consistent color grade
            norm_clips = []
            for i, (src, dur) in enumerate(zip(downloaded, clip_durations)):
                dst = f"norm_clip_{i}.mp4"
                logger.info(f"Normalising clip {i+1}/{len(downloaded)} → {dur:.2f}s | '{keywords[i] if i < len(keywords) else ''}'")
                if normalise_clip(src, dst, dur):
                    norm_clips.append(dst)
                else:
                    logger.warning(f"Clip {i+1} failed — skipping.")

            if not norm_clips:
                broll = generate_placeholder_video(total_duration)
            else:
                # Step D: Stitch with seamless 0.6s dissolve transitions
                broll = build_xfade_chain(norm_clips, total_duration)

    compile_final_reel(broll, script_data.get("thumbnail_text", ""))


if __name__ == "__main__":
    render()
