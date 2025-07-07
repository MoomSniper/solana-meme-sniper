import os
import logging
import httpx
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))
HELIUS_API = os.getenv("HELIUS_API")

app = Flask(__name__)

# Telegram Messenger
async def send_telegram_message(text: str):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_ID, "text": text},
            )
    except Exception as e:
        logger.error(f"❌ Telegram send failed: {e}")

# Alpha Scanner via Helius
async def scan_market_loop():
    headers = {
        "Authorization": f"Bearer {HELIUS_API}",
        "Content-Type": "application/json",
    }

    url = "https://mainnet.helius-rpc.com/"  # your actual endpoint may differ
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAssetsByGroup",
        "params": {
            "groupKey": "collection",
            "groupValue": "TOKEN_PROGRAM_PUBKEY",
            "page": 1,
            "limit": 50
        }
    }

    while True:
        try:
            logger.info("⚡️ Scanning market via Helius...")
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, headers=headers)
                data = res.json()

            tokens = data.get("result", {}).get("items", [])[:30]
            for token in tokens:
                name = token.get("content", {}).get("metadata", {}).get("name", "Unknown")
                address = token.get("id", "N/A")
                mc = token.get("metrics", {}).get("market_cap_usd", 0)
                vol = token.get("metrics", {}).get("volume_usd_24h", 0)
                txns = token.get("metrics", {}).get("tx_count_24h", 0)

                if mc and vol and txns and mc < 300_000 and vol > 5000 and txns > 15:
                    msg = (
                        f"🚨 ALPHA FOUND\n\n"
                        f"🪙 {name}\n"
                        f"💰 MC: ${mc:,.0f}\n"
                        f"📈 Vol (24h): ${vol:,.0f}\n"
                        f"🛒 Txns: {txns}\n"
                        f"🔗 https://solanatracker.io/token/{address}"
                    )
                    logger.info(msg)
                    await send_telegram_message(msg)

            await asyncio.sleep(45)

        except Exception as e:
            logger.error(f"❌ Market scan error: {e}")
            await asyncio.sleep(45)

# Flask Routes
@app.route("/", methods=["GET"])
def index():
    return "Sniper bot is live."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    logger.info(f"📥 Telegram update: {data}")
    return "OK"

# Telegram Bot Setup
application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .post_init(lambda app: asyncio.get_event_loop().create_task(scan_market_loop()))
    .build()
)

# Run App
if __name__ == "__main__":
    logger.info("✅ Telegram webhook set.")
    logger.info("🧠 Obsidian Mode active. Scanner running.")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )
