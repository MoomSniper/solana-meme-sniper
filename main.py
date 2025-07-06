import os
import logging
import time
import httpx
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)

async def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_ID, "text": text}
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload)
    except Exception as e:
        logger.error(f"❌ Failed to send Telegram message: {e}")

async def scan_market():
    logger.info("⚡️ Scanning market for alpha...")
    # Placeholder logic
    # Replace this with real logic when ready
    pass

@app.route("/", methods=["GET"])
def index():
    return "Sniper bot is running."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    application.update_queue.put_nowait(Update.de_json(data, application.bot))
    return "OK"

# Telegram Bot Setup
application = ApplicationBuilder().token(BOT_TOKEN).build()

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper bot activated and watching the market in Obsidian Mode.")

application.add_handler(CommandHandler("start", start))

# Webhook mode
if __name__ == "__main__":
    logger.info("✅ Telegram webhook set.")
    logger.info("🧠 Obsidian Mode active. Scanner running.")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", default=10000)),
        webhook_url=WEBHOOK_URL
    )

    while True:
        try:
            time.sleep(44)
            import asyncio
            asyncio.run(scan_market())
        except Exception as e:
            logger.error(f"❌ Error during market scan: {e}")
