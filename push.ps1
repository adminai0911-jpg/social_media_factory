Set-Location "C:\Users\drsau\.gemini\antigravity-ide\scratch\Viral_Autopilot_Factory"
git add -A
git commit -m "DUAL-RUNNER ARCHITECTURE: Add buffer queue system

- orchestrator/generate_video.py: Renders video + uploads to GitHub Release buffer
- orchestrator/post_video.py: Lightweight poster that pops oldest video from buffer
- .github/workflows/1_pc_generator.yml: Self-hosted runner, Mon-Fri 9-7, Sat 9-3
- .github/workflows/2_cloud_poster.yml: GitHub cloud poster 3x daily (free)

This makes the system 100% free forever:
- Heavy rendering happens on your PC (zero cost)
- Lightweight posting (60s/run) runs on GitHub cloud (uses <5% of 2000 free min/month)
- Buffer queue holds 15 videos so posting continues even when PC is off"
git push origin main
Write-Host "DONE!"
