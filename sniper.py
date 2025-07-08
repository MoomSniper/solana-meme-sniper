
import time
import logging
import asyncio
from telegram import Bot
import os

TELEGRAM_ID = os.environ.get("TELEGRAM_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
log = logging.getLogger()

async def send_telegram(msg):
    try:
        await bot.send_message(chat_id=TELEGRAM_ID, text=msg)
        log.info(f"Sent to Telegram: {msg}")
    except Exception as e:
        log.error(f"Telegram error: {e}")

async def run_sniper():
    log.info("🟢 Sniper bot started.")
    await send_telegram("🚀 Sniper bot is live and scanning...")

    while True:
        try:
            log.info("🔎 Scanning for new coins...")
            await asyncio.sleep(5)

            if int(time.time()) % 30 < 5:
                alert = f"🪙 Fake Coin Detected! MC: ${round(time.time() % 100000)}"
                await send_telegram(alert)
        except Exception as e:
            log.error(f"Sniper error: {e}")
            await send_telegram(f"❌ Sniper crashed: {e}")
            await asyncio.sleep(10)
