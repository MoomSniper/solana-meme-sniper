import os
import asyncio
import aiohttp
import logging
from datetime import datetime
from pytz import timezone

logger = logging.getLogger("sniper")
logging.basicConfig(level=logging.INFO)

TELEGRAM_ID = os.getenv("TELEGRAM_ID")

# Scanning config
SCAN_INTERVAL = 45  # seconds between scans
SLEEP_HOURS = range(0, 7)  # Do not scan from 12am–7am EST

async def fetch_token_data(session, token_address):
    url = f"https://public-api.solanatracker.io/token/{token_address}"
    try:
        async with session.get(url, timeout=5) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 404:
                logger.warning("[SolanaTracker] Token not found: 404")
            else:
                logger.error(f"[SolanaTracker] Failed: HTTP {response.status}")
    except Exception as e:
        logger.error(f"[SolanaTracker] Error fetching token {token_address}: {e}")
    return None

def is_sleep_time():
    now = datetime.now(timezone("US/Eastern"))
    return now.hour in SLEEP_HOURS

def score_coin(data):
    try:
        score = 0
        holders = data.get("holders", 0)
        liquidity = data.get("liquidity", {}).get("usd", 0)
        mc = data.get("market_cap", {}).get("usd", 0)

        if holders >= 100:
            score += 30
        if liquidity > 5000:
            score += 30
        if mc and mc < 300000:
            score += 40

        return min(score, 100)
    except Exception as e:
        logger.error(f"[Scoring Error] {e}")
        return 0

async def scan_and_score_market():
    while True:
        if is_sleep_time():
            logger.info("⏸ Sleeping hours. Pausing scans.")
            await asyncio.sleep(60 * 10)
            continue

        try:
            async with aiohttp.ClientSession() as session:
                test_token = "So11111111111111111111111111111111111111112"
                logger.info(f"🔍 Scanning token: {test_token}")
                data = await fetch_token_data(session, test_token)
                if data:
                    score = score_coin(data)
                    logger.info(f"✅ Score: {score}")
                else:
                    logger.warning("⚠️ No data returned.")
        except Exception as e:
            logger.error(f"[Scan Error] {e}")

        await asyncio.sleep(SCAN_INTERVAL)
