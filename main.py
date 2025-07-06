import os
import asyncio
import logging
from flask import Flask, request
from telegram.ext import Application
from sniper import start_sniping

# Environment variables
TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Initialize application
application = Application.builder().token(TOKEN).build()

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook_handler():
    await application.update_queue.put(request.json)
    return {"status": "ok"}

async def main():
    # Set webhook
    await application.bot.delete_webhook()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{TOKEN}")

    # Start sniper
    logger.info("🚀 Starting DEX Screener sniper...")
    asyncio.create_task(start_sniping())

    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    loop = asyncio.get_event_loop()
    loop.create_task(main())
    app.run(host="0.0.0.0", port=PORT)
