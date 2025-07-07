import os
import logging
import asyncio
import httpx
import cloudscraper
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)

# Send Telegram Message
async def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_ID, "text": text}
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload)
    except Exception as e:
        logger.error(f"❌ Failed to send Telegram message: {e}")

# Market Scanner using Dexscreener HTML + cloudscraper
async def scan_market_loop():
    scraper = cloudscraper.create_scraper()
    url = "https://dexscreener.com/solana"

    while True:
        try:
            logger.info("⚡️ Scanning Dexscreener HTML...")
            res = scraper.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if res.status_code != 200:
                logger.warning(f"⚠️ Dexscreener returned status {res.status_code}")
                await asyncio.sleep(30)
                continue

            html = res.text
            # You can extract token data here using BeautifulSoup if needed
            logger.info("✅ Dexscreener HTML loaded successfully.")

            await asyncio.sleep(45)

        except Exception as e:
            logger.error(f"❌ Dexscreener scrape failed: {e}")
            await asyncio.sleep(45)

# Telegram Bot Init
application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .post_init(lambda app: asyncio.get_event_loop().create_task(scan_market_loop()))
    .build()
)

# Flask Routes
@app.route("/", methods=["GET"])
def index():
    return "Sniper bot is live."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    logger.info(f"📥 Incoming Telegram update: {data}")
    application.update_queue.put_nowait(Update.de_json(data, application.bot))
    return "OK"

# Start App
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    logger.info("✅ Telegram webhook set.")
    logger.info("🧠 Obsidian Mode active. Scanner running.")
    application.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=WEBHOOK_URL,
    )
