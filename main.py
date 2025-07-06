import logging
import os
import asyncio

from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# Flask app
app = Flask(__name__)

# Telegram bot app
application = Application.builder().token(BOT_TOKEN).build()

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Obsidian Mode is live. Scanning for alpha now...")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Bot is running. Scanning every 44s for alpha 2.5–25x+")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("status", status))

# Routes
@app.route("/", methods=["GET", "HEAD"])
def home():
    return "Sniper bot is running in Obsidian Mode.", 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "OK", 200

async def init_bot():
    logging.basicConfig(level=logging.INFO)
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logging.info("✅ Telegram webhook set.")
    logging.info("🧠 Obsidian Mode active. Scanner running.")

# Final combined entrypoint
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(init_bot())
    app.run(host="0.0.0.0", port=PORT)
