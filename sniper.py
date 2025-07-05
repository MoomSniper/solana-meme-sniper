import os
import httpx
import asyncio
import logging

TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BIRDEYE_API = os.getenv("BIRDEYE_API")

birdeye_headers = {"X-API-KEY": BIRDEYE_API}
active_coin = None

# Example known smart wallets (replace or update later)
smart_wallets = ["6hfG...xyz", "2T7P...abc"]

async def fetch_token_list():
    url = "https://public-api.birdeye.so/defi/tokenlist?limit=50&offset=0"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=birdeye_headers)
        return resp.json().get("data", {}).get("tokens", [])

async def fetch_trades(token_address):
    url = f"https://public-api.birdeye.so/defi/token/{token_address}/trades"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=birdeye_headers)
        trades = resp.json().get("data", {}).get("items", [])
        return trades

async def analyze_token(bot, token):
    global active_coin
    if active_coin: return  # already tracking one
    trades = await fetch_trades(token["address"])
    if len(trades) < 10: return

    buyers = sum(1 for t in trades if t["side"] == "buy")
    sellers = sum(1 for t in trades if t["side"] == "sell")
    volume = sum(float(t["amount"]) for t in trades)
    price = float(trades[-1]["price"]) if trades else 0

    alpha = (
        token["fdv"] and token["fdv"] < 300000 and
        volume > 5000 and
        buyers > sellers
    )

    if alpha:
        active_coin = token["address"]
        msg = f"""
🚨 ALPHA COIN DETECTED
Name: {token['name']}
Symbol: {token['symbol']}
Buyers: {buyers} | Sellers: {sellers}
1H Volume: ${volume:,.2f}
Price: ${price}
Chart: https://birdeye.so/token/{token['address']}
"""
        await bot.send_message(chat_id=TELEGRAM_ID, text=msg)

        # Start deep research loop
        asyncio.create_task(deep_research(bot, token["address"]))

async def deep_research(bot, token_address):
    global active_coin
    score = 100
    while active_coin == token_address:
        trades = await fetch_trades(token_address)
        buyers = sum(1 for t in trades if t["side"] == "buy")
        sellers = sum(1 for t in trades if t["side"] == "sell")
        volume = sum(float(t["amount"]) for t in trades)
        price = float(trades[-1]["price"]) if trades else 0

        # Logic-based scoring
        if volume < 3000 or sellers > buyers:
            await bot.send_message(chat_id=TELEGRAM_ID, text="⚠️ Exit — volume fading or sell pressure.")
            active_coin = None
            break
        elif volume > 10000:
            await bot.send_message(chat_id=TELEGRAM_ID, text="✅ HOLD — strong push, good momentum.")
        elif volume > 7000:
            await bot.send_message(chat_id=TELEGRAM_ID, text="💰 Partial Take Profit — steady but watch carefully.")

        # Social placeholder
        score -= 1  # Fake social score decay logic
        if score < 70:
            await bot.send_message(chat_id=TELEGRAM_ID, text=f"⚠️ Social score dropping ({score}%) — re-evaluate soon.")

        summary = f"""
🧠 Deep Scan Update
Buyers: {buyers} | Sellers: {sellers}
Volume: ${volume:,.2f}
Price: ${price}
Score: {score}%
Chart: https://birdeye.so/token/{token_address}
"""
        await bot.send_message(chat_id=TELEGRAM_ID, text=summary)
        await asyncio.sleep(60)

async def monitor_market(bot):
    logging.info("🧠 Sniper loop: scanning live token list...")
    tokens = await fetch_token_list()

    # Just pick the first coin to prove it's working
    if tokens:
        token = tokens[0]
        msg = f"""
🔍 TESTING LIVE COIN SCAN
Name: {token['name']}
Symbol: {token['symbol']}
FDV: ${token['fdv']:,.0f}
Chart: https://birdeye.so/token/{token['address']}
"""
        await bot.send_message(chat_id=TELEGRAM_ID, text=msg)

    # Resume normal alpha scanning after test
    while True:
        tokens = await fetch_token_list()
        for token in tokens:
            try:
                await analyze_token(bot, token)
            except Exception as e:
                logging.error(f"Error analyzing token: {e}")
        await asyncio.sleep(10)
