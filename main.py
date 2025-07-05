import os
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.ext.webhook import WebhookHandler

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")

# Telegram Bot and Flask App
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()
webhook_handler = WebhookHandler(application)

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 God Mode Meme Sniper Activated.")

application.add_handler(CommandHandler("start", start))

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await webhook_handler.handle_update(update, application)
    return "OK", 200

# Main app route
@app.route("/", methods=["GET"])
def index():
    return "Meme Sniper Webhook is Live", 200

# Set the webhook on startup
async def setup():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(setup())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
