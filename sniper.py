import asyncio
import logging
from datetime import datetime
from pytz import timezone
import httpx

# --- Configuration ---
SOLANA_TRACKER_API = "https://public-api.solanatracker.io/token/"
ACTIVE_HOURS_START = 7   # 7 AM EST
ACTIVE_HOURS_END = 24    # 12 AM EST
SCAN_INTERVAL_SECONDS = 44
MIN_VOLUME = 3000
MIN_BUYERS = 15
MIN_MCAP = 20000

# --- Logging ---
logger = logging.getLogger("sniper")
logging.basicConfig(level=logging.INFO)

# --- Utility: Time Control ---
def within_active_hours():
    now = datetime.now(timezone("US/Eastern"))
    return ACTIVE_HOURS_START <= now.hour < ACTIVE_HOURS_END

# --- Utility: Fetch Token Info ---
async def get_token_data(token_address):
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(f"{SOLANA_TRACKER_API}{token_address}")
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"[SolanaTracker] Token fetch failed: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"[SolanaTracker] Exception: {str(e)}")
            return None

# --- Sniper Logic ---
async def scan_and_score_market():
    scanned_mints = set()

    while True:
        if not within_active_hours():
            await asyncio.sleep(300)  # sleep 5 mins outside active hours
            continue

        logger.info("🔍 Starting scan...")

        tokens_to_check = get_recent_tokens()  # Replace with real source

        for token in tokens_to_check:
            token_address = token["address"]

            if token_address in scanned_mints:
                continue

            if (token.get("volume_1h_usd", 0) < MIN_VOLUME or
                token.get("txns_1h", {}).get("buys", 0) < MIN_BUYERS or
                token.get("fdv", 0) < MIN_MCAP):
                continue

            coin_data = await get_token_data(token_address)
            if not coin_data:
                continue

            logger.info(f"✅ Token {token_address} passed filters")

            scanned_mints.add(token_address)

        await asyncio.sleep(SCAN_INTERVAL_SECONDS)

# --- Placeholder ---
def get_recent_tokens():
    # TEMP MOCK – replace this with actual token source (DexScreener, etc.)
    return [{
        "address": "So11111111111111111111111111111111111111112",
        "volume_1h_usd": 5000,
        "txns_1h": {"buys": 20},
        "fdv": 25000
    }]
