"""
Ghost Handler — Human Timing Simulator
Generates random delays that match real human behavior patterns.
No bot has Gaussian-distributed action timing. This does.
"""
import random
import time
import datetime
import logging

logger = logging.getLogger("GhostTiming")

# IST active hours (24h format)
ACTIVE_START = 8   # 8 AM
ACTIVE_END   = 23  # 11 PM

def is_active_hours():
    """Check if current IST time is within human active hours."""
    now_utc = datetime.datetime.utcnow()
    now_ist = now_utc + datetime.timedelta(hours=5, minutes=30)
    return ACTIVE_START <= now_ist.hour < ACTIVE_END

def human_delay(min_sec=3, max_sec=15, label="action"):
    """
    Sleep for a random duration with Gaussian distribution.
    Real humans: fast sometimes, slow sometimes. Never perfectly uniform.
    """
    # Gaussian distribution feels more organic than uniform random
    mean = (min_sec + max_sec) / 2
    std  = (max_sec - min_sec) / 4
    delay = max(min_sec, min(max_sec, random.gauss(mean, std)))
    logger.info(f"⏳ [{label}] Waiting {delay:.1f}s (human pause)...")
    time.sleep(delay)

def session_pause():
    """Simulate a human getting distracted mid-session (2-8 min break)."""
    pause = random.randint(120, 480)
    logger.info(f"☕ Session break: {pause//60}m {pause%60}s (simulating human distraction)")
    time.sleep(pause)

def micro_pause():
    """Very short pause between micro-actions (reading, scrolling)."""
    time.sleep(random.uniform(0.8, 3.5))

def post_action_cooldown():
    """After posting something, humans browse a bit before next post."""
    delay = random.randint(45, 180)
    logger.info(f"🕐 Post-action cooldown: {delay}s")
    time.sleep(delay)

def get_daily_action_limit(platform, action_type):
    """
    Safe daily action limits per platform — NEVER exceed these.
    These are well below platform detection thresholds.
    """
    limits = {
        "instagram": {
            "like":    30,   # Safe: up to 60, we use 30
            "comment": 10,   # Safe: up to 20, we use 10
            "follow":  15,   # Safe: up to 30, we use 15
            "story":   5,    # Stories: always safe
        },
        "x": {
            "like":    50,   # Safe: up to 100, we use 50
            "reply":   20,   # Safe: up to 50, we use 20
            "follow":  10,   # Safe: up to 25, we use 10
            "tweet":   5,    # Including thread tweets
            "retweet": 5,
        },
        "youtube": {
            "like":    20,
            "comment": 5,
            "reply":   15,
        }
    }
    return limits.get(platform, {}).get(action_type, 5)

def jitter_time(base_hour, base_minute, variance_minutes=15):
    """
    Add random variance to posting times.
    Never post at exact same time every day — that's a bot fingerprint.
    """
    offset = random.randint(-variance_minutes, variance_minutes)
    total_minutes = base_hour * 60 + base_minute + offset
    hour = (total_minutes // 60) % 24
    minute = total_minutes % 60
    return hour, minute
