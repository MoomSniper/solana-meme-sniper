import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

from sniper import run_sniper  # Ensure function name matches sniper.py

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Obsidian Bot Deployed. Scanning in real-time.")

# Bot setup
async def start_bot():
    bot_token = os.environ.get("BOT_TOKEN")
    application = ApplicationBuilder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))

    webhook_url = f"{os.environ.get('WEBHOOK_URL')}/{bot_token}"
    await application.initialize()
    await application.bot.set_webhook(url=webhook_url)
    logger.info("✅ Telegram webhook set.")

    asyncio.create_task(run_sniper())  # Must match sniper.py entrypoint
    logger.info("🧠 Obsidian Mode active. Scanner running.")

    await application.start()

@app.route(f"/{os.environ['BOT_TOKEN']}", methods=["POST"])
async def telegram_webhook():
    from telegram.ext import Application
    application = ApplicationBuilder().token(os.environ.get("BOT_TOKEN")).build()
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "OK", 200

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    app.run(host="0.0.0.0", port=int(os.envir
