import os
import logging
import httpx
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BIRDEYE_API = os.getenv("BIRDEYE_API")

app = Flask(__name__)

# ========== TELEGRAM UTIL ==========

async def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_ID, "text": text}
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload)
    except Exception as e:
        logger.error(f"❌ Telegram send error: {e}")

# ========== MARKET SCANNER ==========

async def scan_market():
    try:
        url = "https://public-api.birdeye.so/public/price/solana"
        headers = {"X-API-KEY": BIRDEYE_API}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            data = response.json().get("data", [])

        for coin in data:
            symbol = coin.get("symbol", "")
            price = float(coin.get("value", 0))

            # Placeholder logic: flag if coin has 'dog' in name and price < $0.01
            if "dog" in symbol.lower() and price < 0.01:
                msg = f"🚨 Potential Alpha: {symbol}\n💰 Price: ${price}"
                await send_telegram_message(msg)

                # Start research timer
                asyncio.create_task(deep_research(symbol))
    except Exception as e:
        logger.error(f"❌ Scan error: {e}")

async def scan_market_loop():
    while True:
        logger.info("⚡️ Scanning market for alpha...")
        await scan_market()
        await asyncio.sleep(44)

# ========== DEEP RESEARCH ==========

async def deep_research(symbol):
    await asyncio.sleep(90)
    try:
        # Simulated research placeholders
        fake_wallets = ["WhaleA", "WhaleB"]
        fake_twitter_hype = "🔥🔥 1,200 tweets in 30m"
        fake_telegram_hype = "2.3K members, 740 online"

        msg = f"🧠 Deep Research on {symbol}:\n\n👛 Smart Wallets: {', '.join(fake_wallets)}\n🐦 Twitter: {fake_twitter_hype}\n💬 Telegram: {fake_telegram_hype}\n\n📈 Hold or Take Profit."
        await send_telegram_message(msg)
    except Exception as e:
        logger.error(f"❌ Deep research error: {e}")

# ========== TELEGRAM SETUP ==========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper bot activated and watching the market in Obsidian Mode.")

application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .post_init(lambda app: app.create_task(scan_market_loop()))
    .build()
)

application.add_handler(CommandHandler("start", start))

@app.route("/", methods=["GET"])
def index():
    return "Sniper bot live."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    logger.info(f"📥 Incoming Telegram update: {data}")
    application.update_queue.put_nowait(Update.de_json(data, application.bot))
    return "OK"

if __name__ == "__main__":
    logger.info("✅ Telegram webhook set.")
    logger.info("🧠 Obsidian Mode active. Scanner running.")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        webhook_url=WEBHOOK_URL,
    )
