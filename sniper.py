
import os
import asyncio
import httpx
import logging
import random

TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

async def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": TELEGRAM_ID, "text": text})

async def fetch_token_list():
    url = "https://public-api.birdeye.so/defi/tokenlist?limit=100&offset=0"
    headers = {"X-API-KEY": os.getenv("BIRDEYE_API")}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            logging.warning("Invalid response from Birdeye.")
            return []
        return response.json().get("data", [])

async def monitor_market():
    while True:
        logging.info("🧠 Sniper loop: scanning live token list...")

        try:
            tokens = await fetch_token_list()
            logging.info(f"📊 Fetched {len(tokens)} tokens from Birdeye.")
        except Exception as e:
            await send_telegram_message(f"❌ Error fetching token list: {e}")
            await asyncio.sleep(30)
            continue

        if not tokens:
            await send_telegram_message("⚠️ No tokens found or Birdeye limit hit.")
        else:
            for token in tokens:
                msg = f"""
📡 LIVE TOKEN FOUND
Name: {token.get('name', 'N/A')}
Symbol: {token.get('symbol', 'N/A')}
Chart: https://birdeye.so/token/{token.get('address')}
"""
                await send_telegram_message(msg)

        await asyncio.sleep(random.randint(20, 30))
