import asyncio
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from sniper import monitor_market

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App config
BOT_TOKEN = "7619311236:AAFzjBR3N1oVi31J2WqU4cgZDiJgBxDPWRo"
WEBHOOK_URL = "https://solana-meme-sniper-godmode.onrender.com/" + BOT_TOKEN

# Telegram bot app
application = Application.builder().token(BOT_TOKEN).build()

# Flask webhook
app = Flask(__name__)

@app.post(f"/{BOT_TOKEN}")
async def webhook() -> str:
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

async def main():
    await application.initialize()
    await application.bot.delete_webhook()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}")

    # Start background sniper
    asyncio.create_task(monitor_market())

    await application.start()
    # No idle/polling here — this is webhook-only

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
