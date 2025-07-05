import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler
)
import asyncio

from sniper import sniper_loop

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask App
app = Flask(__name__)

# Telegram Bot Setup
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
application = ApplicationBuilder().token(BOT_TOKEN).build()

# /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper Bot is active and listening.")
    logger.info("✅ Bot started by user")
    application.create_task(sniper_loop())

application.add_handler(CommandHandler("start", start))

# Webhook Endpoint
@app.post(f"/{BOT_TOKEN}")
async def webhook() -> str:
    data = await request.get_data()
    update = Update.de_json(data.decode("utf-8"), application.bot)
    await application.process_update(update)
    return "ok"

# App Init
async def main():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info("✅ Webhook set and bot is idle.")
    await application.updater.start_polling()  # Required to suppress error
    await application.updater.stop()           # Immediately stop polling to lock webhook mode

if __name__ == "__main__":
    asyncio.run(main())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
