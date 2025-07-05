import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import httpx

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load ENV
BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
TELEGRAM_ID = int(os.environ.get("TELEGRAM_ID"))

# Flask app
app = Flask(__name__)

# Telegram bot app
application = Application.builder().token(BOT_TOKEN).build()

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Sniper bot is online and ready to hunt.")

application.add_handler(CommandHandler("start", start))

# Webhook route - SYNC handler
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

# Root test route
@app.route("/", methods=["GET"])
def home():
    return "✅ Bot Server Running", 200

# Set webhook once app is ready
async def setup():
    # Delete existing webhook
    async with httpx.AsyncClient() as client:
        await client.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            params={"url": f"{WEBHOOK_URL}/{BOT_TOKEN}"}
        )
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{BOT_TOKEN}")
    await application.bot.send_message(chat_id=TELEGRAM_ID, text="✅ Sniper Bot Deployed & Live via Webhook")

# Startup
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(setup())
    application.run_polling()  # Still needed to run dispatcher
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
