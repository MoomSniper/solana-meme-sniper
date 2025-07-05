import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext import Dispatcher
import asyncio
import httpx

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Telegram application
application = Application.builder().token(BOT_TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 God Mode Meme Sniper Activated.")

# Register command
application.add_handler(CommandHandler("start", start))

# Flask route must match the full bot token for webhook
@app.post(f"/{BOT_TOKEN}")
async def webhook_handler():
    try:
        update = Update.de_json(await request.get_json(force=True), application.bot)
        await application.process_update(update)
        return "ok"
    except Exception as e:
        logger.exception("Failed to handle update")
        return "error"

# Set webhook
async def set_webhook():
    async with httpx.AsyncClient() as client:
        url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
        resp = await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            json={"url": url}
        )
        if resp.status_code == 200:
            logger.info(f"✅ Webhook set to {url}")
        else:
            logger.error(f"❌ Failed to set webhook: {resp.text}")

# Startup logic
if __name__ == "__main__":
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=PORT)
