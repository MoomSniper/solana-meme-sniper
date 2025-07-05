import os
import logging
import asyncio
import httpx
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Env variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Flask app
app = Flask(__name__)

# Telegram app
application = Application.builder().token(BOT_TOKEN).build()

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"/start by {user.id} ({user.username})")
    await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Sniper system active. Awaiting alpha...")

# Watch command (GodRadar)
async def watch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟡 Radar activated.\nMonitoring high-potential coins nearing sniper criteria...")

# Register handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("watch", watch))

# Flask route to handle webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def telegram_webhook():
    try:
        data = request.get_json(force=True)
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return "OK"
    except Exception as e:
        logger.error(f"Exception in telegram_webhook: {e}")
        return "Webhook error"

# Set webhook on startup
async def set_webhook():
    async with httpx.AsyncClient() as client:
        webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
        res = await client.post(url, json={"url": webhook_url})
        if res.status_code == 200:
            logger.info(f"✅ Webhook set: {webhook_url} — Telegram response: {res.json()['ok']}")
        else:
            logger.error(f"❌ Failed to set webhook: {res.text}")

# Boot everything
async def run():
    await application.initialize()
    await application.bot.delete_webhook(drop_pending_updates=True)
    await set_webhook()
    await application.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except RuntimeError as e:
        logger.error(f"Event loop error: {e}")
