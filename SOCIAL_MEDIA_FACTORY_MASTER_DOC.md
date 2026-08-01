# 🏭 Omni-Channel Social Media Factory: Master Architecture Document

**Version:** V36 Engine (100% Cloud-Native)
**Location:** GitHub Actions (`.github/workflows/autopilot_server.yml`)

This document serves as the absolute source of truth for the entire architecture of your Viral Autopilot Factory.

---

## 1. The Core Pipeline (How It Works)
The factory is a fully automated, headless video generation and distribution system. It runs 100% free on GitHub Actions without any external SaaS fees (no Make.com, no Ayrshare).

### Step-by-Step Flow:
1. **The Cron Trigger:** GitHub Actions wakes up (`autopilot_server.yml`) daily at the scheduled time.
2. **The Jitter Delay:** A random sleep timer (5 to 60 minutes) executes to prevent Instagram/YouTube from detecting a bot pattern.
3. **The Dopamine Engine (`orchestrator/v32_dopamine_engine.py`):**
   * Selects a random AI personality (e.g., Analytical, Contrarian).
   * Generates a 30-40 second viral script about wealth/finance using Gemini 1.5.
   * Scrapes 1080p background footage from Pexels using deep-paginated, randomized search queries.
   * Generates a compelling AI voiceover.
4. **The Remotion Studio (`remotion-studio/`):**
   * Compiles the background video, voiceover, animated captions (with highlighted keywords), sound effects (risers, impacts), and a monetization CTA into a final `FINAL_V35_HD.mp4`.
5. **The Omni-Uploader (`uploader.py`):**
   * Blasts the final HD video out to YouTube Shorts, Instagram Reels, Facebook Reels, Telegram, LinkedIn, and Pinterest using their official APIs.
   * Applies Exponential Backoff (`@with_retry`) to ensure network glitches don't crash the pipeline.
6. **The Omni-Engagement Bot (`engagement_bot.py`):**
   * Scans previous videos on YouTube, Facebook, and Instagram for new comments.
   * Instantly writes natural AI replies to the fans, triggering algorithmic distribution.

---

## 2. The Cloud Environment (GitHub Actions)

The factory is completely dependent on the **Secrets** stored in your GitHub Repository (`Settings > Secrets and variables > Actions`). If you ever migrate this repo, you MUST copy these exact keys over:

| Platform | Required Keys | Purpose |
| :--- | :--- | :--- |
| **Google/Gemini** | `GEMINI_API_KEY`, `GEMINI_API_KEY_2`, `GEMINI_API_KEY_3` | Rotated keys for script generation. |
| **Pexels** | `PEXELS_API_KEY` | Fetches HD background videos. |
| **Meta (FB/IG)** | `META_USER_ACCESS_TOKEN`, `FACEBOOK_PAGE_ID`, `INSTAGRAM_BUSINESS_ACCOUNT_ID` | Posts Reels and Stories. |
| **YouTube** | `YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN` | Uploads Shorts & replies to comments. |
| **LinkedIn** | `LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_AUTHOR_URN` | Uploads via UGC Post API. |
| **Pinterest** | `PINTEREST_ACCESS_TOKEN`, `PINTEREST_BOARD_ID` | Pins the video to your board. |
| **Telegram** | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Distributes directly to your community. |
| **Discord** | `DISCORD_WEBHOOK_URL` | Sends you alerts if the factory crashes. |

---

## 3. Core Files (Do Not Delete)

* **`.github/workflows/autopilot_server.yml`**: The master server file that orchestrates everything.
* **`orchestrator/v32_dopamine_engine.py`**: The brain of the operation. Handles AI generation, asset downloading, and Remotion orchestration.
* **`remotion-studio/`**: The React-based video editing engine. 
* **`uploader.py`**: The master distribution script.
* **`linkedin_uploader.py` / `pinterest_uploader.py`**: Sub-modules for specific platform APIs.
* **`engagement_bot.py`**: The community manager AI.
* **`cover.jpg`**: Fallback thumbnail image.

---

## 4. Maintenance & Troubleshooting

1. **"The factory didn't post today"**
   * Go to GitHub -> Actions tab. Check the latest run log.
   * If an API Key expired (e.g., Meta Access Token), you must regenerate it in the Developer Portal and paste it back into GitHub Secrets.
2. **"The videos are too similar"**
   * Modify the `AI_PERSONAS` or the `pexel_queries` list inside `orchestrator/v32_dopamine_engine.py`.
3. **"I want to change the posting time"**
   * Edit the `cron:` schedule in `.github/workflows/autopilot_server.yml`. Remember that cron is in UTC time (IST minus 5.5 hours).

> [!IMPORTANT]
> This repository is now entirely cloud-native. Do not attempt to run it locally using `.bat` files. To trigger a test run, go to **GitHub > Actions > Run workflow**.
