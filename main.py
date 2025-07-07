import os
import time
import threading
import requests
from telegram import Bot
from flask import Flask, request

TELEGRAM_ID = os.getenv("TELEGRAM_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
HELIUS_API = os.getenv("HELIUS_API")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "sniper_secret")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

active_alpha = {}

def send_telegram(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_ID, text=msg)
    except Exception as e:
        print(f"[ERROR] Telegram send failed: {e}")

def get_new_coins():
    try:
        res = requests.get("https://api.dexscreener.com/latest/dex/pairs/solana")
        data = res.json().get("pairs", [])
        return data
    except Exception as e:
        print(f"[ERROR] Fetching pairs failed: {e}")
        return []

def is_coin_alpha(coin):
    try:
        mc = float(coin["fdv"] or 0)
        vol = float(coin["volume"]["h1"] or 0)
        buyers = int(coin.get("txns", {}).get("h1", {}).get("buys", 0))
        score = 0

        if mc < 300000: score += 25
        if vol > 5000: score += 25
        if buyers > 25: score += 25
        if "t.me/" in (coin.get("info", {}).get("socials", {}).get("telegram", "") + ""): score += 25

        return score >= 85, score
    except:
        return False, 0

def run_deep_research(coin):
    address = coin["pairAddress"]
    try:
        wallet_res = requests.get(f"https://api.helius.xyz/v0/addresses/{address}/balances?api-key={HELIUS_API}")
        wallets = wallet_res.json()
        top_wallets = [w for w in wallets if float(w.get("amount", 0)) > 1000]
        send_telegram(f"🔍 Deep Research Triggered for {coin['baseToken']['symbol']}\nSmart wallets: {len(top_wallets)}")
    except Exception as e:
        send_telegram(f"[ERROR] Deep Research failed: {e}")

def start_tracking(coin):
    symbol = coin["baseToken"]["symbol"]
    address = coin["pairAddress"]
    active_alpha[address] = {
        "symbol": symbol,
        "start_time": time.time(),
        "entry_price": float(coin["priceUsd"]),
    }

    send_telegram(f"🚀 ALPHA FOUND: ${symbol}\n🔹Entry: ${coin['priceUsd']}\n🔹MC: {coin['fdv']}\n🔹Vol/h1: {coin['volume']['h1']}")
    threading.Timer(90, run_deep_research, [coin]).start()

def check_tracked():
    for address, data in list(active_alpha.items()):
        try:
            res = requests.get(f"https://api.dexscreener.com/latest/dex/pairs/solana/{address}")
            coin = res.json()["pair"]
            current_price = float(coin["priceUsd"])
            entry = data["entry_price"]
            ratio = current_price / entry

            if ratio >= 2:
                send_telegram(f"💰 {data['symbol']} has hit 2x. HOLD or TP suggested.\n📈 Current: ${current_price}")
            elif ratio < 0.6:
                send_telegram(f"⚠️ {data['symbol']} tanking. Recommend EXIT.\n📉 Current: ${current_price}")
        except Exception as e:
            print(f"[ERROR] Track check failed: {e}")

def loop_sniper():
    scanned = set()
    while True:
        coins = get_new_coins()
        for coin in coins:
            address = coin["pairAddress"]
            if address in scanned or address in active_alpha: continue

            valid, score = is_coin_alpha(coin)
            if valid:
                start_tracking(coin)
                scanned.add(address)

        check_tracked()
        time.sleep(3)

@app.route(f"/{WEBHOOK_SECRET}", methods=["POST"])
def handle_webhook():
    data = request.json
    if "message" in data:
        text = data["message"].get("text", "").strip().lower()
        if "/status" in text:
            tracked = "\n".join([f"- {v['symbol']}" for v in active_alpha.values()]) or "No active alpha."
            send_telegram(f"🔎 Currently Tracking:\n{tracked}")
    return "ok", 200

def run_bot():
    threading.Thread(target=loop_sniper).start()
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    run_bot()
