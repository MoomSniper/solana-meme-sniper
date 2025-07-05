import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

# === Environment Variables ===
BOT_TOKEN = os.environ["BOT_TOKEN"]
TELEGRAM_USER_ID = int(os.environ["TELEGRAM_ID"])
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Flask App ===
app = Flask(__name__)

# === Telegram Bot App ===
application = Application.builder().token(BOT_TOKEN).build()

# === Telegram Commands ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Sniper Bot Webhook is live and working.")

application.add_handler(CommandHandler("start", start))

# === Flask Webhook Endpoint ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, application.bot)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.initialize())
        loop.run_until_complete(application.process_update(update))
        return "OK"
    except Exception as e:
        logger.exception(f"❌ Exception in telegram_webhook: {e}")
        return "ERROR"

# === Set Webhook When Script Starts ===
async def set_webhook():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(set_webhook())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
