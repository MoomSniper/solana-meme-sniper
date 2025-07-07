import asyncio
import aiohttp
import requests
import logging
from datetime import datetime
import pytz
import json
import time
from bs4 import BeautifulSoup

TELEGRAM_ID = "6881063420"
BOT_TOKEN = "7619311236:AAFzjBR3N1oVi31J2WqU4cgZDiJgBxDPWRo"
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
HELIUS_API_KEY = "e61da153-6986-43c3-b19f-38099c1e335a"

DEXSCREENER_URL = "https://api.dexscreener.com/latest/dex/pairs/solana"
TIMEZONE = pytz.timezone("America/Toronto")

MIN_VOLUME = 5000
MAX_MARKETCAP = 300000
MIN_BUYERS = 15

async def fetch_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(DEXSCREENER_URL) as resp:
            return await resp.json()

def log(msg):
    print(f"[{datetime.now(TIMEZONE).strftime('%H:%M:%S')}] {msg}")

def send_telegram_message(message):
    try:
        payload = {
            "chat_id": TELEGRAM_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        requests.post(TELEGRAM_URL, json=payload)
    except Exception as e:
        log(f"Telegram Error: {e}")

def score_coin(coin):
    try:
        mc = coin["fdv"] or coin["marketCap"]
        vol = coin["volume"]["h1"]
        buyers = coin["txns"]["h1"]["buys"]

        score = 0
        if mc and mc < MAX_MARKETCAP:
            score += 30
        if vol and vol > MIN_VOLUME:
            score += 30
        if buyers and buyers > MIN_BUYERS:
            score += 20
        if coin.get("liquidity", {}).get("usd", 0) >= 3000:
            score += 10
        if "honeypot" in coin.get("info", {}).get("description", "").lower():
            score -= 50

        return score
    except:
        return 0

def generate_alpha_report(coin, score):
    name = coin.get("baseToken", {}).get("name", "Unknown")
    symbol = coin.get("baseToken", {}).get("symbol", "")
    mc = coin.get("fdv") or coin.get("marketCap", 0)
    vol = coin.get("volume", {}).get("h1", 0)
    buys = coin.get("txns", {}).get("h1", {}).get("buys", 0)
    dexs = coin.get("url", "")
    liq = coin.get("liquidity", {}).get("usd", 0)

    return f"""🚀 <b>ALPHA FOUND [{symbol}]</b>
🧠 Score: <b>{score}/100</b>
🪙 Market Cap: ${mc:,.0f}
📊 Volume (1h): ${vol:,.0f}
🛒 Buys (1h): {buys}
💧 Liquidity: ${liq:,.0f}
🔗 <a href="{dexs}">View on Dexscreener</a>
"""

async def check_smart_wallets(mint):
    url = f"https://api.helius.xyz/v0/tokens/{mint}/holders?api-key={HELIUS_API_KEY}"
    try:
        res = requests.get(url).json()
        count = len(res)
        return count > 10  # Placeholder condition
    except Exception as e:
        log(f"Helius error: {e}")
        return False

async def deep_research(coin):
    try:
        url = coin.get("url")
        mint = coin.get("baseToken", {}).get("address")
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        social_signals = soup.get_text().lower()

        score_boost = 0
        if "telegram" in social_signals or "twitter" in social_signals:
            score_boost += 10
        if await check_smart_wallets(mint):
            score_boost += 10

        return score_boost
    except Exception as e:
        log(f"Deep research failed: {e}")
        return 0

async def main_loop():
    alerted = set()
    while True:
        try:
            data = await fetch_data()
            for coin in data.get("pairs", []):
                address = coin.get("pairAddress")
                if not address or address in alerted:
                    continue

                score = score_coin(coin)
                if score >= 85:
                    boost = await deep_research(coin)
                    total_score = score + boost

                    if total_score >= 90:
                        msg = generate_alpha_report(coin, total_score)
                        send_telegram_message(msg)
                        alerted.add(address)

        except Exception as e:
            log(f"Main loop error: {e}")

        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main_loop())
