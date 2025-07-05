import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_ID = int(os.environ.get("TELEGRAM_ID"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

# Flask app setup
app = Flask(__name__)

# Create bot and application instance
bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

# Basic /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Sniper bot online and watching the charts.")

application.add_handler(CommandHandler("start", start))

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        if request.method == "POST":
            update = Update.de_json(request.get_json(force=True), bot)

            async def process():
                await application.initialize()
                await application.start()
                await application.process_update(update)
                await application.stop()
                await application.shutdown()

            asyncio.run(process())

        return "ok"
    except Exception as e:
        logger.error(f"Exception in telegram_webhook: {e}")
        return "error"

# Root route for testing
@app.route("/")
def index():
    return "🚀 Solana Meme Sniper Bot is Live!"

# Set webhook before running
async def set_webhook():
    await bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=PORT)
