import os
import httpx
import logging
import asyncio
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
BIRDEYE_API = os.getenv("BIRDEYE_API")

logger = logging.getLogger("sniper")
logging.basicConfig(level=logging.INFO)

headers = {
    "X-API-KEY": BIRDEYE_API
}

async def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_ID, "text": text}
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, data=payload)
    except Exception as e:
        logger.warning(f"Telegram error: {e}")

async def fetch_tokens():
    url = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)
            if response.status_code == 429:
                logger.warning("⛔ Rate limit hit. Backing off.")
                return []
            data = response.json()
            return data.get("data", []) if isinstance(data.get("data"), list) else []
    except Exception as e:
        logger.warning(f"Error fetching tokens: {e}")
        return []

def format_token_message(token):
    name = token.get("name", "N/A")
    symbol = token.get("symbol", "N/A")
    address = token.get("address", "N/A")
    price = token.get("priceUsd", 0.0)
    volume = token.get("volume24hUsd", 0.0)
    holders = token.get("holders", "N/A")
    timestamp = datetime.now().strftime("%H:%M:%S")

    return (
        f"⚔️ *Oblivion Scout Alert*\n"
        f"🪙 Name: {name} ({symbol})\n"
        f"💰 Price: ${price:.6f}\n"
        f"📈 Volume (24h): ${volume:,.0f}\n"
        f"👥 Holders: {holders}\n"
        f"🔗 Address: `{address}`\n"
        f"🕒 Time: {timestamp}\n\n"
        f"⚠️ Early Market Watch — Not alpha-verified"
    )

async def monitor_market():
    logger.info("Starting market monitor...")
    tokens = await fetch_tokens()
    if not tokens:
        logger.warning("No tokens returned from Birdeye.")
        return

    for token in tokens[:2]:  # limit results to top 2 for safety
        msg = format_token_message(token)
        await send_telegram_message(msg)

    logger.info("Scan complete.")
