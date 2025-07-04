import os
import logging
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, CommandHandler

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ENV VARS
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://your-app-name.onrender.com
PORT = int(os.getenv("PORT", 10000))

# Telegram app init
application: Application = ApplicationBuilder().token(BOT_TOKEN).build()

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is live and webhook works.")

application.add_handler(CommandHandler("start", start))

# FastAPI app
app = FastAPI()

@app.on_event("startup")
async def startup():
    webhook_url = f"{WEBHOOK_URL}/webhook"
    await application.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

@app.post("/webhook")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"status": "ok"}

# Uvicorn runs this if main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
