import asyncio
import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from sniper import run_sniper  # from your sniper.py

# Patch event loop to avoid RuntimeError in VPS or nested envs
import nest_asyncio
nest_asyncio.apply()

# === Logging ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# === Start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Obsidian Bot Online. Sniping live alpha.")

# === Bot Entry ===
async def main():
    bot_token = os.getenv("BOT_TOKEN", "8086252105:AAF-_xAzlorVkq-Lq9mGP2lLA99dRYj12BQ")
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))

    # Launch sniper in background
    asyncio.create_task(run_sniper())

    logger.info("✅ Bot started in polling mode. Awaiting commands.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
