import os
import logging
import asyncio
import httpx
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BOT_TOKEN = os.getenv("BOT_TOKEN")
BIRDEYE_API = os.getenv("BIRDEYE_API", "e3c36a11a7614498b29940e077b1f230")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

app = Flask(__name__)

# Initialize Telegram Bot
bot = Bot(token=BOT_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is live and ready to snipe.")

# Define your CU-safe sniper scan logic
async def monitor_market():
    url = f"https://public-api.birdeye.so/defi/tokenlist?chain=solana"
    headers = {"X-API-KEY": BIRDEYE_API}
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data.get("data"), list):
                        logger.info(f"📊 Monitoring {len(data['data'])} tokens...")
                    else:
                        logger.warning("❌ Birdeye returned non-list token data")
                elif response.status_code == 400 and "usage limit exceeded" in response.text.lower():
                    logger.error("💥 Birdeye CU limit hit. Halting scan.")
                    break
                else:
                    logger.warning(f"⚠️ Birdeye API error {response.status_code}: {response.text}")
            except Exception as e:
                logger.error(f"❌ Exception: {e}")
            await asyncio.sleep(60)  # CU-safe interval

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK"

@app.route("/")
def root():
    return "Bot is running."

async def main():
    global application
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Set webhook
    await bot.delete_webhook()
    await bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{BOT_TOKEN}")

    # Start sniper logic
    logger.info("🚀 Starting market monitor...")
    asyncio.create_task(monitor_market())

    await application.initialize()
    await application.start()

if __name__ == '__main__':
    asyncio.run(main())
    app.run(host="0.0.0.0", port=PORT)
