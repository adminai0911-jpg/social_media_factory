import os
import subprocess

def run(cmd):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True)

run("git reset HEAD~1")
run('git rm --cached ffmpeg.exe ffplay.exe ffprobe.exe ffmpeg.zip -f')
run('git rm --cached -r ffmpeg_extracted -f')
run('git add .')
run('git commit -m "feat: add 100% free native linkedin and pinterest uploaders"')
run('git push origin fix-ytdlp-auth-pipeline -f')
