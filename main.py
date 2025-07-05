import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# === Load environment variables ===
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
TELEGRAM_ID = int(os.environ["TELEGRAM_ID"])

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Flask Setup ===
app = Flask(__name__)
application = None

# === Flask route for Telegram webhook ===
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.create_task(application.process_update(update))
    except Exception as e:
        logger.error(f"Exception in telegram_webhook: {e}")
    return "ok"

# === Button UI ===
def get_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👀 Watch", callback_data="watch")],
        [InlineKeyboardButton("📈 In", callback_data="in")],
        [InlineKeyboardButton("🚪 Out", callback_data="out")]
    ])

# === /start Command ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 Sniper Bot Locked In. Choose an action:", reply_markup=get_keyboard())

# === Callback Button Handler ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "watch":
        await query.edit_message_text("👀 Radar scanning live Solana coins that are heating up... Stand by for alpha.")
        # 🔥 Future hook: send radar preview here

    elif data == "in":
        await query.edit_message_text("📈 Entering position. Running full deep scan on this coin’s behavior...")
        # 🔥 Future hook: trigger deep analysis

    elif data == "out":
        await query.edit_message_text("🚪 Exiting position. PnL snapshot recorded. Prepping next entry...")
        # 🔥 Future hook: log trade + prep rotation

# === Text failsafe ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❗ Use the /start button menu to interact. Type commands are disabled for clarity.")

# === Main async ===
async def main():
    global application
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Launch Flask server
    from threading import Thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=10000)).start()

    await asyncio.sleep(2)

    try:
        url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
        await application.bot.set_webhook(url=url)
        logger.info(f"✅ Webhook set: {url}")
    except Exception as e:
        logger.error(f"❌ Failed to set webhook: {e}")

if __name__ == "__main__":
    asyncio.run(main())
