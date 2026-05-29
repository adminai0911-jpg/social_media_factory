#!/usr/bin/env python3
"""
Studio Video Renderer
Downloads vertical stock b-roll clips from Pexels API matching the trend keywords.
Stitches, normalizes, crops to vertical 1080x1920 @ 30fps.
Applies color contrast adjustment, maps the edge-tts narration audio,
and burns high-retention word-by-word yellow subtitles using native FFmpeg filters.
"""

import os
import json
import logging
import requests
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("StudioRenderer")

SCRIPT_INPUT = "script_output.json"
AUDIO_INPUT = "audio_narration.mp3"
SRT_INPUT = "subtitles.srt"
FINAL_REEL = "final_reel.mp4"

def get_audio_duration():
    """
    Retrieves the exact duration of the audio narration file using ffprobe.
    """
    logger.info("Calculating audio narration duration using ffprobe...")
    cmd = [
        "ffprobe", "-i", AUDIO_INPUT,
        "-show_entries", "format=duration",
        "-v", "quiet", "-of", "csv=p=0"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration = float(result.stdout.strip())
        logger.info(f"Audio narration duration: {duration:.2f} seconds.")
        return duration
    except Exception as e:
        logger.error(f"Failed to probe audio duration: {e}. Defaulting to 15.0 seconds.")
        return 15.0

def fetch_pexels_videos(keywords, pexels_key):
    """
    Queries the Pexels Video API for high-quality, vertical stock clips.
    """
    headers = {"Authorization": pexels_key}
    downloaded_files = []
    
    # We want vertical clips
    base_url = "https://api.pexels.com/videos/search"
    
    # We attempt to download 1 video per keyword to create a dynamic composite
    for i, keyword in enumerate(keywords[:3]):
        logger.info(f"Querying Pexels for keyword: '{keyword}'...")
        params = {
            "query": keyword,
            "orientation": "portrait",
            "per_page": 5,
            "size": "medium"
        }
        
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            videos = data.get("videos", [])
            if not videos:
                logger.warning(f"No vertical videos found for keyword: '{keyword}'. Skipping.")
                continue
                
            # Grab the best video file (vertical orientation with HD size)
            selected_video = videos[0]
            video_files = selected_video.get("video_files", [])
            
            # Find a vertical video file link
            download_url = None
            for file in video_files:
                if file.get("width") and file.get("height"):
                    if file["width"] < file["height"]: # vertical check
                        download_url = file["link"]
                        break
            
            if not download_url and video_files:
                # Fallback to the first video file
                download_url = video_files[0]["link"]
                
            if download_url:
                clip_path = f"raw_clip_{i}.mp4"
                logger.info(f"Downloading b-roll clip from: {download_url[:60]}...")
                vid_resp = requests.get(download_url, stream=True, timeout=30)
                vid_resp.raise_for_status()
                
                with open(clip_path, "wb") as f:
                    for chunk in vid_resp.iter_content(chunk_size=1024*1024):
                        if chunk:
                            f.write(chunk)
                
                downloaded_files.append(clip_path)
                logger.info(f"Saved raw b-roll clip: '{clip_path}'")
                
        except Exception as e:
            logger.error(f"Error fetching/downloading video for '{keyword}': {e}")
            
    return downloaded_files

def normalize_and_stitch(downloaded_clips, target_duration):
    """
    Scales, crops to 1080x1920 vertical format, sets FPS to 30, and stitches 
    clips together using FFmpeg filters. Truncates or loops to match target duration.
    """
    logger.info("Normalizing b-roll clips (Aspect Ratio, FPS, Resolution)...")
    normalized_clips = []
    
    for i, clip in enumerate(downloaded_clips):
        norm_output = f"norm_clip_{i}.mp4"
        # Scale & crop to exactly 1080x1920, force 30fps, remove audio track
        cmd = [
            "ffmpeg", "-y", "-i", clip,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
            "-r", "30", "-an", "-c:v", "libx264", "-preset", "fast", norm_output
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            normalized_clips.append(norm_output)
            logger.info(f"Normalized clip saved: '{norm_output}'")
        except Exception as e:
            logger.error(f"Failed to normalize clip '{clip}': {e}")

    if not normalized_clips:
        logger.error("No valid normalized clips available! Attempting fallback generation.")
        return generate_placeholder_video(target_duration)

    # Prepare list for FFmpeg concat
    concat_list_file = "clips.txt"
    with open(concat_list_file, "w") as f:
        for clip in normalized_clips:
            f.write(f"file '{clip}'\n")

    stitched_output = "stitched_broll.mp4"
    logger.info("Concatenating normalized b-roll clips...")
    
    # Concatenate the files
    cmd_concat = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", concat_list_file, "-c", "copy", stitched_output
    ]
    
    try:
        subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        logger.error(f"Failed to concat clips: {e}")
        return generate_placeholder_video(target_duration)

    # Trim/Loop b-roll to match the narration track duration exactly
    final_broll = "final_broll.mp4"
    cmd_trim = [
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", stitched_output,
        "-t", str(target_duration), "-c", "copy", final_broll
    ]
    
    try:
        subprocess.run(cmd_trim, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Final stitched & trimmed b-roll complete: '{final_broll}'")
        return final_broll
    except Exception as e:
        logger.error(f"Failed to trim b-roll: {e}")
        return generate_placeholder_video(target_duration)

def generate_placeholder_video(duration):
    """
    Fallback video generator creating a premium dark-gradient aesthetic background.
    """
    logger.warning("Generating high-quality abstract gradient video as fallback...")
    placeholder_output = "final_broll.mp4"
    # Generates a premium dark aesthetic moving gradient
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c=0x111116:s=1080x1920:d={duration}:r=30",
        "-vf", "geq=r='r(X,Y)*0.9':g='g(X,Y)*0.95':b='b(X,Y)*1.05'", # premium cool tint filter
        "-c:v", "libx264", "-pix_fmt", "yuv420p", placeholder_output
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return placeholder_output

def compile_final_reel(broll_video, thumbnail_text=""):
    """
    Merges normalized b-roll video with narration audio, applies subtle 
    contrast/grain filters, and burns word-by-word yellow highlighted subtitles.
    Also burns a massive thumbnail text hook for the first 2 seconds.
    """
    logger.info("Merging audio track and applying color grading filters...")
    temp_output = "temp_reel_no_subs.mp4"
    
    # Generate ASS file for the massive thumbnail text (0 to 2 seconds)
    ass_file = "thumbnail.ass"
    try:
        with open(ass_file, "w", encoding="utf-8") as f:
            f.write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Thumbnail,Liberation Sans,120,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,8,4,5,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:02.00,Thumbnail,,0,0,0,,{thumbnail_text}
""")
    except Exception as e:
        logger.error(f"Failed to generate thumbnail ASS: {e}")

    # Combine video and audio, apply visual enhancement
    cmd_merge = [
        "ffmpeg", "-y", "-i", broll_video, "-i", AUDIO_INPUT,
        "-vf", "eq=contrast=1.07:saturation=1.12:brightness=0.01,noise=alls=2:allf=t",
        "-c:v", "libx264", "-preset", "medium", "-b:v", "12M", "-maxrate", "14M", "-bufsize", "24M", "-r", "30",
        "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-map", "0:v:0", "-map", "1:a:0",
        "-shortest", temp_output
    ]
    
    try:
        subprocess.run(cmd_merge, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info("Video-audio merge complete.")
    except Exception as e:
        logger.error(f"Failed to merge audio/video: {e}")
        raise

    logger.info("Burning dynamic, word-by-word yellow subtitles...")
    
    # Subtitle Style Parameters: 
    # Alignment=2 (Bottom Center), Fontname=Liberation Sans (safe linux font), Fontsize=24, 
    # PrimaryColour=&H00FFFF (Stark vibrant yellow active word highlighting style), 
    # OutlineColour=&H000000 (Vibrant black outline), Outline=2, BorderStyle=1, MarginV=280 (Instagram UI Safezone)
    style = "Alignment=2,Fontname=Liberation Sans,Fontsize=24,PrimaryColour=&H00FFFF,OutlineColour=&H000000,Outline=2.5,BorderStyle=1,MarginV=280"
    
    # Ensure srt path is formatted correctly for FFmpeg subtitles filter
    srt_filter_path = SRT_INPUT.replace("\\", "/").replace(":", "\\:")
    ass_filter_path = ass_file.replace("\\", "/").replace(":", "\\:")
    
    cmd_subs = [
        "ffmpeg", "-y", "-i", temp_output,
        "-vf", f"ass={ass_filter_path},subtitles={srt_filter_path}:force_style='{style}'",
        "-c:v", "libx264", "-preset", "medium", "-b:v", "12M", "-maxrate", "14M", "-bufsize", "24M", "-r", "30",
        "-c:a", "copy", FINAL_REEL
    ]
    
    try:
        subprocess.run(cmd_subs, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.info(f"Prism-quality final reel exported to '{FINAL_REEL}'")
    except Exception as e:
        logger.error(f"Failed to burn subtitles: {e}")
        # In case subtitle filter fails due to missing font libraries, copy temp to final
        logger.warning("Subtitle burn failed. Falling back to copy video without subtitles.")
        import shutil
        shutil.copy(temp_output, FINAL_REEL)

    # Cleanup intermediate files to preserve disk space
    cleanup_temp_files()

def cleanup_temp_files():
    logger.info("Cleaning up temporary render components...")
    temp_patterns = ["raw_clip_", "norm_clip_", "clips.txt", "stitched_broll.mp4", "final_broll.mp4", "temp_reel_no_subs.mp4", "thumbnail.ass"]
    for file in os.listdir("."):
        for pattern in temp_patterns:
            if file.startswith(pattern):
                try:
                    os.remove(file)
                except OSError:
                    pass

def render():
    if not os.path.exists(SCRIPT_INPUT):
        logger.error(f"'{SCRIPT_INPUT}' not found. Cannot render video.")
        raise FileNotFoundError(f"Missing {SCRIPT_INPUT}")
        
    with open(SCRIPT_INPUT, "r", encoding="utf-8") as f:
        script_data = json.load(f)
        
    pexels_key = os.environ.get("PEXELS_API_KEY")
    if not pexels_key:
        logger.warning("PEXELS_API_KEY environment variable is missing! Using fallback background video.")
        duration = get_audio_duration()
        broll = generate_placeholder_video(duration)
    else:
        duration = get_audio_duration()
        downloaded = fetch_pexels_videos(script_data["pexels_keywords"], pexels_key)
        if downloaded:
            broll = normalize_and_stitch(downloaded, duration)
        else:
            broll = generate_placeholder_video(duration)
            
    thumbnail_text = script_data.get("thumbnail_text", "")
    compile_final_reel(broll, thumbnail_text)

if __name__ == "__main__":
    render()
