import os
import asyncio
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from sniper import scan_and_score_market
from modules.commands import setup_telegram_commands  # Make sure this exists

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# Flask app
app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# Telegram Bot
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Telegram Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Bot is online in Godest Mode.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🧠 Obsidian scanner active. Scanning every 44s.")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("status", status))
setup_telegram_commands(application)

# Background scanner every 44 seconds
async def run_scanner():
    await asyncio.sleep(10)
    while True:
        logger.info("🔍 Starting 44s scan...")
        try:
            await scan_and_score_market()
        except Exception as e:
            logger.error(f"❌ Scanner crashed: {e}")
        await asyncio.sleep(44)

# Webhook Flask route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "OK"

# Start all systems
async def main():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info("✅ Telegram webhook set.")
    logger.info("🧠 Obsidian Mode activated.")
    asyncio.create_task(run_scanner())
    await application.initialize()
    await application.start()
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    asyncio.run(main())
