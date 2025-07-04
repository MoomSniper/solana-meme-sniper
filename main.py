import os
import threading
import requests
import time
import asyncio
from fastapi import FastAPI, Request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BIRDEYE_API = os.getenv("BIRDEYE_API")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

bot = Bot(BOT_TOKEN)
app = FastAPI()

application = Application.builder().token(BOT_TOKEN).build()

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
    msg = update.message.text.lower()
    if msg == "in":
        tracking = True
        await update.message.reply_text("🧠 Deep tracking ON")
    elif msg == "out":
        tracking = False
        await update.message.reply_text("❌ Tracking OFF")
    elif msg == "watch":
        await update.message.reply_text("👀 Watching coins heating up...")

### ALPHA LOGIC ###
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
                    btns = InlineKeyboardMarkup([[InlineKeyboardButton("IN 🔍", callback_data=f"in:{address}"),
                                                  InlineKeyboardButton("OUT 💸", callback_data=f"out:{address}")]])
                    bot.send_message(chat_id=TELEGRAM_ID, text=text, parse_mode="HTML", reply_markup=btns)
                    seen_tokens.add(addr)
                else:
                    vol = coin.get('volume_1h_quote', 0)
                    buyers = coin.get('txns', {}).get('buys', 0)
                    if vol > 3500 and buyers >= 10 and addr not in watchlist:
                        bot.send_message(chat_id=TELEGRAM_ID, text=f"⏳ Potential: {coin['base_token']['name']} ${coin['base_token']['symbol']} is heating up...")
                        watchlist.append(addr)
        except Exception as e:
            print(f"Tracking error: {e}")
        time.sleep(10)

### FASTAPI ROUTES ###
@app.post(f"/{BOT_TOKEN}")
async def telegram_webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, bot)
    await application.process_update(update)
    return {"ok": True}

@app.get("/")
def index():
    return {"status": "🚀 Bot Running"}

### INIT ###
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_button))
application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))

threading.Thread(target=track_tokens, daemon=True).start()

if __name__ == "__main__":
    async def run():
        await application.initialize()
        await application.bot.delete_webhook()
        await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
        await application.start()
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=10000)

    asyncio.run(run())
