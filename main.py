import os
import logging
import asyncio
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import httpx

# Load environment variables
BOT_TOKEN = os.environ["BOT_TOKEN"]
TELEGRAM_ID = int(os.environ["TELEGRAM_ID"])
BIRDEYE_API = os.environ["BIRDEYE_API"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)

# Telegram bot & app
bot = Bot(token=BOT_TOKEN)
application = Application.builder().token(BOT_TOKEN).build()

# Watchlist + radar
watchlist = set()
radar = []

# Send message util
async def send_msg(text):
    await bot.send_message(chat_id=TELEGRAM_ID, text=text)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 God Mode Sniper is live.")

# /watch command to show radar
async def watch(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not radar:
        await update.message.reply_text("🟡 Radar is currently empty. Watching closely.")
    else:
        msg = "🔭 **Radar Targets:**\n" + "\n".join(f"- {coin}" for coin in radar)
        await update.message.reply_text(msg)

# in/out commands
async def in_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0] if context.args else None
    if not coin:
        await update.message.reply_text("❌ No token address provided.")
        return
    watchlist.add(coin)
    await update.message.reply_text(f"📍 Locked on: {coin}\nRunning deep scan now...")
    await deep_scan(coin)

async def out_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coin = context.args[0] if context.args else None
    if not coin:
        await update.message.reply_text("❌ No token address provided.")
        return
    if coin in watchlist:
        watchlist.remove(coin)
        await update.message.reply_text(f"🚫 Removed from tracking: {coin}")
    else:
        await update.message.reply_text(f"{coin} is not being tracked.")

# Deep scan logic
async def deep_scan(address):
    try:
        url = f"https://public-api.birdeye.so/defi/token_info?address={address}"
        headers = {"X-API-KEY": BIRDEYE_API}
        async with httpx.AsyncClient() as client:
            r = await client.get(url, headers=headers)
            data = r.json().get("data", {})

        if not data:
            await send_msg(f"❌ No data found for {address}")
            return

        volume = float(data.get("volume_1h", 0))
        buyers = int(data.get("tx_count_1h", 0))
        mc = float(data.get("market_cap", 0))

        if volume > 10000 and buyers >= 20 and mc < 300000:
            await send_msg(f"✅ **ALPHA FOUND**\n{address}\nMC: ${int(mc)}\nVol(1h): ${int(volume)}\nBuyers(1h): {buyers}")
        else:
            radar.append(address)
            await send_msg(f"🟠 Radar Mode: {address} — Watching for breakout.")
    except Exception as e:
        logger.error(f"Deep scan error: {e}")
        await send_msg("❌ Deep scan failed.")

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("watch", watch))
application.add_handler(CommandHandler("in", in_cmd))
application.add_handler(CommandHandler("out", out_cmd))

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    try:
        update = Update.de_json(request.get_json(force=True), bot)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.process_update(update))
        return "ok"
    except Exception as e:
        logger.error(f"Exception in telegram_webhook: {e}")
        return "error"

# Main runner
if __name__ == "__main__":
    logger.info("✅ Launching God Mode Sniper...")
    application.run_polling()  # this won't actually run since we use webhook

# Set webhook
async def set_webhook():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info(f"✅ Webhook set: {WEBHOOK_URL}/{BOT_TOKEN}")

# Fire up Flask
if __name__ != "__main__":
    asyncio.run(set_webhook())
