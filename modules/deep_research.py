import asyncio
import logging
from modules.social_scraper import analyze_socials
from modules.contract_safety import analyze_contract
from modules.wallets import detect_smart_wallets
from modules.holder_analysis import analyze_holders

logger = logging.getLogger(__name__)

async def run_deep_research(coin_data):
    try:
        logger.info("🔬 Starting Deep Research Mode...")

        address = coin_data.get("address")
        symbol = coin_data.get("baseToken", {}).get("symbol", "???")

        # Run async scans in parallel
        contract_result, holders_result, smart_wallets, socials = await asyncio.gather(
            analyze_contract(address),
            analyze_holders(address),
            detect_smart_wallets(address),
            analyze_socials(address)
        )

        logger.info(f"🔐 Contract Safety: {contract_result}")
        logger.info(f"👤 Holder Breakdown: {holders_result}")
        logger.info(f"🐳 Smart Wallets In: {smart_wallets}")
        logger.info(f"📊 Social Analysis: {socials}")

        # Estimate projected multiplier and hype strength
        projected_multiplier = 3.0
        if smart_wallets >= 3 and socials['velocity_score'] > 0.75:
            projected_multiplier = 5.0
        if contract_result['rug_risk'] == "low" and holders_result['top_10_hold'] < 40:
            projected_multiplier += 2

        research_summary = {
            "contract_safety": contract_result,
            "holder_stats": holders_result,
            "smart_wallets": smart_wallets,
            "socials": socials,
            "projected_multiplier": projected_multiplier,
            "hype_score": socials["velocity_score"],
            "risk_rating": contract_result["rug_risk"]
        }

        logger.info(f"✅ Deep Research Complete: {symbol}")
        return research_summary

    except Exception as e:
        logger.error(f"❌ Deep Research failed: {e}")
        return None
