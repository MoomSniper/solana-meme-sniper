import asyncio
import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from sniper import run_sniper

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

# === Setup and Run ===
async def launch_bot():
    bot_token = os.getenv("BOT_TOKEN", "8086252105:AAF-_xAzlorVkq-Lq9mGP2lLA99dRYj12BQ")
    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))

    asyncio.create_task(run_sniper())

    logger.info("✅ Bot started in polling mode. Awaiting commands.")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await app.updater.idle()

# === Start Everything ===
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(launch_bot())
