# sniper.py
import asyncio
import aiohttp
import logging
from datetime import datetime
from modules.alpha_scoring import score_token

logger = logging.getLogger("sniper")

SOLANA_TRACKER_BASE_URL = "https://public-api.solanatracker.io"

async def fetch_new_tokens(session):
    try:
        url = f"{SOLANA_TRACKER_BASE_URL}/tokens?sort=createdAt&order=desc&limit=10&offset=0"
        async with session.get(url, timeout=10) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("data", [])
            else:
                logger.warning(f"[SolanaTracker] Token fetch failed: {resp.status}")
    except Exception as e:
        logger.error(f"[SolanaTracker] ❌ Error fetching tokens: {e}")
    return []

async def fetch_token_metadata(session, mint):
    try:
        url = f"{SOLANA_TRACKER_BASE_URL}/token/{mint}"
        async with session.get(url, timeout=10) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return None
    except Exception as e:
        logger.warning(f"[Metadata Error] {e}")
    return None

async def scan_and_score_market():
    while True:
        now = datetime.utcnow()
        if 7 <= now.hour < 24:  # Run between 7am–11:59pm UTC
            try:
                async with aiohttp.ClientSession() as session:
                    tokens = await fetch_new_tokens(session)
                    for token in tokens:
                        mint = token.get("mint")
                        if not mint:
                            continue

                        logger.info(f"🔍 Scanning token: {mint}")
                        token_meta = await fetch_token_metadata(session, mint)
                        if not token_meta:
                            logger.warning(f"⚠️ No data returned for {mint}")
                            continue

                        score = await score_token(mint, token_meta)
                        if score:
                            logger.info(f"🧠 Alpha Score for {mint}: {score}")
                        await asyncio.sleep(2)  # Short delay between token scoring
            except Exception as e:
                logger.error(f"[Scan Error] {e}")
        else:
            logger.info("⏸ Sleeping hours — scanning paused (12am–7am UTC)")

        await asyncio.sleep(40)  # Delay between fetch cycles
