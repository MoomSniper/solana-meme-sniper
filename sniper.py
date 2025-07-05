import httpx
import asyncio
import logging
import re

TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
BIRDEYE_API = os.getenv("BIRDEYE_API")

birdeye_headers = {"X-API-KEY": BIRDEYE_API}

sniper_watchlist = {}
active_coin = None

def is_bot_hype(message_list):
    return any("airdrops" in m.lower() or "invite" in m.lower() for m in message_list)

async def fetch_social_data(coin):
    async with httpx.AsyncClient() as client:
        # Placeholder endpoints, customize based on coin metadata
        tg_resp = await client.get(f"https://api.telegram.org/{coin['telegram_url']}")
        tw_resp = await client.get(f"https://api.twitter.com/{coin['twitter_url']}")
        tg_hype = tg_resp.json().get("messages", [])
        tw_hype = tw_resp.json().get("tweets", [])
        fake_tg = is_bot_hype(tg_hype)
        fake_tw = is_bot_hype(tw_hype)
        score = 100
        if fake_tg or fake_tw:
            score -= 40
        if len(tw_hype) < 5 or len(tg_hype) < 10:
            score -= 30
        return score, not (fake_tg or fake_tw)

async def scan_coin(coin_id):
    async with httpx.AsyncClient() as client:
        # Replace this with your actual Birdeye endpoint logic
        resp = await client.get(f"https://public-api.birdeye.so/defi/token/{coin_id}/trades", headers=birdeye_headers)
        trades = resp.json().get("data", {}).get("items", [])
        buyers = sum(1 for t in trades if t["side"] == "buy")
        sellers = sum(1 for t in trades if t["side"] == "sell")
        volume = sum(float(t["amount"]) for t in trades)
        price = float(trades[-1]["price"]) if trades else 0

        alpha = (buyers > sellers and volume > 5000 and price > 0)
        return {
            "buyers": buyers,
            "sellers": sellers,
            "volume": volume,
            "price": price,
            "alpha": alpha,
            "url": f"https://birdeye.so/token/{coin_id}"
        }

async def deep_research_loop(bot, coin_id):
    global active_coin
    active_coin = coin_id
    max_score = 0
    while active_coin == coin_id:
        result = await scan_coin(coin_id)
        score, legit = await fetch_social_data({"telegram_url": "placeholder", "twitter_url": "placeholder"})  # Customize later

        score_summary = f"""
🧠 Deep Scan on [{coin_id}]
Price: ${result['price']:.4f}
Buyers: {result['buyers']} | Sellers: {result['sellers']}
Volume: ${result['volume']:.2f}
Social Score: {score}%
Telegram + Twitter: {"Legit" if legit else "Botted"}
Chart: {result['url']}
"""

        await bot.send_message(chat_id=TELEGRAM_ID, text=score_summary)

        if result["volume"] < 3000 or result["buyers"] < result["sellers"]:
            await bot.send_message(chat_id=TELEGRAM_ID, text="⚠️ Volume fading — consider EXIT")
            active_coin = None
            break
        elif result["volume"] > 10000 and legit:
            await bot.send_message(chat_id=TELEGRAM_ID, text="✅ HOLD — strong social + volume")
        elif result["volume"] > 8000:
            await bot.send_message(chat_id=TELEGRAM_ID, text="💰 Partial Take Profit — steady momentum")

        await asyncio.sleep(60)

def add_to_watch(coin_id):
    sniper_watchlist[coin_id] = {"watched": True}

def clear_active():
    global active_coin
    active_coin = None
