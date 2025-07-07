import os
import logging
import httpx
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SOLANA_TRACKER_API = os.getenv("SOLANA_TRACKER_API")

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

# Real Market Scan with Solana Tracker (V2)
async def scan_market_loop():
    headers = {
        "accept": "application/json",
        "x-api-key": SOLANA_TRACKER_API
    }
    url = "https://public-api.solanatracker.io/v1/tokens?chain=solana&limit=50&sort=volume_1h"

    while True:
        try:
            logger.info("⚡️ Scanning live market via Solana Tracker...")
            async with httpx.AsyncClient() as client:
                res = await client.get(url, headers=headers)
                data = res.json()

            tokens = data.get("data", [])[:40]
            for token in tokens:
                mc = token.get("market_cap", 0)
                vol = token.get("volume_1h", 0)
                buyers = token.get("transactions_1h", 0)
                name = token.get("name", "N/A")
                address = token.get("address", "")

                if not all([mc, vol, buyers]):
                    continue

                if mc < 300_000 and vol > 5_000 and buyers > 15:
                    msg = (
                        f"🚨 ALPHA FOUND\n\n"
                        f"🪙 {name}\n"
                        f"💰 MC: ${mc:,.0f}\n"
                        f"📈 Vol (1h): ${vol:,.0f}\n"
                        f"🛒 Txns: {buyers}\n"
                        f"🔗 https://solanatracker.io/token/{address}"
                    )
                    logger.info(msg)
                    await send_telegram_message(msg)

            await asyncio.sleep(44)

        except Exception as e:
            logger.error(f"❌ Error in market scan: {e}")
            await asyncio.sleep(44)

# /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Obsidian Sniper Bot is now live. Watching market 24/7.")

# Telegram App
application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .post_init(lambda app: asyncio.get_event_loop().create_task(scan_market_loop()))
    .build()
)
application.add_handler(CommandHandler("start", start))

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
    logger.info("✅ Telegram webhook set.")
    logger.info("🧠 Obsidian Mode active. Scanner running.")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        webhook_url=WEBHOOK_URL,
    )
