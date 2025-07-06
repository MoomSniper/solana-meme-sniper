import os
import asyncio
import httpx
import logging
from datetime import datetime

BIRDEYE_API_KEY = os.getenv("BIRDEYE_API")

async def get_token_list():
    url = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
    headers = {
        "X-API-KEY": BIRDEYE_API_KEY,
        "accept": "application/json"
    }

    try:
        response = httpx.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data.get("data"), list):
                logging.info(f"✅ Token list received: {len(data['data'])} tokens")
                return data["data"]
            else:
                logging.warning("❌ Birdeye returned non-list token data")
                return []
        else:
            logging.warning(f"❌ Birdeye API error {response.status_code}: {response.text}")
            return []
    except Exception as e:
        logging.error(f"❌ Exception during token list fetch: {e}")
        return []

async def monitor_market():
    logging.info("🚀 Starting market monitor...")

    while True:
        token_list = await get_token_list()

        # TEMPORARY: Just print token count. Replace with sniper logic.
        if token_list:
            logging.info(f"📊 Monitoring {len(token_list)} tokens at {datetime.now().strftime('%H:%M:%S')}")

        await asyncio.sleep(10)
