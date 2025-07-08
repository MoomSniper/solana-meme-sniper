import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from sniper import run_sniper
import nest_asyncio

# Load .env variables
load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

# Apply nested event loop patch
nest_asyncio.apply()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Obsidian Bot Online. Sniping live alpha.")

# Run bot
async def bot_main():
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    asyncio.create_task(run_sniper())
    logger.info("✅ Bot started in polling mode. Awaiting commands.")
    await app.run_polling()

# Start the event loop safely (no asyncio.run())
loop = asyncio.get_event_loop()
loop.run_until_complete(bot_main())
