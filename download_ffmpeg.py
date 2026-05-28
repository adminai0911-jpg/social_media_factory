import urllib.request
import zipfile
import os
import shutil

print("Downloading FFmpeg...")
url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
urllib.request.urlretrieve(url, "ffmpeg.zip")
print("Extracting FFmpeg...")
with zipfile.ZipFile("ffmpeg.zip", 'r') as zip_ref:
    zip_ref.extractall("ffmpeg_ext")

# Find the bin folder and move ffmpeg.exe and ffprobe.exe to current dir
for root, dirs, files in os.walk("ffmpeg_ext"):
    if "ffmpeg.exe" in files:
        shutil.move(os.path.join(root, "ffmpeg.exe"), "ffmpeg.exe")
    if "ffprobe.exe" in files:
        shutil.move(os.path.join(root, "ffprobe.exe"), "ffprobe.exe")

print("Cleaning up...")
os.remove("ffmpeg.zip")
shutil.rmtree("ffmpeg_ext")
print("Done.")
