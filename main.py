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

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Flask app for webhook
app = Flask(__name__)

# Telegram message sender
async def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_ID, "text": text}
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload)
    except Exception as e:
        logger.error(f"❌ Failed to send Telegram message: {e}")

# Scanner loop
async def scan_market_loop():
    while True:
        logger.info("⚡️ Scanning market for alpha...")
        # Put real scanning logic here
        await asyncio.sleep(44)  # Respect API quota

# Proper post_init function (called when loop is running)
async def launch_tasks(app):
    app.create_task(scan_market_loop())

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper bot activated and watching the market in Obsidian Mode.")

# Set up the Telegram bot app
application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .post_init(launch_tasks)
    .build()
)

# Register command
application.add_handler(CommandHandler("start", start))

# Flask route to show status
@app.route("/", methods=["GET"])
def index():
    return "Sniper bot is live."

# Webhook endpoint
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    logger.info(f"📥 Incoming Telegram update: {data}")
    application.update_queue.put_nowait(Update.de_json(data, application.bot))
    return "OK"

# Run the bot in webhook mode
if __name__ == "__main__":
    logger.info("✅ Telegram webhook set.")
    logger.info("🧠 Obsidian Mode active. Scanner running.")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", default=10000)),
        webhook_url=WEBHOOK_URL
    )
