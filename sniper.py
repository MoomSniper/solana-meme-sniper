import os
import logging
import asyncio
import httpx
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

# Environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_ID = int(os.environ.get("TELEGRAM_ID"))
BIRDEYE_API = os.environ.get("BIRDEYE_API")
PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# Flask app
app = Flask(__name__)

# Telegram bot setup
bot = Bot(BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

# Constants
BIRDEYE_URL = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"

# Phase 5.1: Birdeye resilience patch
async def fetch_token_list():
    try:
        headers = {"X-API-KEY": BIRDEYE_API}
        async with httpx.AsyncClient() as client:
            response = await client.get(BIRDEYE_URL, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                tokens = data.get("data")
                if isinstance(tokens, list):
                    return tokens
                else:
                    logger.warning("Birdeye returned non-list token data")
                    return []
            elif response.status_code == 429:
                logger.warning("⛔ Rate limit hit. Backing off.")
                await asyncio.sleep(15)
                return []
            else:
                logger.warning(f"Birdeye error {response.status_code}: {response.text}")
                return []
    except Exception as e:
        logger.error(f"Error fetching from Birdeye: {e}")
        return []

# Alpha scan loop
async def monitor_market():
    logger.info("Starting market monitor...")
    while True:
        tokens = await fetch_token_list()
        if not tokens:
            logger.warning("No tokens returned from Birdeye.")
        else:
            logger.info(f"✅ Retrieved {len(tokens)} tokens from Birdeye")
            # Process tokens here — filter alpha, etc.
            # This is where you plug in your detection logic
        await asyncio.sleep(8)

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok"

@app.route("/")
def index():
    return "Solana Meme Sniper Bot Running"

# Telegram command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Sniper bot is live.")

application.add_handler(CommandHandler("start", start))

# Main entry
async def main():
    await application.bot.delete_webhook()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{BOT_TOKEN}")
    await bot.send_message(chat_id=TELEGRAM_ID, text="🚀 Sniper bot online. Waiting for alpha...")
    asyncio.create_task(monitor_market())
    application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
