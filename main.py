import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from modules.telegram_engine import send_message
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)

application = Application.builder().token(BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Obsidian Mode is live. Scanning for alpha now...")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Bot is running. Scanning every 44s for alpha 2.5–25x+")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("status", status))

@app.route("/", methods=["HEAD", "GET"])
def home():
    return "Bot is live", 200

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

async def run():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logging.info("✅ Telegram webhook set.")
    logging.info("🧠 Obsidian Mode active. Scanner running.")

if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run())
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

application.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),
    url_path=BOT_TOKEN,
    webhook_url=WEBHOOK_URL + "/" + BOT_TOKEN,
)

from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return 'Sniper bot is running in Obsidian Mode.'

# Run Flask to keep Render happy
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
