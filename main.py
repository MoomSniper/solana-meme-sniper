import os
import logging
import asyncio
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sniper import start_sniping

# === Environment Vars ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# === Logger Setup ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Flask App Setup ===
app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# === Telegram Bot Setup ===
application = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Sniper bot is live and hunting for alpha.")

application.add_handler(CommandHandler("start", start))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        application.update_queue.put_nowait(update)
        return "OK", 200

# === Run Everything ===
async def run():
    logger.info("🚀 Setting webhook...")
    await bot.delete_webhook()
    await bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{BOT_TOKEN}")

    logger.info("🚀 Starting market monitor...")
    asyncio.create_task(start_sniping())
    await application.initialize()
    await application.start()
    await application.updater.start_polling()  # Required by Telegram framework internals
    await application.updater.idle()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(run())
    app.run(host="0.0.0.0", port=PORT)
