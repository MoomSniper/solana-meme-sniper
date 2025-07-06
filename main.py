import os
import logging
import asyncio
import threading
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import time

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

# ========== Telegram Command ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧠 Obsidian Mode is live. Scanning for alpha now...")

application.add_handler(CommandHandler("start", start))

# ========== Flask Webhook ==========

@app.route("/", methods=["GET", "HEAD"])
def index():
    return "Sniper bot running."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok", 200

# ========== Sniper Scanner (every 44s) ==========

async def sniper_loop():
    while True:
        try:
            # Placeholder — this is where you scan live coins
            print("[🔍] Scanning market for alpha...")
            await application.bot.send_message(chat_id=TELEGRAM_ID, text="⚡️ Scanning round complete. No alpha yet.")
            await asyncio.sleep(44)
        except Exception as e:
            logging.error(f"[❌] Sniper loop crashed: {e}")
            await asyncio.sleep(10)

# ========== Telegram Runner ==========

def run_telegram():
    asyncio.run(telegram_main())

async def telegram_main():
    logging.basicConfig(level=logging.INFO)
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logging.info("✅ Telegram webhook set.")
    logging.info("🧠 Obsidian Mode active. Scanner running.")
    asyncio.create_task(sniper_loop())  # Kick off the alpha scanner loop

# ========== Entry ==========

if __name__ == "__main__":
    threading.Thread(target=run_telegram).start()
    app.run(host="0.0.0.0", port=PORT)
