import logging
from modules.social_scraper import fetch_social_stats
from modules.alpha_scoring import get_coin_details

logger = logging.getLogger(__name__)

async def run_deep_research(symbol, mint):
    try:
        logger.info(f"🔬 Deep research initiated for {symbol} ({mint})")

        # Pull contract + liquidity data from Solana Tracker
        coin_data = await get_coin_details(mint)
        if not coin_data:
            logger.warning(f"❌ Solana Tracker returned no data for {symbol}")
            return "Could not fetch coin details."

        # Pull Telegram + Twitter data
        social = await fetch_social_stats(symbol)
        if not social:
            logger.warning(f"⚠️ No social data returned for {symbol}")
            return "Social data unavailable."

        # Assign intelligence layers
        hype_score = social.get('hype_score', 0)
        bot_ratio = social.get('bot_ratio', 1)
        liquidity_locked = coin_data.get("liquidity_locked", False)
        holders = coin_data.get("holders", 0)

        # Trigger exit if any fatal flaws
        if not liquidity_locked or bot_ratio > 0.3 or holders < 50:
            return (
                f"<b>🚨 EXIT NOW — Too risky</b>\n"
                f"🔐 LP Locked: {liquidity_locked}\n"
                f"🤖 Bot %: {round(bot_ratio*100)}%\n"
                f"👥 Holders: {holders}"
            )

        # HOLD zone
        if hype_score >= 85 and holders >= 150:
            return (
                f"<b>✅ HOLD</b>\n"
                f"🔥 Hype Score: {hype_score}\n"
                f"🤖 Bot %: {round(bot_ratio*100)}%\n"
                f"🔐 LP Locked: {liquidity_locked}\n"
                f"👥 Holders: {holders}"
            )

        # TAKE PROFIT zone
        return (
            f"<b>⚠️ PARTIAL TAKE PROFIT</b>\n"
            f"📈 Hype Score: {hype_score}\n"
            f"🤖 Bot %: {round(bot_ratio*100)}%\n"
            f"🔐 LP Locked: {liquidity_locked}\n"
            f"👥 Holders: {holders}"
        )

    except Exception as e:
        logger.error(f"[Deep Research Error] {e}")
        return "Deep research failed. Check logs."
