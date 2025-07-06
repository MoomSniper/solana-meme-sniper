import os
import httpx
import asyncio
import logging
from datetime import datetime
from telegram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

TELEGRAM_ID = os.getenv("TELEGRAM_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BIRDEYE_API = os.getenv("BIRDEYE_API")

bot = Bot(token=BOT_TOKEN)

API_URL = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"

HEADERS = {
    "accept": "application/json",
    "X-API-KEY": BIRDEYE_API
}

async def fetch_tokens():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(API_URL, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                tokens = data.get("data")
                if isinstance(tokens, list):
                    return tokens
                else:
                    logger.warning("Birdeye returned non-list token data")
                    return []
            elif response.status_code == 429:
                logger.warning("⛔ Rate limit hit. Backing off.")
                await asyncio.sleep(2)
                return []
            else:
                logger.warning(f"⚠️ Birdeye error: {response.status_code} - {response.text}")
                return []
    except Exception as e:
        logger.error(f"Birdeye fetch failed: {str(e)}")
        return []

async def deep_research_phase(token):
    # Placeholder for actual social & contract logic (Phase 4)
    logger.info(f"🔎 Deep scan started for {token.get('address')}")
    await asyncio.sleep(1)
    return {
        "social_score": 87,
        "risk": "low",
        "predicted_multiplier": "4-8x"
    }

async def process_batch(batch):
    for token in batch:
        logger.info(f"🧠 Evaluating {token.get('address')}")
        research = await deep_research_phase(token)
        if research['social_score'] > 85:
            message = (
                f"🚀 ALPHA ALERT 🚀\n"
                f"Token: {token.get('address')}\n"
                f"Score: {research['social_score']}\n"
                f"Risk: {research['risk']}\n"
                f"Target: {research['predicted_multiplier']}"
            )
            await bot.send_message(chat_id=TELEGRAM_ID, text=message)
        await asyncio.sleep(0.2)

async def monitor_market():
    logger.info("Starting market monitor...")
    while True:
        tokens = await fetch_tokens()
        if not tokens:
            logger.warning("No tokens returned from Birdeye.")
            await asyncio.sleep(10)
            continue

        batch_size = 25
        batches = [tokens[i:i + batch_size] for i in range(0, len(tokens), batch_size)]
        for batch in batches:
            await process_batch(batch)
            await asyncio.sleep(1.5)  # throttle to avoid API abuse

        await asyncio.sleep(10)  # main cycle sleep
