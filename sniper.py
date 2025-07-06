import logging
import os
import asyncio
import httpx
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BIRDEYE_API = os.getenv("BIRDEYE_API")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

application = Application.builder().token(BOT_TOKEN).build()
bot = Bot(BOT_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper bot is active and monitoring in CU-safe mode.")

application.add_handler(CommandHandler("start", start))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(application.process_update(update))
    return "ok"

async def fetch_tokenlist():
    url = f"https://public-api.birdeye.so/defi/tokenlist?chain=solana"
    headers = {"X-API-KEY": BIRDEYE_API}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                tokens = data.get("data")
                if isinstance(tokens, list):
                    logger.info(f"✅ Token list received: {len(tokens)} tokens")
                    return tokens
                else:
                    logger.warning("❌ Birdeye returned non-list token data")
                    return []
            elif response.status_code == 400 and "Compute units usage limit exceeded" in response.text:
                logger.error("💥 Birdeye CU limit hit. Halting scan.")
                return []
            else:
                logger.error(f"❌ Birdeye API error {response.status_code}: {response.text}")
                return []
        except Exception as e:
            logger.error(f"❌ Error fetching token list: {e}")
            return []

async def monitor_market():
    logger.info("📊 Starting CU-safe token scan loop (1 call/min)...")
    while True:
        tokens = await fetch_tokenlist()
        logger.info(f"📊 Monitoring {len(tokens)} tokens...")
        await asyncio.sleep(60)  # Wait 60 seconds between scans

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(monitor_market())
    loop.create_task(application.initialize())
    loop.create_task(application.bot.delete_webhook())
    loop.create_task(application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}"))
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{BOT_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
