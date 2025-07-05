import asyncio
import logging
import httpx
import os
from telegram import Bot

BIRDEYE_API_KEY = os.getenv("BIRDEYE_API")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)

# Basic logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def fetch_token_list():
    url = "https://public-api.birdeye.so/defi/tokenlist?limit=100&offset=0"
    headers = {"X-API-KEY": BIRDEYE_API_KEY}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            elif response.status_code == 429:
                logging.warning("Birdeye rate limit hit. Skipping scan.")
            else:
                logging.error(f"Unexpected response {response.status_code}: {response.text}")
    except Exception as e:
        logging.error(f"Exception while fetching tokens: {e}")
    return []

async def scan_birdeye():
    logging.info("\U0001F9E0 Sniper loop: scanning live token list...")
    tokens = await fetch_token_list()

    if not tokens:
        logging.info("No tokens returned, skipping alert.")
        return

    for token in tokens:
        # Basic example filter (expand with alpha-grade filters later)
        if token.get("liquidity", 0) > 10000 and token.get("volume_h1", 0) > 5000:
            name = token.get("name")
            address = token.get("address")
            mc = token.get("market_cap", 0)
            vol = token.get("volume_h1", 0)
            liquidity = token.get("liquidity", 0)

            msg = f"\U0001F525 *ALPHA COIN FOUND*
Name: {name}
Market Cap: ${mc:,.0f}
1H Volume: ${vol:,.0f}
Liquidity: ${liquidity:,.0f}
Address: `{address}`"

            await bot.send_message(chat_id=TELEGRAM_ID, text=msg, parse_mode="Markdown")

async def main_loop():
    while True:
        await scan_birdeye()
        await asyncio.sleep(30)  # Run every 30 seconds

if __name__ == "__main__":
    asyncio.run(main_loop())
