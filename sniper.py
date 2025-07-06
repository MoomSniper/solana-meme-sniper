import os
import httpx
import logging
import asyncio
from datetime import datetime
from typing import List

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
            data = response.json()
            if isinstance(data.get("data"), list):
                return data["data"]
            else:
                logger.warning("Birdeye returned non-list token data")
                return []
    except Exception as e:
        logger.warning(f"Error fetching tokens: {e}")
        return []

def format_token_message(token, score):
    name = token.get("name", "N/A")
    symbol = token.get("symbol", "N/A")
    address = token.get("address", "N/A")
    price = token.get("priceUsd", 0)
    volume = token.get("volume24hUsd", 0)
    holders = token.get("holders", 0)
    timestamp = datetime.now().strftime("%H:%M:%S")

    return (
        f"⚔️ *Alpha Alert | Phase 5*\n"
        f"🪙 *{name}* ({symbol})\n"
        f"💰 Price: ${price:.6f}\n"
        f"📈 Volume (24h): ${volume:,.0f}\n"
        f"👥 Holders: {holders}\n"
        f"🔗 Address: `{address}`\n"
        f"🔥 Alpha Score: {score}%\n"
        f"🕒 Time: {timestamp}\n"
        f"\n⚠️ Use sniper discretion. Not financial advice."
    )

def score_token(token) -> int:
    price = token.get("priceUsd", 0)
    volume = token.get("volume24hUsd", 0)
    holders = token.get("holders", 0)

    score = 0
    if 0.0001 < price < 1: score += 30
    if volume > 10000: score += 30
    if holders and holders > 50: score += 20
    if token.get("symbol") and len(token["symbol"]) <= 5: score += 10
    if token.get("name") and token["name"].lower().count("dog") + token["name"].lower().count("pepe") > 0: score += 5

    return min(score, 100)

async def monitor_market():
    logger.info("Starting market monitor...")
    tokens = await fetch_tokens()
    if not tokens:
        logger.warning("No tokens returned from Birdeye.")
        return

    for token in tokens:
        score = score_token(token)
        if score >= 85:
            msg = format_token_message(token, score)
            await send_telegram_message(msg)

    logger.info("Phase 5 scan complete.")
