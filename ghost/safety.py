"""
Ghost Handler — Safety Engine
Anti-ban rate limiter. Tracks all actions per platform per day.
Automatically slows down or stops if approaching limits.
"""
import os
import json
import datetime
import logging
from ghost.timing import get_daily_action_limit

logger = logging.getLogger("GhostSafety")

STATE_FILE = "/tmp/ghost_state.json"

def _load_state():
    """Load today's action counters from temp state file."""
    today = datetime.date.today().isoformat()
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                state = json.load(f)
            if state.get("date") == today:
                return state
        except Exception:
            pass
    # New day or corrupted — reset
    return {"date": today, "actions": {}}

def _save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        logger.warning(f"Could not save ghost state: {e}")

def can_act(platform, action_type):
    """
    Check if we are allowed to perform this action today.
    Returns True if safe, False if limit reached.
    """
    state = _load_state()
    key = f"{platform}_{action_type}"
    current = state["actions"].get(key, 0)
    limit = get_daily_action_limit(platform, action_type)
    
    if current >= limit:
        logger.warning(f"🛑 [{platform}:{action_type}] Daily limit reached ({current}/{limit}). Skipping.")
        return False
    
    remaining = limit - current
    logger.info(f"✅ [{platform}:{action_type}] Allowed. Used {current}/{limit} today ({remaining} remaining)")
    return True

def record_action(platform, action_type, count=1):
    """Record that we performed an action."""
    state = _load_state()
    key = f"{platform}_{action_type}"
    state["actions"][key] = state["actions"].get(key, 0) + count
    _save_state(state)
    logger.info(f"📊 [{platform}:{action_type}] Count: {state['actions'][key]}")

def get_today_stats():
    """Return all today's action counts as a formatted string."""
    state = _load_state()
    if not state["actions"]:
        return "No actions recorded today."
    lines = [f"📊 Ghost Stats — {state['date']}"]
    for key, count in sorted(state["actions"].items()):
        platform, action = key.split("_", 1)
        limit = get_daily_action_limit(platform, action)
        bar = "█" * min(10, int(10 * count / max(limit, 1)))
        lines.append(f"  {platform:12} {action:10} {bar:10} {count}/{limit}")
    return "\n".join(lines)
