import os
import json
import asyncio
import logging
import httpx
from flask import Flask, request
from telegram import Bot

# Environment Variables
BOT_TOKEN = os.environ["BOT_TOKEN"]
TELEGRAM_ID = os.environ["TELEGRAM_ID"]
HELIUS_RPC = "https://mainnet.helius-rpc.com/"
PORT = int(os.environ.get("PORT", 10000))
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

# Logger Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# Send Telegram Message
async def send_telegram_message(message):
    try:
        await bot.send_message(chat_id=TELEGRAM_ID, text=message, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Telegram send error: {e}")

# Pull and filter token data
async def scan_market():
    headers = {"Content-Type": "application/json"}
    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokens",
        "params": {
            "limit": 50,
            "sortBy": "recent",
            "direction": "desc"
        }
    }

    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(HELIUS_RPC, headers=headers, json=body, timeout=10)
            data = res.json()
            logger.info(f"📦 Raw Helius data: {json.dumps(data, indent=2)}")

            if not data.get("result"):
                logger.warning("No result in Helius response.")
                return

            for token in data["result"]:
                name = token.get("name", "Unknown")
                mc = token.get("marketCap", 0)
                vol = token.get("volume24h", 0)
                buyers = token.get("uniqueBuyers", 0)

                logger.info(f"📊 Token: {name} | MC: {mc} | Vol: {vol} | Buyers: {buyers}")

                if mc and vol and buyers and mc < 300_000 and vol > 5_000 and buyers > 15:
                    message = (
                        f"🚨 <b>ALPHA FOUND</b>\n"
                        f"🪙 <b>{name}</b>\n"
                        f"💰 MC: ${mc:,.0f}\n"
                        f"📈 Vol: ${vol:,.0f}\n"
                        f"👥 Buyers: {buyers}"
                    )
                    await send_telegram_message(message)
        except Exception as e:
            logger.error(f"Helius scan error: {e}")

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    return "OK"

@app.route("/")
def root():
    return "✅ Obsidian Sniper Bot is live."

async def main():
    logger.info("✅ Telegram webhook set.")
    logger.info("🧠 Obsidian Mode active. Scanner running.")
    await send_telegram_message("🟢 Obsidian Bot Deployed. Scanning in real-time.")

    while True:
        await scan_market()
        await asyncio.sleep(4)

if __name__ == "__main__":
    asyncio.run(main())  # ✅ Python 3.11+ safe
    app.run(host="0.0.0.0", port=PORT)
