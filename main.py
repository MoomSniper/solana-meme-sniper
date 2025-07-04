import os
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler
)
import uvicorn

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # example: https://yourapp.onrender.com
PORT = int(os.getenv("PORT", default=10000))

# Init FastAPI app and Telegram bot
app = FastAPI()
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Example /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Bot is live. Webhook setup complete. God Mode+++++ active."
    )

application.add_handler(CommandHandler("start", start))

# Webhook route
@app.post("/")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return {"ok": True}

# On startup: set Telegram webhook
@app.on_event("startup")
async def on_startup():
    await application.bot.set_webhook(url=WEBHOOK_URL)
    print("✅ Webhook set to:", WEBHOOK_URL)

# Run app with uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
