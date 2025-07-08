import time
import os
import requests
import logging
from telegram import Bot

# === BASIC CONFIG ===
TELEGRAM_ID = os.environ.get("TELEGRAM_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# === SETUP LOGGING ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
log = logging.getLogger()

# === TELEGRAM BOT SETUP ===
bot = Bot(token=BOT_TOKEN)

def send_telegram(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_ID, text=msg)
        log.info(f"Sent to Telegram: {msg}")
    except Exception as e:
        log.error(f"Failed to send Telegram message: {e}")

# === MAIN SCANNER ===
def run_sniper_sync():
    log.info("🟢 Sniper bot started.")
    send_telegram("🚀 Sniper bot is live and scanning...")

    while True:
        try:
            log.info("🔎 Scanning for new coins...")
            time.sleep(5)

            if int(time.time()) % 30 < 5:
                alert = f"🪙 Fake Coin Detected! MC: ${round(time.time() % 100000)}"
                send_telegram(alert)
        except Exception as e:
            log.error(f"Sniper error: {e}")
            send_telegram(f"❌ Sniper crashed: {e}")
            time.sleep(10)

async def run_sniper():
    import asyncio
    await asyncio.to_thread(run_sniper_sync)
