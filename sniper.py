import os
import asyncio
import logging
import httpx
from telegram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

TELEGRAM_ID = os.getenv("TELEGRAM_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BIRDEYE_API = os.getenv("BIRDEYE_API")

bot = Bot(token=BOT_TOKEN)

async def send_to_telegram(text):
    try:
        await bot.send_message(chat_id=TELEGRAM_ID, text=text)
    except Exception as e:
        logger.error(f"Telegram send error: {e}")

async def fetch_tokens():
    url = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
    headers = {"X-API-KEY": BIRDEYE_API}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(f"Birdeye raw data: {data}")  # 👈 This will print the full response
            token_list = data.get("data", [])
            if not isinstance(token_list, list):
                logger.warning("Birdeye returned non-list token data")
                return []
            return token_list[:3]
    except Exception as e:
        logger.warning(f"Error fetching tokens: {e}")
        return []

async def monitor_market():
    logger.info("Starting market monitor...")
    tokens = await fetch_tokens()
    for token in tokens:
        symbol = token.get("symbol", "UNKNOWN")
        name = token.get("name", "No name")
        address = token.get("address", "N/A")
        market_cap = token.get("mc", "N/A")
        text = f"🧪 Token Found: {symbol}\nName: {name}\nMarket Cap: {market_cap}\nAddress: {address}"
        await send_to_telegram(text)
    logger.info("Scan complete.")
