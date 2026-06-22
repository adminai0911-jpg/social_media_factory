"""
Ghost Handler — BRAIN
Simplified to only run comment replies.
Proactive handlers (X, IG, YT) and X thread removed.
"""
import os
import sys
import logging
import asyncio
from ghost.timing import is_active_hours
from ghost.safety import get_today_stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - GHOST - %(levelname)s - %(message)s"
)
logger = logging.getLogger("GhostBrain")

SESSION = os.environ.get("GHOST_SESSION", "morning")

def send_telegram(message):
    try:
        from ghost.notifications import broadcast_alert
        broadcast_alert(message)
    except Exception as e:
        logger.error(f"Failed to broadcast notification: {e}")

def run_session(session_name):
    logger.info(f"=== {session_name.upper()} SESSION STARTING ===")
    send_telegram(f"🤖 <b>Ghost Handler — {session_name.capitalize()} Session</b>\nChecking for comments...")
    
    results = {}
    
    try:
        from ghost.comment_bot import run as reply_comments
        results["comment_replies"] = reply_comments()
    except Exception as e:
        logger.error(f"Comment bot failed: {e}")
        results["comment_replies"] = {}

    cr = results.get("comment_replies", {})
    total = len(cr.get("youtube", [])) + len(cr.get("instagram", [])) + len(cr.get("facebook", []))
    
    report = f"🤖 <b>Ghost Handler — {session_name.capitalize()} Complete</b>\n\n"
    if total > 0:
        report += "💬 <b>Comment Replies Posted:</b>\n"
        for plat, lst in cr.items():
            if lst:
                report += f"  <b>{plat.capitalize()}:</b>\n"
                for item in lst[:5]:
                    report += f"    • {item}\n"
    else:
        report += "💬 No comment replies posted.\n"
        
    send_telegram(report)
    logger.info(f"✅ Session done.")

if __name__ == "__main__":
    logger.info(f"🤖 Ghost Handler Brain starting — Session: {SESSION}")
    
    if not is_active_hours():
        logger.warning("😴 Not active hours (night time). Ghost is sleeping.")
        send_telegram("😴 <b>Ghost Handler</b>\nNight time detected. Resting.")
        sys.exit(0)
        
    run_session(SESSION)

