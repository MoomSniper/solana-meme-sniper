import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# === Phase 1: Basic Setup ===
# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Env vars
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# Flask app
app = Flask(__name__)

# Telegram app
application = Application.builder().token(BOT_TOKEN).build()

# === Phase 2: /start and webhook ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"/start called by {update.effective_user.id}")
    await update.message.reply_text("🚀 God Mode Meme Sniper Activated.")

application.add_handler(CommandHandler("start", start))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        update = Update.de_json(request.get_json(force=True), application.bot)
        application.update_queue.put_nowait(update)
        return "ok"
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "error", 500

# === Phase 3: Set webhook + run Flask ===
async def set_webhook():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    app.run(host="0.0.0.0", port=PORT)
