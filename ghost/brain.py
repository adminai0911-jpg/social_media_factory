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


def format_detailed_report(session_name, results):
    lines = [f"🤖 <b>Ghost Handler — {session_name} Complete</b>"]
    
    # Check comment replies
    if "comment_replies" in results and isinstance(results["comment_replies"], dict):
        cr = results["comment_replies"]
        total_replies = len(cr.get("youtube", [])) + len(cr.get("instagram", [])) + len(cr.get("facebook", []))
        if total_replies > 0:
            lines.append("\n💬 <b>Comment Replies Posted:</b>")
            for plat, lst in cr.items():
                if lst:
                    lines.append(f"  <b>{plat.capitalize()}:</b>")
                    for item in lst[:5]:
                        lines.append(f"    • {item}")
        else:
            lines.append("\n💬 No comment replies posted.")
            
    # Check thread
    if "x_thread" in results:
        lines.append(f"\n🧵 <b>X Thread:</b> {'✅ Posted Successfully' if results['x_thread'] else '❌ Failed / Skipped'}")

    # Check X engagement
    if "x_engage" in results and isinstance(results["x_engage"], dict):
        xe = results["x_engage"]
        has_engage = False
        if xe.get("liked"):
            has_engage = True
            lines.append("\n❤️ <b>X Niche Likes:</b>")
            for item in xe["liked"][:5]:
                lines.append(f"    • {item}")
        if xe.get("replied"):
            has_engage = True
            lines.append("\n💬 <b>X Mentions Replied:</b>")
            for item in xe["replied"][:5]:
                lines.append(f"    • {item}")
        if xe.get("commented"):
            has_engage = True
            lines.append("\n🔥 <b>X Viral Comments:</b>")
            for item in xe["commented"][:5]:
                lines.append(f"    • {item}")
        if xe.get("followed"):
            has_engage = True
            lines.append("\n➕ <b>X Niche Follows:</b>")
            for item in xe["followed"][:5]:
                lines.append(f"    • {item}")
        if not has_engage:
            lines.append("\n❤️ No X engagement actions taken.")
            
    # Check IG proactive
    if "ig_proactive" in results and isinstance(results["ig_proactive"], dict):
        igp = results["ig_proactive"]
        if igp.get("liked"):
            lines.append("\n❤️ <b>IG Proactive Likes:</b>")
            for item in igp["liked"][:5]: lines.append(f"    • {item}")
        if igp.get("commented"):
            lines.append("\n💬 <b>IG Proactive Comments:</b>")
            for item in igp["commented"][:5]: lines.append(f"    • {item}")

    # Check YT proactive
    if "yt_proactive" in results and isinstance(results["yt_proactive"], dict):
        ytp = results["yt_proactive"]
        if ytp.get("commented"):
            lines.append("\n▶️ <b>YT Proactive Comments:</b>")
            for item in ytp["commented"][:5]: lines.append(f"    • {item}")
                
    return "\n".join(lines)


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

    report = format_detailed_report("🌅 Morning Session", results)
    send_telegram(report)
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
        results["comment_replies"] = {}

    # 2. X engagement — comment on viral posts
    logger.info("🔥 Step 2: X midday engagement...")
    try:
        from ghost.x_ghost import run as x_run
        results["x_engage"] = x_run(session="midday")
        human_delay(180, 400, "after_x_midday")
    except Exception as e:
        logger.error(f"X ghost failed: {e}")
        results["x_engage"] = {}

    # 3. IG Proactive Engagement
    logger.info("📸 Step 3: IG Proactive engagement...")
    try:
        from ghost.ig_ghost import run_ig_proactive_session
        results["ig_proactive"] = run_ig_proactive_session(session="midday")
        human_delay(120, 300, "after_ig_midday")
    except Exception as e:
        logger.error(f"IG ghost failed: {e}")
        results["ig_proactive"] = {}

    # 4. YT Proactive Engagement
    logger.info("▶️ Step 4: YT Proactive engagement...")
    try:
        from ghost.yt_ghost import run_yt_proactive_session
        results["yt_proactive"] = run_yt_proactive_session(session="midday")
    except Exception as e:
        logger.error(f"YT ghost failed: {e}")
        results["yt_proactive"] = {}

    report = format_detailed_report("☀️ Midday Session", results)
    send_telegram(report)
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
        results["comment_replies"] = {}

    # 5. IG + YT Evening Proactive
    logger.info("📸 Step 5: IG & YT Proactive evening...")
    try:
        from ghost.ig_ghost import run_ig_proactive_session
        results["ig_proactive"] = run_ig_proactive_session(session="evening")
        from ghost.yt_ghost import run_yt_proactive_session
        results["yt_proactive"] = run_yt_proactive_session(session="evening")
    except Exception as e:
        logger.error(f"IG/YT ghost failed: {e}")
        results["ig_proactive"] = {}
        results["yt_proactive"] = {}

    # Final stats
    stats = get_today_stats()
    report = format_detailed_report("🌆 Evening Session", results)
    send_telegram(f"{report}\n\n<pre>{stats}</pre>")
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
