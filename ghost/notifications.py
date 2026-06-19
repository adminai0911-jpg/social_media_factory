"""
Ghost Handler — Universal Notification Engine
Broadcasts alerts to Telegram, Discord, and WhatsApp (via CallMeBot).
"""
import os
import requests
import logging
import urllib.parse

logger = logging.getLogger("Notifications")

def broadcast_alert(message):
    """
    Broadcasts message to Telegram, Discord, and WhatsApp (CallMeBot) if credentials exist.
    """
    # Create clean text for Discord / WhatsApp
    plain_message = message.replace("<b>", "").replace("</b>", "").replace("<pre>", "").replace("</pre>", "")
    
    # 1. Telegram Alert
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if bot_token and chat_id:
        try:
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                data={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
                timeout=10
            )
            logger.info("Notification sent to Telegram.")
        except Exception as e:
            logger.warning(f"Telegram alert failed: {e}")

    # 2. Discord Alert (100% Free)
    discord_webhook = os.environ.get("DISCORD_WEBHOOK_URL", "")
    if discord_webhook:
        try:
            requests.post(
                discord_webhook,
                json={"content": plain_message},
                timeout=10
            )
            logger.info("Notification sent to Discord.")
        except Exception as e:
            logger.warning(f"Discord alert failed: {e}")

    # 3. WhatsApp Alert (via CallMeBot - 100% Free Gateway)
    callmebot_key = os.environ.get("CALLMEBOT_API_KEY", "")
    callmebot_phone = os.environ.get("CALLMEBOT_PHONE", "")  # e.g., +919876543210
    
    if callmebot_key and callmebot_phone:
        try:
            encoded_text = urllib.parse.quote(plain_message)
            url = f"https://api.callmebot.com/whatsapp.php?phone={callmebot_phone}&text={encoded_text}&apikey={callmebot_key}"
            resp = requests.get(url, timeout=15)
            if resp.status_code == 200:
                logger.info("Notification sent to WhatsApp via CallMeBot.")
            else:
                logger.warning(f"CallMeBot responded with status: {resp.status_code}")
        except Exception as e:
            logger.warning(f"CallMeBot WhatsApp alert failed: {e}")
