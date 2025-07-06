import os
import httpx
import logging

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
