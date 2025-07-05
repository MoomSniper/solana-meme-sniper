import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sniper import monitor_market

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Env
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))

# Bot app
application = Application.builder().token(TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper Bot is active and listening.")

application.add_handler(CommandHandler("start", start))

# ✅ Setup runner
async def main():
    await application.bot.delete_webhook()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{TOKEN}")
    
    await application.bot.send_message(chat_id=TELEGRAM_ID, text="✅ Sniper Bot is live and scanning the market.")
    
    # ⛏️ Start monitoring in background
    application.create_task(monitor_market(application.bot))

    # 🚀 Start webhook server
    await application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}",
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
