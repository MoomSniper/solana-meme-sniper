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
    payload = {"chat_id": TELEGRAM_ID, "text": text, "parse_mode": "Markdown"}
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
            logger.info(f"🔍 Birdeye raw response: {data}")

            tokens = data.get("data")
            if isinstance(tokens, list):
                return tokens
            elif isinstance(tokens, dict) and "tokens" in tokens:
                return tokens["tokens"]
            else:
                logger.warning("⚠️ Unexpected Birdeye format. No token list found.")
                return []
    except Exception as e:
        logger.warning(f"Error fetching tokens: {e}")
        return []

def format_token_message(token):
    name = token.get("name", "N/A")
    symbol = token.get("symbol", "N/A")
    address = token.get("address", "N/A")
    price = token.get("priceUsd", 0)
    volume = token.get("volume24hUsd", 0)
    holders = token.get("holders", "N/A")
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Phase 4 Spam Filter — Send only if real alpha (volume check)
    if volume is None or volume < 10000:
        return None

    return (
        f"⚔️ *Oblivion Alpha Alert*\n"
        f"🪙 Name: {name} ({symbol})\n"
        f"💰 Price: ${price:.6f}\n"
        f"📈 Volume (24h): ${volume:,.0f}\n"
        f"👥 Holders: {holders}\n"
        f"🔗 Address: `{address}`\n"
        f"🕒 Time: {timestamp}\n\n"
        f"🔥 Potential alpha candidate — track manually."
    )

async def monitor_market():
    logger.info("Starting market monitor...")
    tokens = await fetch_tokens()
    if not tokens:
        logger.warning("No tokens returned from Birdeye.")
        return

    alerts_sent = 0
    for token in tokens[:15]:  # Expand to top 15 for Phase 4 filtering
        msg = format_token_message(token)
        if msg:
            await send_telegram_message(msg)
            alerts_sent += 1

    logger.info(f"Market scan complete. {alerts_sent} alerts sent.")
