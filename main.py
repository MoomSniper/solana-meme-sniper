import os
import logging
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    Application, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get env vars
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g., https://your-app.onrender.com

# Telegram app
application: Application = ApplicationBuilder().token(BOT_TOKEN).build()

# FastAPI app
app = FastAPI()

# === Command Handlers ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Sniper Bot: God Mode+++++++ initialized.")

# === Add Handlers ===
application.add_handler(CommandHandler("start", start))

# === Webhook Endpoint ===
@app.post("/webhook")
async def telegram_webhook(request: Request):
    raw_data = await request.body()
    update = Update.de_json(data=raw_data.decode("utf-8"), bot=application.bot)

    if not application.ready:
        await application.initialize()
    await application.process_update(update)

    return {"ok": True}

# === Set Webhook on Startup ===
@app.on_event("startup")
async def startup():
    await application.initialize()
    await application.bot.set_webhook(f"{WEBHOOK_URL}/webhook")
    logger.info("🚀 Webhook set successfully.")

# === Optional Healthcheck ===
@app.get("/")
def root():
    return {"status": "running"}
