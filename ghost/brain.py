"""
Ghost Handler — BRAIN
The master orchestrator that runs all ghost modules in human-like sequence.

3 Sessions per day:
  Morning  (7:30 AM IST) → Post content + X thread + engage
  Midday   (12:30 PM IST) → Reply comments + like/follow
  Evening  (6:30 PM IST) → Post content + X thread + engage + reply

This file is the single entry point called from GitHub Actions.
"""
import os
import sys
import logging
import asyncio
import random
import requests
from ghost.timing import human_delay, session_pause, is_active_hours
from ghost.safety import get_today_stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - GHOST - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GhostBrain")

SESSION = os.environ.get("GHOST_SESSION", "morning")  # morning | midday | evening

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "")

def send_telegram(message):
    try:
        from ghost.notifications import broadcast_alert
        broadcast_alert(message)
    except Exception as e:
        logger.error(f"Failed to broadcast notification: {e}")


def run_morning_session():
    """
    Morning Session (7:30 AM IST):
    1. Post X viral thread
    2. X: Like niche posts + follow accounts
    3. Run main video content pipeline
    """
    logger.info("🌅 === MORNING SESSION STARTING ===")
    send_telegram("🌅 <b>Ghost Handler — Morning Session</b>\nStarting X thread + engagement...")
    
    results = {}
    
    # 1. Post X viral thread (text threads get massive reach in morning)
    logger.info("🧵 Step 1: Posting X viral thread...")
    try:
        from ghost.thread_engine import run as post_thread
        results["x_thread"] = post_thread()
        human_delay(60, 180, "after_thread")
    except Exception as e:
        logger.error(f"Thread engine failed: {e}")
        results["x_thread"] = False

    # 2. X engagement — likes + follows
    logger.info("❤️ Step 2: X engagement session...")
    try:
        from ghost.x_ghost import run as x_run
        results["x_engage"] = x_run(session="morning")
        human_delay(120, 300, "after_x_morning")
    except Exception as e:
        logger.error(f"X ghost failed: {e}")
        results["x_engage"] = {}

    # 3. Run main content pipeline
    logger.info("🎬 Step 3: Running content pipeline...")
    try:
        import subprocess
        proc = subprocess.run(
            [sys.executable, "orchestrator/v32_dopamine_engine.py"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True, text=True, timeout=1200
        )
        results["content_pipeline"] = proc.returncode == 0
        if proc.returncode != 0:
            logger.error(f"Content pipeline error: {proc.stderr[-500:]}")
    except Exception as e:
        logger.error(f"Content pipeline failed: {e}")
        results["content_pipeline"] = False

    # Send Telegram summary
    status = "\n".join([f"  {k}: {'✅' if v else '❌'}" for k, v in results.items()])
    send_telegram(f"🌅 <b>Morning Session Complete</b>\n{status}")
    logger.info(f"✅ Morning session done: {results}")
    return results

def run_midday_session():
    """
    Midday Session (12:30 PM IST):
    1. Reply to all comments (IG + FB + X mentions)
    2. X: Comment on viral posts in niche
    3. Follow more niche accounts
    """
    logger.info("☀️ === MIDDAY SESSION STARTING ===")
    send_telegram("☀️ <b>Ghost Handler — Midday Session</b>\nComment replies + engagement...")
    
    results = {}
    
    # 1. Reply to all comments
    logger.info("💬 Step 1: Replying to all comments...")
    try:
        from ghost.comment_bot import run as reply_comments
        results["comment_replies"] = reply_comments()
        human_delay(120, 300, "after_comments")
    except Exception as e:
        logger.error(f"Comment bot failed: {e}")
        results["comment_replies"] = 0

    # 2. X engagement — comment on viral posts
    logger.info("🔥 Step 2: X midday engagement...")
    try:
        from ghost.x_ghost import run as x_run
        results["x_engage"] = x_run(session="midday")
        human_delay(180, 400, "after_x_midday")
    except Exception as e:
        logger.error(f"X ghost failed: {e}")
        results["x_engage"] = {}

    status = "\n".join([f"  {k}: {'✅' if v else '❌'}" for k, v in results.items()])
    send_telegram(f"☀️ <b>Midday Session Complete</b>\n{status}")
    logger.info(f"✅ Midday session done: {results}")
    return results

def run_evening_session():
    """
    Evening Session (6:30 PM IST — PEAK TRAFFIC TIME):
    1. Post second video of the day
    2. Post evening X thread
    3. X: Like + reply engagement
    4. Reply to comments accumulated during the day
    """
    logger.info("🌆 === EVENING SESSION STARTING ===")
    send_telegram("🌆 <b>Ghost Handler — Evening Session</b>\nPeak hour content + engagement...")
    
    results = {}
    
    # 1. Run content pipeline again (second video of day)
    logger.info("🎬 Step 1: Evening content pipeline...")
    try:
        import subprocess
        proc = subprocess.run(
            [sys.executable, "orchestrator/v32_dopamine_engine.py"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            capture_output=True, text=True, timeout=1200
        )
        results["content_pipeline"] = proc.returncode == 0
    except Exception as e:
        logger.error(f"Content pipeline failed: {e}")
        results["content_pipeline"] = False

    human_delay(120, 300, "after_evening_video")

    # 2. Evening X thread
    logger.info("🧵 Step 2: Evening X thread...")
    try:
        from ghost.thread_engine import run as post_thread
        results["x_thread"] = post_thread()
        human_delay(60, 180, "after_evening_thread")
    except Exception as e:
        logger.error(f"Thread engine failed: {e}")
        results["x_thread"] = False

    # 3. X evening engagement
    logger.info("❤️ Step 3: X evening engagement...")
    try:
        from ghost.x_ghost import run as x_run
        results["x_engage"] = x_run(session="evening")
        human_delay(180, 400, "after_x_evening")
    except Exception as e:
        logger.error(f"X ghost failed: {e}")
        results["x_engage"] = {}

    # 4. Reply to any new comments
    logger.info("💬 Step 4: Evening comment replies...")
    try:
        from ghost.comment_bot import run as reply_comments
        results["comment_replies"] = reply_comments()
    except Exception as e:
        logger.error(f"Comment bot failed: {e}")
        results["comment_replies"] = 0

    # Final stats
    stats = get_today_stats()
    status = "\n".join([f"  {k}: {'✅' if v else '❌'}" for k, v in results.items()])
    send_telegram(f"🌆 <b>Evening Session Complete</b>\n{status}\n\n<pre>{stats}</pre>")
    logger.info(f"✅ Evening session done: {results}")
    logger.info(f"\n{stats}")
    return results

if __name__ == "__main__":
    logger.info(f"🤖 Ghost Handler Brain starting — Session: {SESSION}")
    
    if SESSION == "morning":
        run_morning_session()
    elif SESSION == "midday":
        run_midday_session()
    elif SESSION == "evening":
        run_evening_session()
    else:
        logger.error(f"Unknown session: {SESSION}")
        sys.exit(1)
