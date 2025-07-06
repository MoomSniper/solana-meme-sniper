# modules/solana_tracker.py

import httpx
import logging
import os

SOLANA_TRACKER_API_KEY = os.getenv("SOLANA_TRACKER_API")
BASE_URL = "https://public-api.solanatracker.io"

HEADERS = {
    "accept": "application/json",
    "x-api-key": SOLANA_TRACKER_API_KEY
}

def fetch_token_data(token_address):
    try:
        url = f"{BASE_URL}/token/{token_address}"
        response = httpx.get(url, headers=HEADERS)
        if response.status_code == 200:
            logging.info(f"[SolanaTracker] ✅ Fetched token data for {token_address}")
            return response.json()
        else:
            logging.warning(f"[SolanaTracker] ❌ Token fetch failed: {response.status_code}")
            return None
    except Exception as e:
        logging.error(f"[SolanaTracker] ❌ Exception: {e}")
        return None
