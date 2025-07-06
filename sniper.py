import httpx
import logging
import asyncio

BIRDEYE_API_KEY = "5d395eeeae754e048cd34ed07a72e2e1"

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
            print("🔍 Raw Birdeye response:", data)  # LOG STRUCTURE
            token_data = data.get("data")

            if isinstance(token_data, list):
                logging.info(f"✅ Token list received: {len(token_data)} tokens")
                return token_data
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
    while True:
        tokens = await get_token_list()
        logging.info(f"📊 Monitoring {len(tokens)} tokens...")
        # Placeholder — future logic goes here
        await asyncio.sleep(10)
