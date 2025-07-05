import os
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# Bot Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 God Mode Meme Sniper Activated.")
    logger.info(f"/start called by {update.effective_user.id}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    logger.info(f"Message: {text}")
    if text == "watch":
        await update.message.reply_text("✅ Watching radar-ready coins...")
    elif text == "in":
        await update.message.reply_text("🟢 You’re IN. Doing deeper scan on this one.")
    elif text == "out":
        await update.message.reply_text("🔴 Out. Removing from radar.")
    else:
        await update.message.reply_text("🤖 Unknown command. Try watch / in / out.")

# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# Fix: This is the endpoint that Telegram will actually hit
@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get("Content-Type") == "application/json":
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
        logger.info("✅ Update received and queued.")
        return jsonify({"status": "ok"})
    else:
        logger.warning("❌ Wrong content type")
        return "Invalid", 400

# Set webhook on launch
async def set_webhook():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
    logger.info("✅ Webhook set")

# Start Flask
if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=PORT)
