# 📌 MANUAL WEBHOOK SETUP:
# Once deployed and live, visit the following URL to activate your webhook:
# https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://solana-meme-sniper-godmode.onrender.com/<YOUR_BOT_TOKEN>
# Example (your actual values):
# https://api.telegram.org/bot7619311236:AAFzjBR3N1oVi31J2WqU4cgZDiJgBxDPWRo/setWebhook?url=https://solana-meme-sniper-godmode.onrender.com/7619311236:AAFzjBR3N1oVi31J2WqU4cgZDiJgBxDPWRo

import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Load env vars
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

# Flask app
app = Flask(__name__)

# Initialize Telegram application
application = Application.builder().token(BOT_TOKEN).build()

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 God Mode Meme Sniper Activated.")
    logger.info(f"/start called by {update.effective_user.id}")

# Message handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    user_id = update.effective_user.id
    logger.info(f"Received message from {user_id}: {text}")

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

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
        return "ok"
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "error", 500

# Start the Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
