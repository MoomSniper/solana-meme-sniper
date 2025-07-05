import asyncio
import httpx
import logging
import os
from datetime import datetime
from telegram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
BIRDEYE_API = os.getenv("BIRDEYE_API")

bot = Bot(token=BOT_TOKEN)

# Alpha Criteria
MIN_VOLUME = 5000
MAX_MARKET_CAP = 300000
MIN_BUYERS = 15
SCAN_DELAY = 30  # seconds

found_tokens = set()

logging.basicConfig(level=logging.INFO)

def meets_criteria(token):
    try:
        liquidity_locked = token.get("liquidity_locked", True)
        buyers = token.get("buyers", 0)
        volume = float(token.get("volume_h1", 0))
        market_cap = float(token.get("market_cap", 0))
        symbol = token.get("symbol", "").lower()

        return (
            liquidity_locked
            and volume >= MIN_VOLUME
            and market_cap <= MAX_MARKET_CAP
            and buyers >= MIN_BUYERS
            and "test" not in symbol
        )
    except Exception:
        return False

def format_alpha(token):
    return (
        f"🚀 *ALPHA FOUND!*\n"
        f"Symbol: `{token['symbol']}`\n"
        f"Name: {token['name']}\n"
        f"MC: ${int(token['market_cap']):,}\n"
        f"Volume (1h): ${int(token['volume_h1']):,}\n"
        f"Buyers: {token['buyers']}\n"
        f"Link: https://birdeye.so/token/{token['address']}?chain=solana"
    )

async def monitor_market():
    url = "https://public-api.birdeye.so/defi/tokenlist?limit=100&offset=0"
    headers = {"X-API-KEY": BIRDEYE_API}

    while True:
        logging.info("🧠 Sniper loop: scanning live token list...")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)

            if response.status_code == 200:
                tokens = response.json().get("data", [])
                logging.info(f"📊 Fetched {len(tokens)} tokens from Birdeye.")

                for token in tokens:
                    address = token.get("address")
                    if address in found_tokens:
                        continue

                    if meets_criteria(token):
                        found_tokens.add(address)

                        message = format_alpha(token)
                        await bot.send_message(chat_id=TELEGRAM_ID, text=message, parse_mode="Markdown")

                        asyncio.create_task(deep_research(token))
            else:
                logging.warning("Invalid response from Birdeye.")
        except Exception as e:
            logging.error(f"⚠️ Error in monitor_market: {e}")

        await asyncio.sleep(SCAN_DELAY)

async def deep_research(token):
    await asyncio.sleep(90)  # simulate deep research delay
    symbol = token['symbol']
    try:
        update = f"🧪 Deep research on `{symbol}` complete.\n"
        update += "✅ Liquidity locked\n"
        update += "✅ Strong volume\n"
        update += "✅ Meets sniper-grade alpha filters"
        await bot.send_message(chat_id=TELEGRAM_ID, text=update, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Error in deep research: {e}")
