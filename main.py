# main.py
import os
import json
import time
import threading
import requests
from flask import Flask, request
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Dispatcher, CommandHandler, CallbackQueryHandler

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BIRDEYE_API = os.getenv("BIRDEYE_API")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot=bot, update_queue=None, workers=4, use_context=True)

seen_tokens = set()
tracking = False
watchlist = []

### HANDLERS ###
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="\ud83d\ude80 Sniper bot ONLINE. Send 'in', 'out', or 'watch'.")

def handle_button(update, context):
    query = update.callback_query
    query.answer()
    action, address = query.data.split(":")

    if action == "in":
        context.bot.send_message(chat_id=TELEGRAM_ID, text=f"\ud83d\udd0d Deep scan on {address} starting now...")
    elif action == "out":
        context.bot.send_message(chat_id=TELEGRAM_ID, text=f"\ud83d\udcc8 Done tracking {address}. Closing position.")

def handle_text(update, context):
    global tracking
    txt = update.message.text.lower()
    if txt == "in":
        tracking = True
        update.message.reply_text("\ud83e\udde0 Deep tracking ON")
    elif txt == "out":
        tracking = False
        update.message.reply_text("\u274c Tracking OFF")
    elif txt == "watch":
        update.message.reply_text("\ud83d\udc40 Watching coins that are heating up...")

### FLASK ENDPOINT ###
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dp.process_update(update)
    return "ok"

@app.route("/")
def index():
    return "\ud83d\ude80 Bot running."

### ALERTING ###
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
    return f"\ud83d\udd25 <b>{name}</b> (${symbol})\nMarket Cap: ${mc}\nVolume: ${vol}\n<a href='https://birdeye.so/token/{addr}?chain=solana'>Birdeye</a>", addr

def track_tokens():
    global seen_tokens
    while True:
        try:
            res = requests.get("https://public-api.birdeye.so/public/tokenlist?sort=volume_1h&order=desc&limit=50&chain=solana",
                               headers={"X-API-KEY": BIRDEYE_API})
            tokens = res.json().get("data", [])

            for coin in tokens:
                addr = coin.get("address")
                if not addr or addr in seen_tokens:
                    continue

                if is_alpha(coin):
                    text, address = alert_msg(coin)
                    btns = InlineKeyboardMarkup([[InlineKeyboardButton("IN \ud83d\udd0d", callback_data=f"in:{address}"),
                                                  InlineKeyboardButton("OUT \ud83d\udcb8", callback_data=f"out:{address}")]])
                    bot.send_message(chat_id=TELEGRAM_ID, text=text, parse_mode="HTML", reply_markup=btns)
                    seen_tokens.add(addr)
                else:
                    # Watchlist potential
                    vol = coin.get('volume_1h_quote', 0)
                    buyers = coin.get('txns', {}).get('buys', 0)
                    if vol > 3500 and buyers >= 10 and addr not in watchlist:
                        bot.send_message(chat_id=TELEGRAM_ID, text=f"\u231b Potential: {coin['base_token']['name']} ${coin['base_token']['symbol']} is heating up...")
                        watchlist.append(addr)

        except Exception as e:
            print(f"Error tracking: {e}")
        time.sleep(10)

### INIT ###
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CallbackQueryHandler(handle_button))
dp.add_handler(CommandHandler("in", handle_text))
dp.add_handler(CommandHandler("out", handle_text))
dp.add_handler(CommandHandler("watch", handle_text))

t = threading.Thread(target=track_tokens)
t.start()

if __name__ == '__main__':
    bot.delete_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    app.run(host='0.0.0.0', port=10000)
