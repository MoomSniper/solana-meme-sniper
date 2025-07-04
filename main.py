import os
import time
import threading
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

# ENVIRONMENT
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BIRDEYE_API = os.getenv("BIRDEYE_API")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# TELEGRAM BOT SETUP
bot = Bot(token=BOT_TOKEN)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# FLASK
app = Flask(__name__)

# GLOBALS
seen_tokens = set()
watchlist = []

# ==== HANDLERS ==== #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper bot is LIVE. Send 'in' to track, 'out' to stop.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.lower()
    if message == "in":
        await update.message.reply_text("🧠 Deep tracking mode enabled.")
    elif message == "out":
        await update.message.reply_text("🛑 Tracking stopped.")
    elif message == "watch":
        await update.message.reply_text("👀 Watching hot coins...")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, address = query.data.split(":")
    if action == "in":
        await context.bot.send_message(chat_id=TELEGRAM_ID, text=f"🔍 Deep scan on {address} started.")
    elif action == "out":
        await context.bot.send_message(chat_id=TELEGRAM_ID, text=f"📤 Stopped tracking {address}.")

# ==== SNIPER LOGIC ==== #
def is_alpha(coin):
    try:
        mc = coin.get('fdv_usd')
        vol = coin.get('volume_1h_quote')
        buyers = coin['txns']['buys']
        has_socials = coin['dex_info'].get('telegram') and coin['dex_info'].get('twitter')
        return mc and mc < 300000 and vol > 5000 and buyers >= 15 and has_socials
    except:
        return False

def alert_msg(coin):
    name = coin['base_token']['name']
    symbol = coin['base_token']['symbol']
    addr = coin['address']
    mc = round(coin['fdv_usd'])
    vol = round(coin['volume_1h_quote'])
    return f"🔥 <b>{name}</b> (${symbol})\nMarket Cap: ${mc}\nVolume: ${vol}\n<a href='https://birdeye.so/token/{addr}?chain=solana'>Birdeye</a>", addr

def track_tokens():
    global seen_tokens
    while True:
        try:
            res = requests.get(
                "https://public-api.birdeye.so/public/tokenlist?sort=volume_1h&order=desc&limit=50&chain=solana",
                headers={"X-API-KEY": BIRDEYE_API}
            )
            tokens = res.json().get("data", [])
            for coin in tokens:
                addr = coin.get("address")
                if not addr or addr in seen_tokens:
                    continue
                if is_alpha(coin):
                    text, address = alert_msg(coin)
                    buttons = InlineKeyboardMarkup([
                        [InlineKeyboardButton("IN 🔍", callback_data=f"in:{address}"),
                         InlineKeyboardButton("OUT 💸", callback_data=f"out:{address}")]
                    ])
                    bot.send_message(chat_id=TELEGRAM_ID, text=text, parse_mode="HTML", reply_markup=buttons)
                    seen_tokens.add(addr)
                elif coin.get('volume_1h_quote', 0) > 3500 and coin.get('txns', {}).get('buys', 0) >= 10:
                    if addr not in watchlist:
                        bot.send_message(chat_id=TELEGRAM_ID, text=f"⏳ {coin['base_token']['name']} is heating up.")
                        watchlist.append(addr)
        except Exception as e:
            print(f"[SNIPER ERROR] {e}")
        time.sleep(10)

# ==== FLASK ROUTES ==== #
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

@app.route("/", methods=["GET"])
def home():
    return "🚀 Sniper Bot Running", 200

# ==== MAIN EXEC ==== #
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_button))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# BACKGROUND THREAD
threading.Thread(target=track_tokens, daemon=True).start()

if __name__ == "__main__":
    import asyncio
    async def setup():
        await application.bot.delete_webhook()
        await application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        application.run_polling()

    asyncio.run(setup())
    app.run(host="0.0.0.0", port=10000)
