import logging

logger = logging.getLogger(__name__)

# === Long-Term Trust Protocol ===
def check_trust_promotion(token_data):
    try:
        multiplier = token_data.get("current_multiplier", 1)
        age_minutes = token_data.get("age_minutes", 0)
        locked_liquidity = token_data.get("liquidity_locked", False)
        active_community = token_data.get("community_active", False)
        contract_safe = token_data.get("contract_safe", False)

        if (
            multiplier >= 5
            and age_minutes > 120
            and locked_liquidity
            and active_community
            and contract_safe
        ):
            logger.info(f"🟢 Token {token_data.get('symbol')} promoted to long-term watchlist")
            return True

        return False
    except Exception as e:
        logger.error(f"❌ Trust protocol check failed: {e}")
        return False
