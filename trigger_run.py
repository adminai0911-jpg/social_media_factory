import urllib.request
import json

# Trigger a manual workflow_dispatch run on main
url = "https://api.github.com/repos/adminai0911-jpg/social_media_factory/actions/workflows/autopilot_server.yml/dispatches"
req = urllib.request.Request(url, method="POST")
req.add_header("Authorization", "token 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")
req.add_header("User-Agent", "Python-urllib")
req.add_header("Accept", "application/vnd.github+json")
req.add_header("Content-Type", "application/json")

payload = json.dumps({"ref": "main"}).encode()

try:
    with urllib.request.urlopen(req, data=payload) as response:
        print(f"Trigger response code: {response.getcode()} - Run dispatched!")
except Exception as e:
    print("Error:", e)
