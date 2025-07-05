import asyncio
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from sniper import monitor_market

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app for webhook
app = Flask(__name__)

BOT_TOKEN = "7619311236:AAFzjBR3N1oVi31J2WqU4cgZDiJgBxDPWRo"
WEBHOOK_URL = "https://solana-meme-sniper-godmode.onrender.com/" + BOT_TOKEN

# Telegram app setup
application = Application.builder().token(BOT_TOKEN).build()

@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

async def main():
    await application.initialize()
    await application.bot.delete_webhook()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}")

    # Launch sniper in background
    asyncio.create_task(monitor_market())

    await application.start()
    await application.updater.start_polling()  # Safe fallback
    await application.idle()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
