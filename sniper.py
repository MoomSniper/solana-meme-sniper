import asyncio
import httpx
import logging
from datetime import datetime
import pytz

logger = logging.getLogger("sniper")
logging.basicConfig(level=logging.INFO)

# Obsidian Mode Parameters
SCAN_INTERVAL = 40  # in seconds
MIN_HOUR = 7  # 7 AM
MAX_HOUR = 23  # 11 PM
TIMEZONE = "America/Toronto"

def is_within_active_hours():
    current_time = datetime.now(pytz.timezone(TIMEZONE))
    return MIN_HOUR <= current_time.hour < MAX_HOUR

async def fetch_recent_tokens():
    url = "https://public-api.solanatracker.io/tokens?sort=createdAt&order=desc&limit=25&offset=0"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
    except Exception as e:
        logger.warning(f"[SolanaTracker] Token list fetch failed: {e}")
        return []

async def fetch_token_details(mint):
    url = f"https://public-api.solanatracker.io/token/{mint}"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json().get("data", {})
            else:
                logger.warning(f"[SolanaTracker] Token fetch failed: {response.status_code}")
                return None
    except Exception as e:
        logger.warning(f"[SolanaTracker] Token fetch exception: {e}")
        return None

async def scan_token(mint):
    logger.info(f"ð Scanning token: {mint}")
    token_data = await fetch_token_details(mint)
    if not token_data:
        logger.warning(f"â ï¸ No data returned for {mint}")
        return
    # Alpha detection placeholder
    if token_data.get("holders", 0) > 15 and token_data.get("volume", 0) > 5000:
        logger.info(f"ð ALPHA FOUND: {mint} | Volume: {token_data.get('volume')} | Holders: {token_data.get('holders')}")
        # Telegram alert logic would go here
    else:
        logger.info(f"ð¸ Not alpha: {mint}")

async def scan_and_score_market():
    while True:
        if is_within_active_hours():
            tokens = await fetch_recent_tokens()
            for token in tokens:
                mint = token.get("mintAddress")
                if mint:
                    await scan_token(mint)
                await asyncio.sleep(2)  # Space out calls to avoid API burn
        else:
            logger.info("ð Outside of scan hours (12AM - 7AM). Sleeping...")
        await asyncio.sleep(SCAN_INTERVAL)
