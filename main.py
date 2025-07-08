import os
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from sniper import run_sniper

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Command: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Obsidian Bot Deployed. Sniper scanning live.")

# Bot setup
async def start_bot():
    application = ApplicationBuilder().token(os.environ.get("BOT_TOKEN")).build()
    application.add_handler(CommandHandler("start", start))

    asyncio.create_task(run_sniper())
    logger.info("🧠 Obsidian Mode active. Scanner running.")

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()

if __name__ == "__main__":
    asyncio.run(start_bot())
