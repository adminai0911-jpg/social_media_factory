#!/usr/bin/env python3
"""
THE HUMAN-STYLE DYNAMIC ENGINE — Phase 12.4
Infinite Visual Sync (yt-dlp) & Dynamic Typography

Features:
1. YT-DLP Global Scraping for 100% Exact Matching (Bypasses APIs)
2. Dynamic Typography (Fades, Slides, Zooms, Random Quadrants, Emojis)
3. 30s Pattern Interrupt, Color Shift, Progress Bar, 3D Whooshes
"""

import os
import json
import random
import logging
import subprocess
import urllib.request
import math

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("DynamicStudio")

SCRIPT_INPUT  = "script_output.json"
AUDIO_INPUT   = "audio_narration.mp3"
SRT_INPUT     = "subtitles.srt"
FINAL_REEL    = "final_reel.mp4"
BG_MUSIC_FILE = "bg_music.mp3"
WHOOSH_FILE   = "whoosh.mp3"
DROP_FILE     = "drop.mp3"
CACHE_DIR     = "yt_broll_cache"

TARGET_W      = 1080
TARGET_H      = 1920
TARGET_FPS    = 30

MUSIC_URLS = ["https://cdn.pixabay.com/download/audio/2022/10/25/audio_5b3eb59461.mp3"]
WHOOSH_URL = "https://cdn.pixabay.com/download/audio/2022/03/15/audio_7ea20eb18a.mp3"
DROP_URL   = "https://cdn.pixabay.com/download/audio/2022/03/10/audio_c8c8a73467.mp3"

os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_audio_assets():
    if not os.path.exists(BG_MUSIC_FILE):
        for url in MUSIC_URLS:
            try:
                r = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=20)
                with open(BG_MUSIC_FILE, "wb") as o: o.write(r.read())
                break
            except: pass
    if not os.path.exists(WHOOSH_FILE):
        try:
            r = urllib.request.urlopen(urllib.request.Request(WHOOSH_URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=20)
            with open(WHOOSH_FILE, "wb") as o: o.write(r.read())
        except: pass
    if not os.path.exists(DROP_FILE):
        try:
            r = urllib.request.urlopen(urllib.request.Request(DROP_URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=20)
            with open(DROP_FILE, "wb") as o: o.write(r.read())
        except: pass

def get_audio_duration():
    try:
        r = subprocess.run(["ffprobe", "-i", AUDIO_INPUT, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"], capture_output=True, text=True, check=True)
        return float(r.stdout.strip())
    except: return 55.0

def parse_srt_times():
    if not os.path.exists(SRT_INPUT): return []
    def ts(s):
        try:
            h, m, sec = s.strip().replace(",", ".").split(":")
            return float(h) * 3600 + float(m) * 60 + float(sec)
        except: return 0.0
    entries = []
    with open(SRT_INPUT, encoding="utf-8") as f:
        for block in f.read().strip().split("\n\n"):
            lines = [l.strip() for l in block.strip().splitlines()]
            arrow = next((l for l in lines if "-->" in l), None)
            if arrow:
                p = arrow.split("-->")
                if len(p) == 2: entries.append((ts(p[0]), ts(p[1])))
    return entries

def get_clip_durations_from_srt(n_clips, total_dur):
    words = parse_srt_times()
    if not words or n_clips <= 0:
        return [total_dur / max(n_clips, 1)] * n_clips
    n = min(n_clips, len(words))
    words_per_seg = max(1, len(words) // n)
    durations = []
    for i in range(n):
        start_idx = i * words_per_seg
        end_idx   = start_idx + words_per_seg if i < n - 1 else len(words)
        seg       = words[start_idx:end_idx]
        if not seg: continue
        raw_dur = seg[-1][1] - seg[0][0]
        durations.append(max(raw_dur, 1.5))
    while len(durations) < n_clips: durations.append(total_dur / n_clips)
    return durations[:n_clips]

def fetch_clip_dynamically_youtube(query):
    """Uses yt-dlp to grab exactly the visual we need from global stock video / shorts"""
    clean_query = "".join(c if c.isalnum() else "_" for c in query)
    cache_path = os.path.join(CACHE_DIR, f"{clean_query}.mp4")
    
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 100_000:
        return cache_path

    # Search for stock video or vertical short matching exactly the query
    search_term = f"stock video footage {query}"
    logger.info(f"Downloading from YouTube Worldwide DB: '{search_term}'")
    
    temp_dl = f"temp_{clean_query}.mp4"
    cmd = [
        "python", "-m", "yt_dlp",
        f"ytsearch1:{search_term}",
        "-f", "bestvideo[ext=mp4]/best",
        "--max-downloads", "1",
        "--quiet", "--no-warnings",
        "-o", temp_dl
    ]
    
    try:
        subprocess.run(cmd, check=True)
        if os.path.exists(temp_dl):
            # Extract a random 3-5 second clip from the downloaded video to avoid long unedited blocks
            total_dur_str = subprocess.run(["ffprobe", "-i", temp_dl, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"], capture_output=True, text=True).stdout.strip()
            total_dur = float(total_dur_str) if total_dur_str else 10.0
            start_time = random.uniform(2, max(2.1, total_dur - 5))
            
            # Crop to 9:16 and save to cache
            subprocess.run([
                "ffmpeg", "-y", "-ss", str(start_time), "-t", "5", "-i", temp_dl,
                "-vf", f"crop=ih*(9/16):ih,scale={TARGET_W}:{TARGET_H}",
                "-an", "-c:v", "libx264", "-preset", "ultrafast", cache_path
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            os.remove(temp_dl)
            return cache_path
    except Exception as e:
        logger.error(f"YT-DLP failed for '{query}': {e}")
        if os.path.exists(temp_dl): os.remove(temp_dl)
        return None
    return None

def fallback_clip():
    clips = []
    for root, _, files in os.walk("broll"):
        for f in files:
            if f.endswith(".mp4"): clips.append(os.path.join(root, f))
    return random.choice(clips) if clips else None

def get_dynamic_typography(master_word, target_dur):
    if not master_word: return ""
    
    mw_clean = master_word.replace("'", "").replace(":", "")
    
    colors = ["#00FFFF", "#FF00FF", "#FFFF00", "#FF4444", "#00FF44", "white"]
    color = random.choice(colors)
    
    # Fonts available on Windows. Emojis work best with default Arial or Segoe UI
    fonts = ["C\\:/Windows/Fonts/arialbd.ttf", "C\\:/Windows/Fonts/impact.ttf"]
    font = random.choice(fonts)
    
    # Randomly position text in different quadrants to not block the center
    # x, y strings for FFmpeg
    positions = [
        # Center Middle
        ("(w-text_w)/2", "(h-text_h)/2"),
        # Top Third
        ("(w-text_w)/2", "h/4"),
        # Bottom Third
        ("(w-text_w)/2", "3*h/4"),
        # Top Right
        ("w-text_w-100", "h/4"),
        # Top Left
        ("100", "h/4"),
    ]
    x_pos, y_pos = random.choice(positions)
    
    # Random Animation Styles
    anim_type = random.choice(["static", "zoom", "slide_left", "slide_right", "fade"])
    
    size_str = "100"
    alpha_str = "1.0"
    
    if anim_type == "zoom":
        size_str = "min(80+t*30, 140)"
        x_pos = "(w-tw)/2" # Needs tw for dynamic size
        y_pos = "(h-th)/2"
    elif anim_type == "slide_left":
        x_pos = "min(t*1000, (w-text_w)/2)"
    elif anim_type == "slide_right":
        x_pos = "max(w-t*1000, (w-text_w)/2)"
    elif anim_type == "fade":
        alpha_str = "min(t*2, 1.0)"
        
    # Outline and shadow instead of a box, for raw clean text
    outline = "borderw=5:bordercolor=black:shadowcolor=black@0.8:shadowx=6:shadowy=6"
    
    drawtext = f"drawtext=text='{mw_clean}':fontcolor={color}:fontsize={size_str}:fontfile='{font}':x={x_pos}:y={y_pos}:alpha={alpha_str}:{outline}:enable='between(t,0.2,{target_dur-0.2})'"
    return f",{drawtext}"

def normalize_and_add_text(src, dst, target_dur, master_word, is_warm):
    if is_warm:
        grade = "eq=contrast=1.1:saturation=1.2:brightness=0.02:gamma=1.0:gamma_b=0.9:gamma_r=1.1"
    else:
        grade = "eq=contrast=1.1:saturation=0.8:brightness=-0.02:gamma=0.95:gamma_r=0.9:gamma_b=1.1"
        
    # Visual Hypnosis: Continuous 3% per second zoom-in
    hypnosis_zoom = f"zoompan=z='1+0.03*t':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={TARGET_W}x{TARGET_H}:fps={TARGET_FPS}"
        
    vf = f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,crop={TARGET_W}:{TARGET_H},setsar=1,{grade},{hypnosis_zoom}"
    vf += get_dynamic_typography(master_word, target_dur)
        
    cmd = [
        "ffmpeg", "-y", "-ss", "0", "-t", str(target_dur), "-i", src,
        "-vf", vf, "-r", str(TARGET_FPS), "-an",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "18",
        "-pix_fmt", "yuv420p", dst
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def build_hardcut_chain(norm_clips):
    midpoint = len(norm_clips) // 2
    black_clip = "black_interrupt.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=black:s={TARGET_W}x{TARGET_H}:d=0.5:r={TARGET_FPS}", "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", black_clip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    chain_list = norm_clips[:midpoint] + [black_clip] + norm_clips[midpoint:]
    
    with open("clips.txt", "w") as f:
        for c in chain_list: f.write(f"file '{c}'\n")
    out = "stitched_broll.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "clips.txt", "-c", "copy", out], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    cut_times = []
    cumulative = 0.0
    for i, c in enumerate(chain_list[:-1]):
        dur = float(subprocess.run(["ffprobe", "-i", c, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"], capture_output=True, text=True).stdout.strip())
        cumulative += dur
        cut_times.append((cumulative, "DROP" if c == black_clip else "WHOOSH"))
    return out, cut_times

def build_sfx_mix(cut_times):
    if not cut_times or not os.path.exists(WHOOSH_FILE): return None
    inputs, filters = [], []
    valid_cuts = 0
    for i, (t, sfx_type) in enumerate(cut_times):
        if sfx_type == "DROP" and os.path.exists(DROP_FILE):
            inputs.extend(["-i", DROP_FILE])
            filters.append(f"[{valid_cuts}:a]adelay={int(t*1000)}|{int(t*1000)}[w{valid_cuts}]")
            valid_cuts += 1
        elif os.path.exists(WHOOSH_FILE):
            inputs.extend(["-i", WHOOSH_FILE])
            pan_val = -0.8 if i % 2 == 0 else 0.8
            filters.append(f"[{valid_cuts}:a]adelay={int(t*1000)}|{int(t*1000)},apulsator=mode=sine:hz=2:offset_l={pan_val}:offset_r={-pan_val}[w{valid_cuts}]")
            valid_cuts += 1
            
    if valid_cuts == 0: return None
    labels = "".join(f"[w{i}]" for i in range(valid_cuts))
    filters.append(f"{labels}amix=inputs={valid_cuts}:dropout_transition=0:normalize=0[sfx]")
    sfx_out = "sfx_track.wav"
    try:
        subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "[sfx]", sfx_out], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return sfx_out
    except: return None

def add_progress_bar(video_in, video_out):
    dur = float(subprocess.run(["ffprobe", "-i", video_in, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"], capture_output=True, text=True).stdout.strip())
    vf = f"drawbox=y=ih-10:color=red@0.8:width=iw*t/{dur}:height=10:t=fill"
    try:
        subprocess.run(["ffmpeg", "-y", "-i", video_in, "-vf", vf, "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "copy", video_out], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        import shutil
        shutil.copy(video_in, video_out)

def compile_final(broll, cut_times):
    fetch_audio_assets()
    sfx = build_sfx_mix(cut_times)
    temp_out = "temp_merged.mp4"
    
    cmd = ["ffmpeg", "-y", "-i", broll, "-i", AUDIO_INPUT]
    audio_parts = "[1:a]volume=1.0[voice];"
    mix_labels, mix_count = "[voice]", 1
    
    if os.path.exists(BG_MUSIC_FILE):
        cmd.extend(["-stream_loop", "-1", "-i", BG_MUSIC_FILE])
        audio_parts += "[2:a]volume=0.10[bg];"
        mix_labels += "[bg]"
        mix_count += 1
    if sfx and os.path.exists(sfx):
        sfx_idx = 3 if os.path.exists(BG_MUSIC_FILE) else 2
        cmd.extend(["-i", sfx])
        audio_parts += f"[{sfx_idx}:a]volume=0.8[sfx];"
        mix_labels += "[sfx]"
        mix_count += 1

    fc = f"{audio_parts}{mix_labels}amix=inputs={mix_count}:duration=first:dropout_transition=3[a_out]"
    cmd.extend(["-filter_complex", fc, "-map", "0:v", "-map", "[a_out]", "-c:v", "copy", "-shortest", temp_out])
    
    logger.info("Merging audio streams...")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    logger.info("Adding Progress Bar...")
    pb_out = "temp_pb.mp4"
    add_progress_bar(temp_out, pb_out)

    logger.info("Burning subtitles...")
    srt_abs = os.path.abspath(SRT_INPUT).replace("\\", "/").replace(":", "\\:")
    style = "Alignment=2,Fontname=Arial,Fontsize=30,Bold=-1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,Outline=5,Shadow=3,MarginV=60"
    
    try:
        r1 = subprocess.run(["ffmpeg", "-y", "-i", pb_out, "-vf", f"subtitles='{srt_abs}':force_style='{style}'", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "copy", FINAL_REEL], capture_output=True, text=True)
        if r1.returncode != 0:
            r2 = subprocess.run(["ffmpeg", "-y", "-i", pb_out, "-vf", f"subtitles={os.path.basename(SRT_INPUT)}:force_style='{style}'", "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "copy", FINAL_REEL], capture_output=True, text=True)
            if r2.returncode != 0:
                import shutil
                shutil.copy(pb_out, FINAL_REEL)
    except:
        import shutil
        shutil.copy(pb_out, FINAL_REEL)

    # Cleanup
    for f in os.listdir("."):
        if f.startswith("norm_clip_") or f in ["clips.txt", "stitched_broll.mp4", "temp_merged.mp4", "temp_pb.mp4", "sfx_track.wav", "black_interrupt.mp4"]:
            try: os.remove(f)
            except: pass

def render():
    fetch_audio_assets()
    with open(SCRIPT_INPUT, "r", encoding="utf-8") as f: script = json.load(f)
    scenes = script.get("scenes", [])
    if not scenes:
        logger.error("No scenes found.")
        return

    total_dur = get_audio_duration()
    clip_durs = get_clip_durations_from_srt(len(scenes), total_dur)
    
    norm_clips = []
    midpoint = len(scenes) // 2
    
    for i, (scene, dur) in enumerate(zip(scenes, clip_durs)):
        query = scene.get("visual_query", "")
        master_word = scene.get("master_word", "")
        
        logger.info(f"Scene {i+1}/{len(scenes)}: Query='{query}' | Word='{master_word}'")
        
        src = fetch_clip_dynamically_youtube(query)
        if not src: 
            src = fallback_clip()
            logger.info(f"Using generic fallback.")
            
        if not src: continue
            
        dst = f"norm_clip_{i}.mp4"
        is_warm = (i >= midpoint)
        
        if normalize_and_add_text(src, dst, dur, master_word, is_warm):
            norm_clips.append(dst)
    
    if norm_clips:
        broll, cuts = build_hardcut_chain(norm_clips)
        compile_final(broll, cuts)
        logger.info(f"✅ ULTIMATE HUMAN-EDITED REEL READY: {FINAL_REEL}")

if __name__ == "__main__":
    render()
