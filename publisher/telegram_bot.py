import os
import requests
import logging

logger = logging.getLogger("TelegramSentinel")

def send_telegram_alert(message):
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        logger.warning("Telegram Bot Token or Chat ID is missing. Skipping Telegram alert.")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Telegram alert sent successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to send Telegram alert: {e}")
        return False

if __name__ == "__main__":
    import sys
    msg = sys.argv[1] if len(sys.argv) > 1 else "🤖 Test Alert from The Factory."
    send_telegram_alert(msg)
