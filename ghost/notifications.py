"""
Ghost Handler — Universal Notification Engine
Broadcasts alerts to Telegram, Discord, and WhatsApp.
"""
import os
import requests
import logging

logger = logging.getLogger("Notifications")

def broadcast_alert(message):
    """
    Broadcasts message to Telegram, Discord, and WhatsApp (Twilio) if credentials exist.
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

    # 2. Discord Alert
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

    # 3. WhatsApp Alert (via Twilio Sandbox or API)
    twilio_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
    twilio_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
    twilio_to = os.environ.get("TWILIO_TO_NUMBER", "")      # Must start with whatsapp:
    twilio_from = os.environ.get("TWILIO_FROM_NUMBER", "whatsapp:+14155238886")
    
    if twilio_sid and twilio_token and twilio_to:
        try:
            # Ensure "whatsapp:" prefix
            to_number = twilio_to if twilio_to.startswith("whatsapp:") else f"whatsapp:{twilio_to}"
            from_number = twilio_from if twilio_from.startswith("whatsapp:") else f"whatsapp:{twilio_from}"
            
            url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
            resp = requests.post(
                url,
                auth=(twilio_sid, twilio_token),
                data={
                    "From": from_number,
                    "To": to_number,
                    "Body": plain_message
                },
                timeout=10
            )
            if resp.status_code == 201:
                logger.info("Notification sent to WhatsApp via Twilio.")
            else:
                logger.warning(f"Twilio API responded with: {resp.text}")
        except Exception as e:
            logger.warning(f"Twilio WhatsApp alert failed: {e}")
