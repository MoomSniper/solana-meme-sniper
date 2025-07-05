import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

import asyncio
import httpx

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Env vars
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# Flask app
app = Flask(__name__)

# Telegram App
application = Application.builder().token(BOT_TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 God Mode Meme Sniper Activated.")

# Register command
application.add_handler(CommandHandler("start", start))

# Notify on startup
async def notify_on_startup():
    async with httpx.AsyncClient() as client:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_ID, "text": "✅ Sniper Bot Deployed & Live via Webhook"}
        await client.post(url, json=payload)

# Set webhook on startup
async def setup_webhook():
    async with httpx.AsyncClient() as client:
        await client.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            params={"url": f"{WEBHOOK_URL}/{BOT_TOKEN}"}
        )
        logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{BOT_TOKEN}")

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def telegram_webhook():
    data = request.get_data().decode("utf-8")
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "OK"

# Root test route
@app.route("/", methods=["GET", "HEAD"])
def index():
    return "Sniper Bot Running"

# Entry point
if __name__ == "__main__":
    async def run():
        await setup_webhook()
        await notify_on_startup()
        app.run(host="0.0.0.0", port=PORT)

    asyncio.run(run())
