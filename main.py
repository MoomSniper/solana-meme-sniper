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
BIRDEYE_API = os.getenv("BIRDEYE_API")

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

# Real Market Scan with Filters (V2)
async def scan_market_loop():
    while True:
        try:
            logger.info("⚡️ Pulling real tokens from Birdeye...")
            url = "https://public-api.birdeye.so/public/tokenlist?sort_by=volume_1h_usd&sort_type=desc"
            headers = {"X-API-KEY": BIRDEYE_API}
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                data = response.json()

            tokens = data.get("data", {}).get("tokens", [])[:30]
            for token in tokens:
                mc = token.get("market_cap")
                vol = token.get("volume_1h_usd")
                buyers = token.get("txns_1h")
                name = token.get("name")
                address = token.get("address")

                if not all([mc, vol, buyers]):
                    continue

                if mc < 300_000 and vol > 5_000 and buyers > 15:
                    msg = f"🚨 ALPHA FOUND\n\n🪙 {name}\n💰 MC: ${mc:,.0f}\n📈 Vol (1h): ${vol:,.0f}\n🛒 Txns: {buyers}\n🔗 https://birdeye.so/token/{address}?chain=solana"
                    logger.info(msg)
                    await send_telegram_message(msg)

            await asyncio.sleep(44)

        except Exception as e:
            logger.error(f"❌ Error in market scan: {e}")
            await asyncio.sleep(44)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Obsidian Sniper Bot is now live. Watching market 24/7.")

application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .post_init(lambda app: asyncio.get_event_loop().create_task(scan_market_loop()))
    .build()
)

application.add_handler(CommandHandler("start", start))

@app.route("/", methods=["GET"])
def index():
    return "Sniper bot is live."

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
