import asyncio
import logging
import httpx
from datetime import datetime, time
from pytz import timezone

# Set timezone
eastern = timezone("US/Eastern")

# Configure logger
logger = logging.getLogger("sniper")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("INFO:sniper:%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Solana Tracker API key
SOLANA_TRACKER_API_KEY = "9a8e336e-9600-4aa3-ae05-ac91456ac055"
HEADERS = {
    "accept": "application/json",
    "x-api-key": SOLANA_TRACKER_API_KEY
}

# Limit request frequency
SCAN_INTERVAL = 44

# Solana rest window (Eastern Time)
REST_START = time(0, 0)  # 12 AM
REST_END = time(7, 0)    # 7 AM

def is_in_rest_hours():
    now = datetime.now(eastern).time()
    return REST_START <= now <= REST_END

async def fetch_new_token_mints(limit=5):
    url = f"https://public-api.solanatracker.io/tokens?sort=createdAt&order=desc&limit={limit}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=HEADERS)
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                logger.warning(f"[SolanaTracker] ❌ Token fetch failed: {response.status_code}")
                return []
    except Exception as e:
        logger.error(f"[SolanaTracker] ⚠️ Exception during token fetch: {e}")
        return []

async def fetch_token_details(token_address):
    url = f"https://public-api.solanatracker.io/token/{token_address}"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=HEADERS)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"[SolanaTracker] ❌ Token fetch failed: {response.status_code}")
                return None
    except Exception as e:
        logger.error(f"[SolanaTracker] ⚠️ Error fetching token details: {e}")
        return None

def is_alpha_worthy(token_data):
    try:
        if not token_data:
            return False
        market_cap = token_data.get("marketCap", 0)
        holders = token_data.get("holders", 0)
        volume = token_data.get("volume", 0)

        # Godest Mode filters
        return (
            market_cap < 300_000 and
            volume > 5_000 and
            holders > 50
        )
    except Exception as e:
        logger.error(f"[Scoring Error] ⚠️ Failed to score token: {e}")
        return False

async def scan_and_score_market():
    while True:
        if is_in_rest_hours():
            logger.info("😴 Sleeping during rest hours (12AM–7AM EST)...")
            await asyncio.sleep(SCAN_INTERVAL)
            continue

        logger.info("🔍 Starting scan...")

        token_list = await fetch_new_token_mints(limit=10)

        for token in token_list:
            address = token.get("address")
            if not address:
                continue

            logger.info(f"🔎 Evaluating token: {address}")
            token_data = await fetch_token_details(address)

            if is_alpha_worthy(token_data):
                logger.info(f"🚀 Alpha Detected: {address}")
                # Future: send to Telegram
            else:
                logger.info(f"⛔ Not alpha: {address}")

        await asyncio.sleep(SCAN_INTERVAL)
