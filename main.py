import os
import time
import threading
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ENV VARS
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BIRDEYE_API = os.getenv("BIRDEYE_API")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # example: https://your-bot-name.onrender.com

# TELEGRAM
bot = Bot(BOT_TOKEN)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# FLASK
app = Flask(__name__)

# GLOBAL STATE
seen_tokens = set()
tracking = False
watchlist = []

### HANDLERS ###
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper bot ONLINE. Send 'in', 'out', or 'watch'.")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, address = query.data.split(":")
    if action == "in":
        await context.bot.send_message(chat_id=TELEGRAM_ID, text=f"🔍 Deep scan on {address} starting now...")
    elif action == "out":
        await context.bot.send_message(chat_id=TELEGRAM_ID, text=f"📈 Done tracking {address}. Closing position.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global tracking
    txt = update.message.text.lower()
    if txt == "in":
        tracking = True
        await update.message.reply_text("🧠 Deep tracking ON")
    elif txt == "out":
        tracking = False
        await update.message.reply_text("❌ Tracking OFF")
    elif txt == "watch":
        await update.message.reply_text("👀 Watching coins that are heating up...")

### FILTER + ALERT LOGIC ###
def is_alpha(coin):
    try:
        mc = coin['fdv_usd']
        vol = coin['volume_1h_quote']
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
                    btns = InlineKeyboardMarkup([
                        [InlineKeyboardButton("IN 🔍", callback_data=f"in:{address}"),
                         InlineKeyboardButton("OUT 💸", callback_data=f"out:{address}")]
                    ])
                    bot.send_message(chat_id=TELEGRAM_ID, text=text, parse_mode="HTML", reply_markup=btns)
                    seen_tokens.add(addr)
                else:
                    vol = coin.get('volume_1h_quote', 0)
                    buyers = coin.get('txns', {}).get('buys', 0)
                    if vol > 3500 and buyers >= 10 and addr not in watchlist:
                        bot.send_message(chat_id=TELEGRAM_ID, text=f"⏳ Potential: {coin['base_token']['name']} ${coin['base_token']['symbol']} is heating up...")
                        watchlist.append(addr)
        except Exception as e:
            print(f"[ERROR] token scan: {e}")
        time.sleep(10)

### WEBHOOK ROUTES ###
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok", 200

@app.route("/")
def index():
    return "🚀 Sniper Bot Running"

### INIT ###
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_button))
application.add_handler(CommandHandler("in", handle_text))
application.add_handler(CommandHandler("out", handle_text))
application.add_handler(CommandHandler("watch", handle_text))

# BACKGROUND TRACKING THREAD
t = threading.Thread(target=track_tokens)
t.daemon = True
t.start()

# SAFE WEBHOOK SETUP
@app.before_first_request
def setup_webhook():
    try:
        application.bot.delete_webhook()
        application.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        print("[✅] Webhook set successfully.")
    except Exception as e:
        print(f"[ERROR] Setting webhook: {e}")

# RUN SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
