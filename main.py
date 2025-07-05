import os
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, ContextTypes
)
from sniper import monitor_market

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Env vars
TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper Bot is live and scanning.")

# Main startup
async def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Set webhook
    await application.bot.delete_webhook()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{TOKEN}")

    # Notify start
    await application.bot.send_message(chat_id=TELEGRAM_ID, text="✅ Sniper Bot is active.")

    # Start sniper loop in background
    asyncio.create_task(monitor_market(application.bot))

    # Start Telegram webhook server (no Flask, clean)
    await application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )

if __name__ == "__main__":
    asyncio.run(main())
