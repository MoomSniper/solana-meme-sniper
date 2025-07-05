import os
import nest_asyncio
import logging
import threading
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sniper import monitor_market

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Env vars
TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# Flask setup
app = Flask(__name__)
nest_asyncio.apply()

# Telegram app
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper Bot is live and scanning.")

application.add_handler(CommandHandler("start", start))

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

def run_flask():
    app.run(host="0.0.0.0", port=PORT)

async def setup():
    await application.bot.delete_webhook()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{TOKEN}")
    await application.initialize()
    await application.bot.send_message(chat_id=TELEGRAM_ID, text="✅ Sniper Bot is active.")
    threading.Thread(target=run_flask, daemon=True).start()
    await monitor_market(application.bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(setup())
