import os
import asyncio
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# Load environment variables
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
TELEGRAM_ID = int(os.environ["TELEGRAM_ID"])

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app for webhook
app = Flask(__name__)
application = None

# === Telegram Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Sniper bot is locked in and scanning alpha. Buckle up.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if text == "ping":
        await update.message.reply_text("✅ Bot is alive and running.")
    else:
        await update.message.reply_text("👀 Scanning... type 'ping' to check status.")

# === Alpha Scanner Placeholder ===
async def scan_and_alert():
    while True:
        # Replace this with real sniper logic
        # Example: fetch new coins, check filters, send alert
        logger.info("Scanning for alpha coins...")
        await asyncio.sleep(10)

# === Webhook Endpoint ===
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
async def webhook():
    if request.method == "POST":
        await application.update_queue.put(Update.de_json(request.get_json(force=True), application.bot))
        return "ok"

# === Runner ===
async def main():
    global application
    application = ApplicationBuilder().token(BOT_TOKEN).concurrent_updates(True).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info("🚀 Webhook set and bot started.")

    # Run alpha scanner in background
    asyncio.create_task(scan_and_alert())

# Start Flask and Telegram together
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    Thread(target=lambda: app.run(host="0.0.0.0", port=10000)).start()
    loop.run_forever()
