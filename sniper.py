import asyncio
import os
import logging
import httpx
from telegram import Bot

BIRDEYE_API = os.getenv("BIRDEYE_API")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
bot = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

async def fetch_tokens():
    headers = {"X-API-KEY": BIRDEYE_API}
    url = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json().get("data", [])
    except httpx.HTTPStatusError as e:
        logger.warning(f"Fetch error: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []

def meets_criteria(token):
    try:
        txns = token.get("txns", {}).get("h1", {})
        volume = float(token.get("volume_h1_usd", 0))
        buys = int(txns.get("buys", 0))
        sells = int(txns.get("sells", 0))
        holders = int(token.get("holders", 0))

        return (
            25000 <= volume <= 500000 and
            buys >= 25 and
            sells <= 20 and
            holders >= 50
        )
    except Exception as e:
        logger.error(f"Error checking criteria: {e}")
        return False

async def deep_research(token):
    name = token.get("name")
    address = token.get("address")
    mc = token.get("market_cap", "N/A")
    holders = token.get("holders", "N/A")

    msg = (
        f"ð Deep Research Mode Initiated
"
        f"Name: {name}
"
        f"Address: {address}
"
        f"Market Cap: {mc}
"
        f"Holders: {holders}
"
        f"Phase: Obsidian++ filtering in progress...
"
    )
    await bot.send_message(chat_id=TELEGRAM_ID, text=msg)

async def monitor_market(_bot: Bot):
    global bot
    bot = _bot
    await bot.send_message(chat_id=TELEGRAM_ID, text="â Sniper Bot is live and scanning the market.")
    while True:
        tokens = await fetch_tokens()
        filtered = [t for t in tokens if meets_criteria(t)]
        if filtered:
            alpha = filtered[0]
            await bot.send_message(chat_id=TELEGRAM_ID, text="ð¨ Alpha Detected â Entering Deep Research...")
            await asyncio.sleep(90)
            await deep_research(alpha)
        await asyncio.sleep(12)  # Throttle to protect API
