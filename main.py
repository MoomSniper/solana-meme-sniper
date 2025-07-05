import logging
import asyncio
import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import httpx

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Telegram bot app
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Start command triggered by {update.effective_user.id}")
    await update.message.reply_text("🚀 Sniper Bot Activated. Type /watch to see radar targets.")

# Watch command
async def watch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/watch used by {update.effective_user.id}")
    await update.message.reply_text("🧠 Radar scanning... No targets right now. (This will show hot coins approaching alpha.)")

# Callback handler for inline buttons
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "yes":
        await query.edit_message_text("🧠 Initiating deeper alpha scan...")
        await context.bot.send_message(chat_id=query.from_user.id, text="🔍 Scanning this coin harder than your ex’s Insta.")
    elif query.data == "no":
        await query.edit_message_text("❌ Cancelled. No problem.")

# Custom "in" message
async def in_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"'in' called by {update.effective_user.id}")
    keyboard = [
        [
            InlineKeyboardButton("Yes 🔥", callback_data="yes"),
            InlineKeyboardButton("No ❌", callback_data="no"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🧠 Run full sniper scan on this coin?", reply_markup=reply_markup)

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("watch", watch))
application.add_handler(CallbackQueryHandler(button_callback))
application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"\bin\b"), in_handler))

# Webhook route (sync for Flask compatibility)
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        asyncio.run(application.process_update(update))
    except Exception as e:
        logger.error(f"Webhook error: {e}")
    return "ok"

# Set webhook on startup
async def set_webhook():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    payload = {"url": f"{WEBHOOK_URL}/{BOT_TOKEN}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload)
        if response.status_code == 200:
            logger.info(f"✅ Webhook set: {payload['url']} — Telegram response: {response.json().get('ok')}")
        else:
            logger.error(f"❌ Failed to set webhook: {response.text}")

# Startup logic
if __name__ == "__main__":
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=PORT)
