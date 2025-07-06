import os
import asyncio
import httpx
import logging

logger = logging.getLogger("sniper")
logging.basicConfig(level=logging.INFO)

TELEGRAM_ID = os.getenv("TELEGRAM_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")

async def send_telegram_message(message: str):
    if not TELEGRAM_ID or not BOT_TOKEN:
        logger.warning("Missing TELEGRAM_ID or BOT_TOKEN")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_ID, "text": message}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

async def monitor_market():
    logger.info("Starting market monitor...")
    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get("https://public-api.birdeye.so/defi/tokenlist?chain=solana")
                data = response.json()

                # Check and extract tokens from a wrapped response
                tokens = data.get("tokens", []) if isinstance(data, dict) else data

                if not isinstance(tokens, list):
                    logger.warning(f"Unexpected tokenlist structure: {data}")
                    await asyncio.sleep(10)
                    continue

                # Proceed with filtered token logic (placeholder)
                logger.info(f"Token list received: {len(tokens)} tokens")

            except Exception as e:
                logger.error(f"Error in monitor_market: {e}")

            await asyncio.sleep(10)
