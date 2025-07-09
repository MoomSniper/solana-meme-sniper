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
from dex_scraper_ws import run_ws_sniper

# === Load environment variables ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN is missing from .env")

# === Logging setup ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# === Telegram command: /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name or "user"
    await update.message.reply_text(f"🟢 Obsidian Bot Online.\nWelcome, {user}. Sniping live alpha...")

# === Telegram command: /test ===
async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Test alert received. Bot is working.")

# === Bot logic ===
async def run_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("test", test))

    # Run sniper in the background
    try:
        asyncio.create_task(run_ws_sniper())
        logger.info("🚀 Sniper task launched.")
    except Exception as e:
        logger.error(f"❌ Failed to start sniper: {e}")

    logger.info("✅ Bot started in polling mode.")
    await app.run_polling()

# === Entrypoint ===
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bot())
