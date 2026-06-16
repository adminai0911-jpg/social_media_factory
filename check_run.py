import urllib.request
import json
import time

url = "https://api.github.com/repos/adminai0911-jpg/social_media_factory/actions/runs?per_page=5"
req = urllib.request.Request(url)
req.add_header("Authorization", "token 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")
req.add_header("User-Agent", "Python-urllib")
req.add_header("Accept", "application/vnd.github+json")

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        for run in data.get("workflow_runs", []):
            print(f"Run ID: {run['id']}, Status: {run['status']}, Conclusion: {run['conclusion']}, Created at: {run['created_at']}")
except Exception as e:
    print("Error:", e)
