import os
import httpx
import asyncio
import logging
from datetime import datetime, timedelta

TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BIRDEYE_API = os.getenv("BIRDEYE_API")
headers = {"X-API-KEY": BIRDEYE_API}

logging.basicConfig(level=logging.INFO)

# Core Filter Criteria
def is_alpha(token):
    try:
        if token.get("marketCap", 0) > 300_000:
            return False
        if token.get("marketCap", 0) < 10_000:
            return False

        if token.get("liquidity", {}).get("locked", False) is not True:
            return False

        if token.get("volume_1h", 0) < 10_000:
            return False

        if token.get("buyers", 0) < 20:
            return False

        if token.get("price_change_percentage_1h", 0) < 150:
            return False

        if not token.get("smart_wallet", False):
            return False

        if not token.get("telegram_hype", False):
            return False

        if not token.get("x_hype", False):
            return False

        return True

    except Exception as e:
        logging.warning(f"Filter error: {e}")
        return False

# Simulate alpha scoring system
def score_alpha(token):
    score = 0
    if token.get("price_change_percentage_1h", 0) > 150:
        score += 25
    if token.get("smart_wallet", False):
        score += 25
    if token.get("telegram_hype", False):
        score += 25
    if token.get("x_hype", False):
        score += 25
    return score

# Simulated deep research
async def run_deep_research(bot, token):
    await asyncio.sleep(90)
    msg = f"""
🧠 DEEP RESEARCH MODE
Name: {token.get('name')}
Hype Score: {score_alpha(token)} / 100
Smart Wallets Still Buying: Yes
Liquidity Locked: ✅
Prediction: 3×–25× potential
"""
    await bot.send_message(chat_id=TELEGRAM_ID, text=msg)

# Birdeye token fetch
async def fetch_token_list():
    url = "https://public-api.birdeye.so/defi/tokenlist?limit=100&offset=0"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            logging.warning("Invalid response from Birdeye.")
            return []
        data = response.json()
        return data.get("data", {}).get("tokens", [])

# Main sniper loop
async def monitor_market(bot):
    while True:
        logging.info("🧠 Sniper loop: scanning live token list...")
        try:
            tokens = await fetch_token_list()
            logging.info(f"📊 Fetched {len(tokens)} tokens from Birdeye.")
        except Exception as e:
            await bot.send_message(chat_id=TELEGRAM_ID, text=f"❌ Birdeye error: {e}")
            await asyncio.sleep(60)
            continue

        for token in tokens:
            if is_alpha(token):
                msg = f"""
🎯 ALPHA COIN DETECTED
Name: {token.get('name', 'N/A')}
Symbol: {token.get('symbol', 'N/A')}
Score: {score_alpha(token)} / 100
Chart: https://birdeye.so/token/{token.get('address')}
"""
                await bot.send_message(chat_id=TELEGRAM_ID, text=msg)
                asyncio.create_task(run_deep_research(bot, token))

        await asyncio.sleep(6)  # Scan every ~6 seconds
