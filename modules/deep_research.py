import asyncio
import logging
from modules.social_scraper import fetch_social_stats
from modules.sol_tracker import get_coin_details

logger = logging.getLogger("deep_research")

async def run_deep_research(symbol, mint):
    try:
        logger.info(f"🧠 Deep research started for {symbol} ({mint})")

        # Fetch contract + liquidity info from Solana Tracker
        coin_data = await get_coin_details(mint)

        if not coin_data:
            logger.warning("❌ Solana Tracker returned nothing.")
            return "Could not fetch data from Solana Tracker."

        # Fetch social hype
        social = await fetch_social_stats(symbol)

        # Intelligence scoring logic
        hype_score = social['hype_score']
        bot_ratio = social['bot_ratio']
        liquidity_locked = coin_data.get("liquidity_locked", False)
        holders = coin_data.get("holders", 0)

        if not liquidity_locked or bot_ratio > 0.25 or holders < 50:
            return f"🚪 <b>EXIT NOW</b>\nToo risky.\n• Locked LP: {liquidity_locked}\n• Bot %: {round(bot_ratio*100)}%\n• Holders: {holders}"

        if hype_score > 85 and holders >= 150:
            return f"✅ <b>HOLD</b>\n• Hype Score: {hype_score}\n• Bot %: {round(bot_ratio*100)}%\n• LP Locked: {liquidity_locked}\n• Holders: {holders}"

        return f"🟡 <b>PARTIAL TAKE PROFIT</b>\n• Hype Score: {hype_score}\n• Bot %: {round(bot_ratio*100)}%\n• Holders: {holders}"

    except Exception as e:
        logger.error(f"[Deep Research Error] {e}")
        return "❌ Error during deep research."
