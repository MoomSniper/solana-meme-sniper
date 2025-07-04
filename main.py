import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    ContextTypes
)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Full Render URL, e.g. https://your-app.onrender.com

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# FastAPI app
app = FastAPI()

# Telegram bot application
application: Application = ApplicationBuilder().token(BOT_TOKEN).build()


@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    logging.info("Webhook set to %s/webhook", WEBHOOK_URL)


@app.post("/webhook")
async def telegram_webhook(request: Request):
    data = await request.body()
    update = Update.de_json(data.decode("utf-8"), application.bot)
    await application.process_update(update)
    return {"ok": True}


@app.get("/")
def health_check():
    return {"status": "✅ Sniper Bot is Running — God Mode+++++"}


# Sample command — you can expand this with real sniper logic
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is online. Sniper locked in.")


# Register handlers
application.add_handler(CommandHandler("start", start))
