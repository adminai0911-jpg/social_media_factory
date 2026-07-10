import os
import shutil
import subprocess

def run(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True)

# 1. Unstage everything
run("git reset HEAD")

# 2. Aggressively delete the large files from disk so `git add .` can't find them
files_to_remove = ["ffmpeg.exe", "ffplay.exe", "ffprobe.exe", "ffmpeg.zip"]
for f in files_to_remove:
    try:
        os.remove(f)
        print(f"Deleted {f}")
    except OSError:
        pass

dirs_to_remove = ["ffmpeg_extracted"]
for d in dirs_to_remove:
    try:
        shutil.rmtree(d)
        print(f"Deleted directory {d}")
    except OSError:
        pass

# 3. Add all valid files
run("git add .")

# 4. Commit and Force Push
run('git commit -m "feat: add 100% free native linkedin and pinterest uploaders"')
run('git push origin fix-ytdlp-auth-pipeline -f')
