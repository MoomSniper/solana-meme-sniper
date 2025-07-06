if __name__ == "__main__":
    logger.info("🔧 Launching Flask app...")

    loop = asyncio.get_event_loop()
    loop.create_task(start_sniping())  # Launch sniper loop
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))import os
import asyncio
import logging
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes
from sniper import start_sniping  # Make sure this is correct

# === Logging Setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# === Environment ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")

# === Telegram Setup ===
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# === Flask Routes ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(handle_update(update))
    logger.info(f"✅ Incoming update: {update.message.text if update.message else 'No message'}")
    return "OK"

@app.route("/", methods=["GET"])
def home():
    return "Sniper bot is live."

# === Async handler ===
async def handle_update(update: Update):
    if update.message and update.message.text == "/start":
        await bot.send_message(chat_id=update.effective_chat.id, text="✅ Sniper Bot ready.")
        logger.info("🚀 /start command received. Starting sniper loop...")
        await start_sniping()

# === Run App ===
if __name__ == "__main__":
    logger.info("🔧 Launching Flask app...")

    loop = asyncio.get_event_loop()
    loop.create_task(start_sniping())  # Launch sniper loop
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
