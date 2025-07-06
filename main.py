import os
import logging
import nest_asyncio
import threading
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sniper import monitor_market

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

# Flask setup
app = Flask(__name__)
nest_asyncio.apply()

# Telegram app
application = Application.builder().token(TOKEN).build()

# Command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Sniper Bot ready.")

application.add_handler(CommandHandler("start", start))

# Webhook route
@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook() -> str:
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

def run_flask():
    app.run(host="0.0.0.0", port=PORT)

# App boot
if __name__ == "__main__":
    import asyncio
    import httpx

    async def setup():
        async with httpx.AsyncClient() as client:
            await client.post(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
            await client.post(
                f"https://api.telegram.org/bot{TOKEN}/setWebhook",
                params={"url": f"{WEBHOOK_URL}/{TOKEN}"}
            )

        await application.initialize()
        logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{TOKEN}")

        # Run Flask in background
        threading.Thread(target=run_flask, daemon=True).start()

        # Scan once (no repeat)
        await monitor_market()

    asyncio.run(setup())
