import os
import json
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# Env
BOT_TOKEN = os.environ['BOT_TOKEN']
TELEGRAM_ID = int(os.environ['TELEGRAM_ID'])

# Setup
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

application = Application.builder().token(BOT_TOKEN).build()

@app.post(f"/{BOT_TOKEN}")
async def webhook() -> str:
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return "OK"

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != TELEGRAM_ID:
        return
    await update.message.reply_text("🚀 Sniper Bot is active and listening.")

# Register
application.add_handler(CommandHandler("start", start))

# Start webhook and polling
async def main():
    await application.initialize()
    await application.start()
    await application.updater.start_polling()  # required for command registration
    await application.bot.set_webhook(url=os.environ['WEBHOOK_URL'])

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
