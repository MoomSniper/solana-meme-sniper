import logging
import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, ContextTypes,
                          MessageHandler, filters, CallbackQueryHandler)
import httpx

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ENV variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# Flask app setup
app = Flask(__name__)

# Telegram Application
application = Application.builder().token(BOT_TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🚀 God Mode Meme Sniper Activated.")

# Watch command
async def watch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🟡 Radar scanning… Targets nearing alpha trigger.")

# in/out commands
async def call_in(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="🧠 Running deep scan on this one… sit tight.")

async def call_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="📉 Marked as exit candidate. Pull profits or trail stop.")

# Telegram command registration
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("watch", watch))
application.add_handler(CommandHandler("in", call_in))
application.add_handler(CommandHandler("out", call_out))

# Webhook endpoint
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        asyncio.run(run_update(update))
    except Exception as e:
        logger.error(f"Webhook error: {e}")
    return "ok"

async def run_update(update: Update):
    await application.initialize()
    await application.process_update(update)

# Set webhook on startup
async def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    async with httpx.AsyncClient() as client:
        r = await client.post(url, json={"url": webhook_url})
        if r.status_code == 200:
            logger.info(f"✅ Webhook set: {webhook_url} — Telegram response: {r.json()['ok']}")
        else:
            logger.error(f"❌ Failed to set webhook: {r.text}")

# Startup
if __name__ == "__main__":
    try:
        asyncio.run(set_webhook())
    except Exception as e:
        logger.error(f"Webhook setup failed: {e}")

    app.run(host="0.0.0.0", port=PORT)
