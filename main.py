import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment vars
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# Flask app
app = Flask(__name__)

# Telegram bot app
application = Application.builder().token(BOT_TOKEN).build()

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 God Mode Meme Sniper Activated.")
    logger.info(f"/start called by {update.effective_user.id}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    user_id = update.effective_user.id
    logger.info(f"Received message from {user_id}: {text}")

    if text == "watch":
        await update.message.reply_text("✅ Watching radar-ready coins...")
    elif text == "in":
        await update.message.reply_text("🟢 You’re IN. Doing deeper scan on this one.")
    elif text == "out":
        await update.message.reply_text("
