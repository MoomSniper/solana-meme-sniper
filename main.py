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

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# Flask
app = Flask(__name__)

# Env Vars
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# Telegram app
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Bot is online in Godest Mode.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🧠 Obsidian scanner is active. Scanning every 44s.")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("status", status))

# Scanner loop
async def run_scanner():
    await asyncio.sleep(10)
    while True:
        logger.info("🔍 Running scan...")
        try:
            await scan_and_score_market()
        except Exception as e:
            logger.error(f"❌ Scan failed: {e}")
        await asyncio.sleep(44)

# Webhook endpoint
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return "OK"

# Init everything
async def main():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info("✅ Telegram webhook set.")
    logger.info("🧠 Obsidian Mode active. Scanner running.")
    asyncio.create_task(run_scanner())
    await application.initialize()
    await application.start()
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    asyncio.run(main())
