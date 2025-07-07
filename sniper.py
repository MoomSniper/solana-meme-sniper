import asyncio
import aiohttp
import time
import json
import os
from datetime import datetime
import logging
from telegram import Bot

TELEGRAM_ID = os.getenv("TELEGRAM_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
HELIUS_API = os.getenv("HELIUS_API")

bot = Bot(token=BOT_TOKEN)

# === CONFIG ===
MIN_VOLUME = 5000
MAX_MARKETCAP = 300000
ALPHA_SCORE_THRESHOLD = 85
ENTRY_SCORE_THRESHOLD = 90
WATCH_MODE_SCORE_MIN = 70
RECHECK_INTERVAL = 3
DEEP_SCAN_TRIGGER_TIME = 90

# === TRACKING ===
active_calls = {}
watchlist = []
pnl_log = {}

# === LOGGING ===
logging.basicConfig(level=logging.INFO)

async def fetch_coin_data():
    # Placeholder - replace with live websocket logic later
    return [
        {
            "name": "ICE",
            "volume": 15000,
            "market_cap": 220000,
            "buyers": 300,
            "url": "https://dexscreener.com/solana/ICE",
            "launch_time": datetime.utcnow().timestamp() - 20
        },
    ]

def score_coin(coin):
    score = 0
    if coin["volume"] > MIN_VOLUME:
        score += 30
    if coin["market_cap"] < MAX_MARKETCAP:
        score += 30
    if coin["buyers"] > 100:
        score += 20
    if "ice" in coin["name"].lower():
        score += 10  # Example narrative boost
    return score

async def send_alert(coin, score):
    msg = f"""🚨 *ALPHA ALERT* 🚨

*{coin['name']}*
• Volume: ${coin['volume']}
• Market Cap: ${coin['market_cap']}
• Buyers: {coin['buyers']}
• Alpha Score: {score}/100

[Open in Dexscreener]({coin['url']})
Type `in 50` if you enter.

#AlphaSniperBot"""
    await bot.send_message(chat_id=TELEGRAM_ID, text=msg, parse_mode='Markdown')
    active_calls[coin['name']] = {
        "data": coin,
        "start_time": time.time(),
        "entered": False,
        "entry_amount": 0,
        "profit_taken": 0
    }

async def deep_research(coin_name):
    # Placeholder for contract checks, smart wallets, TG/X scraping, etc.
    print(f"🔍 Deep scanning {coin_name}...")

    # Simulate exit logic
    await asyncio.sleep(5)
    exit_msg = f"📤 EXIT NOW: {coin_name} showing volume decay + smart wallet exit."
    await bot.send_message(chat_id=TELEGRAM_ID, text=exit_msg)

async def check_active_calls():
    now = time.time()
    for coin_name, details in list(active_calls.items()):
        if not details["entered"] and now - details["start_time"] > DEEP_SCAN_TRIGGER_TIME:
            await deep_research(coin_name)

async def watch_for_new_coins():
    while True:
        coins = await fetch_coin_data()
        for coin in coins:
            score = score_coin(coin)
            if score >= ENTRY_SCORE_THRESHOLD and coin['name'] not in active_calls:
                await send_alert(coin, score)
            elif score >= WATCH_MODE_SCORE_MIN and coin['name'] not in watchlist:
                watchlist.append(coin['name'])
        await check_active_calls()
        await asyncio.sleep(RECHECK_INTERVAL)

# === COMMAND INTERFACE ===
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from flask import Flask, request

app = Flask(__name__)
application = Application.builder().token(BOT_TOKEN).build()

async def handle_in(update, context):
    try:
        parts = update.message.text.strip().split()
        if len(parts) == 2:
            coin_name = list(active_calls.keys())[-1]
            amount = float(parts[1])
            active_calls[coin_name]["entered"] = True
            active_calls[coin_name]["entry_amount"] = amount
            pnl_log[coin_name] = {"in": amount, "out": 0}
            await update.message.reply_text(f"💰 Logged ${amount} into {coin_name}")
        else:
            await update.message.reply_text("Usage: in 50")
    except Exception as e:
        await update.message.reply_text("Error logging entry.")

async def handle_profit(update, context):
    try:
        parts = update.message.text.strip().split()
        if len(parts) == 2:
            coin_name = list(active_calls.keys())[-1]
            amount = float(parts[1])
            pnl_log[coin_name]["out"] += amount
            await update.message.reply_text(f"✅ Logged profit of ${amount} for {coin_name}")
        else:
            await update.message.reply_text("Usage: tp 80")
    except:
        await update.message.reply_text("Error logging profit.")

async def handle_alpha(update, context):
    best = max(active_calls.items(), key=lambda x: score_coin(x[1]["data"]), default=None)
    if best:
        coin = best[1]["data"]
        await update.message.reply_text(f"🔥 Best Alpha Now: {coin['name']} – ${coin['market_cap']} MC – {coin['volume']} Vol")
    else:
        await update.message.reply_text("No alpha coins active.")

application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^in \d+'), handle_in))
application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'^tp \d+'), handle_profit))
application.add_handler(CommandHandler("alpha", handle_alpha))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    application.update_queue.put_nowait(request.get_json(force=True))
    return "ok"

async def run():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(f"{os.getenv('WEBHOOK_URL')}/{BOT_TOKEN}")
    await watch_for_new_coins()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(run())
