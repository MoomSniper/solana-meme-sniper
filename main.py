import os
import logging
import httpx
import asyncio
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

# Send message to Telegram
async def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_ID, "text": text}
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload)
    except Exception as e:
        logger.error(f"❌ Failed to send Telegram message: {e}")

# Market scan loop
async def scan_market_loop():
    while True:
        logger.info("⚡️ Scanning market for alpha...")
        await asyncio.sleep(44)

# Async post_init to launch scanner task
async def post_init(app):
    app.create_task(scan_market_loop())

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper bot activated and watching the market in Obsidian Mode.")

# Telegram bot setup
application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .post_init(post_init)
    .build()
)

application.add_handler(CommandHandler("start", start))

@app.route("/", methods=["GET"])
def index():
    return "Sniper bot is live."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    logger.info(f"📥 Incoming Telegram update: {data}")
    update = Update.de_json(data, application.bot)
    asyncio.create_task(application.process_update(update))
    return "OK"

# Run in webhook mode
if __name__ == "__main__":
    logger.info("✅ Telegram webhook set.")
    logger.info("🧠 Obsidian Mode active. Scanner running.")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", default=10000)),
        webhook_url=WEBHOOK_URL
    )
