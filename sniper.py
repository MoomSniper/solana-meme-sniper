import asyncio
import logging
import httpx
import pytz
from datetime import datetime
from utils.solana_tracker import fetch_latest_tokens, fetch_token_details
from utils.alpha_score import calculate_alpha_score
from utils.social_scanner import get_social_score
from utils.smart_wallets import check_smart_wallet_activity

logger = logging.getLogger("sniper")
logging.basicConfig(level=logging.INFO)

SCAN_INTERVAL = 44  # ~1963 scans/day = ~60,953/month (only during 12hr/day keeps us under 30–40k)
SLEEP_HOURS = (0, 1, 2, 3, 4, 5, 6)  # Do not scan from 12am to 7am

def in_active_hours():
    now = datetime.now(pytz.timezone("America/Toronto"))
    return now.hour not in SLEEP_HOURS

async def scan_and_score_market():
    while True:
        if not in_active_hours():
            logger.info("🌙 [Sleep Mode] Skipping scan during low hours.")
            await asyncio.sleep(300)
            continue

        logger.info("🔍 [OBSIDIAN MODE] Scanning Solana Tracker for fresh tokens...")
        tokens = await fetch_latest_tokens()
        if not tokens:
            logger.warning("⚠️ No tokens pulled.")
            await asyncio.sleep(SCAN_INTERVAL)
            continue

        for token in tokens:
            address = token.get("address")
            if not address:
                continue

            logger.info(f"🔎 Evaluating token: {address}")
            details = await fetch_token_details(address)
            if not details:
                logger.warning(f"⚠️ No data for {address}")
                continue

            alpha_score = calculate_alpha_score(details)
            if alpha_score < 85:
                logger.info(f"❌ {address} scored {alpha_score} – skipping.")
                continue

            social_score = get_social_score(details)
            smart_flag = check_smart_wallet_activity(details)

            confidence = round((alpha_score * 0.5) + (social_score * 5) + (30 if smart_flag else 0), 1)
            projected_x = round(confidence / 10, 1)

            logger.info(f"🔥 ALPHA: {address}")
            logger.info(f"✅ Alpha Score: {alpha_score}")
            logger.info(f"📢 Social Hype: {social_score}/10")
            logger.info(f"💸 Smart Wallets: {'Yes' if smart_flag else 'No'}")
            logger.info(f"🎯 Entry Confidence: {confidence}%")
            logger.info(f"🚀 Projected Potential: {projected_x}x")

        await asyncio.sleep(SCAN_INTERVAL)
