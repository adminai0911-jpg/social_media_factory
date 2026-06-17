import subprocess
import json

queries = [
    "satisfying loop shorts hd",
    "kinetic sand slicing asmr shorts",
    "luxury cars cinematic 4k shorts",
    "abstract 3d loop blender shorts",
    "relaxing nature drone 4k shorts",
    "gta v parkour gameplay shorts",
    "fluid simulation loop satisfying shorts",
    "asmr soap cutting satisfying shorts",
    "cyberpunk city rain loop shorts",
    "space galaxy stars loop shorts",
    "satisfying factory machine loop shorts"
]

all_urls = []

for q in queries:
    try:
        print(f"Searching: {q}")
        res = subprocess.run(
            ["python", "-m", "yt_dlp", f"ytsearch8:{q}", "--get-id", "--match-filter", "duration < 180"],
            capture_output=True, text=True
        )
        for vid in res.stdout.strip().split('\n'):
            if len(vid) == 11:
                all_urls.append(f"https://www.youtube.com/shorts/{vid}")
    except Exception as e:
        pass

all_urls = list(set(all_urls))
print(f"Found {len(all_urls)} URLs.")

with open('urls_dump.txt', 'w') as f:
    for u in all_urls:
        f.write(f'        "{u}",\n')

print("Wrote to urls_dump.txt")
