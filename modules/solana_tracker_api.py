import httpx
import os
import logging

SOLANA_TRACKER_API = os.getenv("SOLANA_TRACKER_API")
BASE_URL = "https://public-api.solanatracker.io/tokens"

headers = {
    "accept": "application/json",
    "authorization": f"Bearer {SOLANA_TRACKER_API}"
}

async def fetch_token_data(limit=50):
    try:
        url = f"{BASE_URL}?sort=createdAt&order=desc&limit={limit}&offset=0"
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            tokens = response.json().get("data", [])
            result = []
            for token in tokens:
                result.append({
                    "name": token.get("name"),
                    "symbol": token.get("symbol"),
                    "address": token.get("address"),
                    "market_cap": token.get("marketCap", 0),
                    "volume": token.get("volume24h", 0),
                    "holders": token.get("holders", 0),
                    "created_at": token.get("createdAt"),
                    "liquidity_locked": token.get("liquidityLocked", False),
                    "slug": token.get("slug")
                })
            logging.info(f"[SOLANA TRACKER] ✅ Fetched {len(result)} tokens")
            return result
    except Exception as e:
        logging.error(f"[SOLANA TRACKER] ❌ Error fetching tokens: {e}")
        return []
