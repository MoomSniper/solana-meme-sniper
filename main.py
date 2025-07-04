import os
import threading
import logging
import json
import time
import requests

from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# --- ENV ---
BOT_TOKEN = os.environ["BOT_TOKEN"]
TELEGRAM_ID = int(os.environ["TELEGRAM_ID"])
BIRDEYE_API = os.environ["BIRDEYE_API"]
PORT = int(os.environ.get("PORT", 10000))

# --- Setup Logging ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# --- Flask (keep Render happy) ---
app = Flask(__name__)

@app.route('/')
def root():
    return "God Mode Sniper is alive."

def run_flask():
    app.run(host="0.0.0.0", port=PORT)

threading.Thread(target=run_flask).start()

# --- Telegram Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper Bot is Active in God Mode+++++++")

# --- Birdeye Scanning Logic ---
def fetch_top_sol_tokens():
    url = "https://public-api.birdeye.so/public/tokenlist?chain=solana"
    headers = {"X-API-KEY": BIRDEYE_API}
    try:
        res = requests.get(url, headers=headers)
        data = res.json()
        tokens = data.get("data", [])
        return sorted(tokens, key=lambda x: x.get("volume_h24", 0), reverse=True)
    except Exception as e:
        logging.error(f"Error fetching tokens: {e}")
        return []

def send_alpha_alert(token):
    base_url = f"https://birdeye.so/token/{token['address']}?chain=solana"
    msg = (
        f"🧠 *Alpha Coin Detected*\n"
        f"Name: `{token['name']}`\n"
        f"Symbol: `{token['symbol']}`\n"
        f"MC: `${int(token['market_cap'])}`\n"
        f"24h Volume: `${int(token['volume_h24'])}`\n"
        f"[View on Birdeye]({base_url})"
    )
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data={
            "chat_id": TELEGRAM_ID,
            "text": msg,
            "parse_mode": "Markdown"
        }
    )

def run_sniper_loop():
    scanned = set()
    while True:
        tokens = fetch_top_sol_tokens()
        for token in tokens:
            try:
                mc = token.get("market_cap", 0)
                vol = token.get("volume_h24", 0)
                buyers = token.get("txns_h24", 0)

                if (
                    token["address"] not in scanned and
                    5000 <= vol <= 300000 and
                    10000 <= mc <= 300000 and
                    buyers >= 20
                ):
                    send_alpha_alert(token)
                    scanned.add(token["address"])
            except Exception as e:
                logging.error(f"Failed during scan loop: {e}")
        time.sleep(10)

# --- Launch Bot + Sniper ---
app_bot = ApplicationBuilder().token(BOT_TOKEN).build()
app_bot.add_handler(CommandHandler("start", start))

# Run sniper in background
threading.Thread(target=run_sniper_loop).start()

# Start bot
print("🤖 Telegram bot running...")
app_bot.run_polling()
