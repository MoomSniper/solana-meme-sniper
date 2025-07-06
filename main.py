import os
import asyncio
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes
)
import threading

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram and Webhook Setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))

application = Application.builder().token(BOT_TOKEN).build()
app = Flask(__name__)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def telegram_webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
    return "ok", 200

@app.route("/", methods=["GET"])
def root():
    return "Sniper Bot is Live", 200

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🚀 Sniper Bot Activated.")

application.add_handler(CommandHandler("start", start))

# Example scan loop (replace with your alpha logic)
async def scan_loop():
    while True:
        logger.info("⚡️ Scanning market for alpha...")
        # placeholder logic for now
        await asyncio.sleep(44)

# Run scan loop in background
def run_scan_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scan_loop())

# Boot everything
if __name__ == "__main__":
    logger.info("✅ Telegram webhook set.")
    logger.info("🧠 Obsidian Mode active. Scanner running.")

    threading.Thread(target=run_scan_loop, daemon=True).start()

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", default=10000)),
        webhook_url=WEBHOOK_URL
    )
