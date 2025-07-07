import logging
import os
import httpx
import threading
import time
from flask import Flask, request
from telegram import Bot
from telegram.ext import Application, CommandHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(token=TOKEN)
application = Application.builder().token(TOKEN).build()

app = Flask(__name__)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json(force=True)
    application.update_queue.put(update)
    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "Bot is alive."

async def start(update, context):
    await update.message.reply_text("Obsidian Mode is active.")

application.add_handler(CommandHandler("start", start))

async def setup_webhook():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    logger.info("✅ Telegram webhook set.")

def scan_dexscreener():
    url = "https://dexscreener.com/solana"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://dexscreener.com/"
    }
    try:
        with httpx.Client(http2=True, timeout=10) as client:
            res = client.get(url, headers=headers)
            if res.status_code == 200:
                logger.info("✅ Dexscreener response received.")
            else:
                logger.warning(f"⚠️ Dexscreener returned status {res.status_code}")
    except Exception as e:
        logger.error(f"❌ Dexscreener fetch failed: {e}")

def run_scanner():
    logger.info("🧠 Obsidian Mode active. Scanner running.")
    while True:
        scan_dexscreener()
        time.sleep(5)  # adjust scan frequency here

if __name__ == "__main__":
    threading.Thread(target=run_scanner, daemon=True).start()
    import asyncio
    asyncio.run(setup_webhook())
    application.run_polling()
