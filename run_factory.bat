@echo off
cd /d "C:\Users\drsau\.gemini\antigravity-ide\scratch\social_media_factory"
echo Starting Autonomous Factory Run at %date% %time% >> factory_logs.txt
.\venv\Scripts\python.exe main.py >> factory_logs.txt 2>&1
echo Finished Run at %date% %time% >> factory_logs.txt
