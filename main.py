import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# Flask app
app = Flask(__name__)

# Init Telegram app
application = Application.builder().token(BOT_TOKEN).build()

# Telegram command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 God Mode Meme Sniper Activated.")
    logger.info(f"/start command by user: {update.effective_user.id}")

# Text command handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    user_id = update.effective_user.id
    logger.info(f"Text from {user_id}: {text}")

    if text == "watch":
        await update.message.reply_text("✅ Watching radar-ready coins...")
    elif text == "in":
        await update.message.reply_text("🟢 You’re IN. Doing deeper scan on this one.")
    elif text == "out":
        await update.message.reply_text("🔴 Out. Removing from radar.")
    else:
        await update.message.reply_text("🤖 Unrecognized command. Use: watch, in, or out")

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# Flask webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
        return "ok"
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "error", 500

# Set webhook
async def set_webhook():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info(f"✅ Webhook set to: {WEBHOOK_URL}/{BOT_TOKEN}")

# Run app
if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=PORT)
