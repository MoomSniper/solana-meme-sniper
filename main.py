import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# 🧠 /start handler only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Obsidian Mode is live. Scanning for alpha now...")

application.add_handler(CommandHandler("start", start))

@app.route("/", methods=["GET", "HEAD"])
def index():
    return "Sniper bot running."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok", 200

def run_telegram():
    asyncio.run(telegram_main())

async def telegram_main():
    logging.basicConfig(level=logging.INFO)
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logging.info("✅ Telegram webhook set.")
    logging.info("🧠 Obsidian Mode active. Scanner running.")

if __name__ == "__main__":
    threading.Thread(target=run_telegram).start()
    app.run(host="0.0.0.0", port=PORT)
