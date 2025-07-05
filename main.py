import os
import asyncio
import logging
from threading import Thread
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# === Load environment variables ===
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
TELEGRAM_USER_ID = int(os.environ["telegram_id"])

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Flask App ===
app = Flask(__name__)
application = None

# === Telegram Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Sniper bot is locked in and scanning. Say 'watch' to heat up the radar.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower()

    if msg == "watch":
        await update.message.reply_text("👀 Watching coins that are heating up...")
    elif msg == "in":
        await update.message.reply_text("📈 Entering position. Bot tracking price action.")
    elif msg == "out":
        await update.message.reply_text("🚪 Exiting position. Profits (or damage) recorded.")
    else:
        await update.message.reply_text("❓ Command not recognized. Try: watch, in, or out.")

# === Fixed Flask route to receive Telegram webhooks ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.process_update(update))
    return "OK"

# === Main async setup ===
async def main():
    global application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Start Flask server in a separate thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=10000)).start()

    # Delay to make sure Flask is up
    await asyncio.sleep(2)

    # Set Telegram webhook
    url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    try:
        res = await application.bot.set_webhook(url=url)
        logger.info(f"✅ Webhook set: {url} — Telegram response: {res}")
    except Exception as e:
        logger.error(f"❌ Failed to set webhook: {e}")

if __name__ == "__main__":
    asyncio.run(main())
