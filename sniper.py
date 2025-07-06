import os
import asyncio
import logging
import httpx
from modules.alpha_scoring import score_token
from modules.telegram_engine import send_alert
from modules.deep_research import run_deep_research

logger = logging.getLogger("sniper")
logging.basicConfig(level=logging.INFO)

SOLANA_TRACKER_URL = "https://public-api.solanatracker.io/token/"
MIN_SCORE = 85
SCAN_INTERVAL = 2  # seconds

async def fetch_token_data(mint: str):
    try:
        url = f"{SOLANA_TRACKER_URL}{mint}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.debug(f"[Tracker] Token not found: {mint}")
            else:
                logger.warning(f"[Tracker] Error {response.status_code} for token {mint}")
    except Exception as e:
        logger.error(f"[Tracker Fetch Error] {e}")
    return None

async def scan_and_score_market():
    while True:
        try:
            logger.info("🧠 Obsidian Scan Starting...")

            # Get tokens from env or fallback to an example list
            token_list = os.getenv("TOKENS_TO_SCAN", "So11111111111111111111111111111111111111112").split(",")
            for mint in token_list:
                mint = mint.strip()
                if not mint or mint.startswith("So111111"):
                    continue

                logger.info(f"🔍 Scanning token: {mint}")
                token_data = await fetch_token_data(mint)
                if not token_data:
                    logger.warning(f"⚠️ No data returned for {mint}")
                    continue

                score = score_token(token_data)
                logger.info(f"📊 {mint} scored {score}")

                if score >= MIN_SCORE:
                    alert_text = f"🚀 <b>ALPHA SPOTTED</b>\nToken: {mint}\nScore: {score}"
                    await send_alert(alert_text)

                    # Queue deep dive research 90s later
                    asyncio.create_task(deep_dive(mint))

            await asyncio.sleep(SCAN_INTERVAL)

        except Exception as e:
            logger.error(f"[Scan Error] {e}")
            await asyncio.sleep(SCAN_INTERVAL)

async def deep_dive(mint):
    await asyncio.sleep(90)
    result = await run_deep_research(symbol=mint, mint=mint)
    await send_alert(result)
