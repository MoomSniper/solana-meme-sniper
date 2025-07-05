import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sniper import sniper_loop  # Your alpha logic
import logging
import os

BOT_TOKEN = os.environ['BOT_TOKEN']
WEBHOOK_URL = os.environ['WEBHOOK_URL']
PORT = int(os.environ.get('PORT', 10000))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

application = Application.builder().token(BOT_TOKEN).build()

@app.post(f"/{BOT_TOKEN}")
async def webhook() -> str:
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "OK"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper Bot is active and listening.")

application.add_handler(CommandHandler("start", start))

async def run():
    await application.initialize()
    application.create_task(sniper_loop())  # ← This was missing
    await application.start()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    await application.updater.start_polling()  # Optional: remove if using webhook only
    await application.updater.idle()

if __name__ == "__main__":
    asyncio.run(run())
