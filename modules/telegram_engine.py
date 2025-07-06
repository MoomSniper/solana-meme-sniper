import os
import requests
import logging

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")

def send_telegram_alert(message: str):
    if not BOT_TOKEN or not TELEGRAM_ID:
        logging.error("[Telegram] Missing BOT_TOKEN or TELEGRAM_ID in env")
        return

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            logging.warning(f"[Telegram] ❌ Failed to send alert: {response.text}")
    except Exception as e:
        logging.error(f"[Telegram] ❌ Error: {e}")

def setup_telegram_commands(application):
    # Placeholder: add real command handlers later if needed
    print("✅ Telegram commands are ready (placeholder)")

from telegram import Bot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

async def send_message(chat_id, text):
    await bot.send_message(chat_id=chat_id, text=text)
