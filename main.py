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

# === Load env variables ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# === Logging ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# === Start command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Obsidian Bot Online. Sniping live alpha.")

# === Bot entry ===
async def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Launch sniper engine in background
    asyncio.create_task(run_sniper())

    logger.info("✅ Bot started in polling mode. Awaiting commands.")
    await app.run_polling()

# === Run ===
if __name__ == "__main__":
    asyncio.run(run_bot())
