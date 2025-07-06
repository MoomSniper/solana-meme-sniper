import os
import aiohttp
import logging
from typing import Optional, Dict
from modules.solana_tracker_api import fetch_token_data
from modules.alpha_scoring import score_token

logger = logging.getLogger("sniper")

# --- Constants ---
MIN_SCORE_THRESHOLD = 85  # Minimum alpha score to trigger alert
MINT_LIST = [
    "So11111111111111111111111111111111111111112",  # Replace with live feed or dynamic list later
]


async def scan_and_score_market() -> Optional[Dict]:
    try:
        async with aiohttp.ClientSession() as session:
            for mint in MINT_LIST:
                logger.info(f"🔍 Scanning token: {mint}")
                
                token_data = await fetch_token_data(mint)
                if not token_data:
                    logger.warning(f"⚠️ No data returned for {mint}")
                    continue

                score = await score_token(token_data)
                alpha_score = score.get("alpha_score", 0)

                if alpha_score >= MIN_SCORE_THRESHOLD:
                    logger.info(f"🚀 ALPHA FOUND: {token_data.get('symbol', 'Unknown')} | Score: {alpha_score}")
                    return {**token_data, **score}
                else:
                    logger.info(f"❌ Low score for {token_data.get('symbol', 'Unknown')}: {alpha_score}")
    except Exception as e:
        logger.error(f"[Scan Error] {e}")

    return None
