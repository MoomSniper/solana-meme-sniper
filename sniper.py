import os
import httpx
import asyncio
import logging

# Setup
logging.basicConfig(level=logging.INFO)
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BIRDEYE_API = os.getenv("BIRDEYE_API")
headers = {"X-API-KEY": BIRDEYE_API}

# Fetch token list from Birdeye
async def fetch_token_list():
    url = "https://public-api.birdeye.so/defi/tokenlist?limit=50&offset=0"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        data = response.json()
        return data.get("data", {}).get("tokens", [])

# Monitor and send dummy calls every 60 seconds
async def monitor_market(bot):
    while True:
        logging.info("🧠 Sniper loop: scanning live token list...")

        try:
            tokens = await fetch_token_list()
            logging.info(f"📊 Fetched {len(tokens)} tokens from Birdeye.")
        except Exception as e:
            await bot.send_message(chat_id=TELEGRAM_ID, text=f"❌ Error fetching token list: {e}")
            logging.error(f"Error fetching token list: {e}")
            await asyncio.sleep(60)
            continue

        if not tokens:
            await bot.send_message(chat_id=TELEGRAM_ID, text="⚠️ No tokens found.")
        else:
            for token in tokens:
                try:
                    msg = f"""
📡 LIVE TOKEN FOUND
Name: {token.get('name', 'N/A')}
Symbol: {token.get('symbol', 'N/A')}
Chart: https://birdeye.so/token/{token.get('address')}
"""
                    await bot.send_message(chat_id=TELEGRAM_ID, text=msg)
                    await asyncio.sleep(0.5)  # prevent Telegram flood
                except Exception as e:
                    logging.error(f"Error sending token msg: {e}")

        await asyncio.sleep(60)  # wait before scanning again
