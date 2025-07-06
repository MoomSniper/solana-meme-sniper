import os
import httpx
import logging

SOLANA_TRACKER_API = "https://public-api.solanatracker.io/token"
HEADERS = {"accept": "application/json"}

async def fetch_token_data(mint: str):
    try:
        url = f"{SOLANA_TRACKER_API}/{mint}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=HEADERS)
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"[SOLANA TRACKER] ❌ Error fetching token {mint}: {response.status_code}")
                return None
    except Exception as e:
        logging.error(f"[SOLANA TRACKER] ❌ Exception: {e}")
        return None
