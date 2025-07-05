import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Logging setup
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# Flask app
app = Flask(__name__)

# Telegram application
application = Application.builder().token(BOT_TOKEN).build()

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("\ud83d\ude80 God Mode Meme Sniper Activated.")

# Text handler
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.lower()
    if message == "watch":
        await update.message.reply_text("\ud83d\udc40 Watching for potential alpha.")
    elif message == "in":
        await update.message.reply_text("\u2705 You're in. Tracking enabled.")
    elif message == "out":
        await update.message.reply_text("\u274c You're out. Tracking disabled.")
    else:
        await update.message.reply_text("\ud83e\udd16 Unknown command. Use: watch, in, or out.")

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

# Flask webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"

# Set webhook and run app
async def run():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logging.info(f"\u2705 Webhook set: {WEBHOOK_URL}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
