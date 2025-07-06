# modules/solana_tracker.py
import os
import requests
import logging

SOL_TRACKER_API = os.getenv("SOL_TRACKER_API")  # Your API key

BASE_URL = "https://api.solanatracker.io/v1/tokens"

def get_live_pairs():
    try:
        headers = {"Authorization": f"Bearer {SOL_TRACKER_API}"}
        params = {
            "sort": "created_at_desc",
            "limit": 50,
            "chain": "solana",
            "is_token": True
        }
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        tokens = response.json().get("tokens", [])
        return tokens
    except Exception as e:
        logging.error(f"[Solana Tracker Error] {e}")
        return []

def filter_alpha_candidates(tokens):
    alpha_tokens = []
    for token in tokens:
        try:
            mc = token.get("fdv", 0)
            volume = token.get("volume_usd_1h", 0)
            holders = token.get("holder_count", 0)
            liq_locked = token.get("is_liquidity_locked", False)

            if (
                5000 <= volume <= 300000 and
                20 <= holders <= 300 and
                liq_locked and
                mc and mc < 300000
            ):
                alpha_tokens.append(token)
        except Exception as e:
            logging.warning(f"[Token Filter Fail] {e}")
            continue

    return alpha_tokens
