import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    Application,
    ContextTypes,
    CommandHandler
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# FastAPI app
app = FastAPI()

# Build Telegram bot application
application: Application = ApplicationBuilder().token(BOT_TOKEN).build()

# Example command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sniper Bot ready. God Mode +++++ engaged.")

application.add_handler(CommandHandler("start", start))

# Webhook endpoint
@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.initialize()
        await application.process_update(update)
    except Exception as e:
        logging.error(f"Error in webhook: {e}")
    return {"ok": True}

# Set webhook on startup
@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    logging.info("Webhook successfully set.")
