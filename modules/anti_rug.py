import logging

logger = logging.getLogger(__name__)

# === Rug Pull Detection ===
def check_rug_protection(token_data):
    try:
        has_locked_liquidity = token_data.get("liquidity_locked", False)
        blacklist_enabled = token_data.get("blacklist_enabled", False)
        max_tx_limit = token_data.get("max_tx_limit", 0)
        trading_paused = token_data.get("trading_paused", False)
        suspicious_functions = token_data.get("suspicious_functions", [])

        if trading_paused:
            logger.warning(f"🚨 Trading is paused for {token_data.get('symbol')}")
            return False

        if not has_locked_liquidity:
            logger.warning(f"🚨 {token_data.get('symbol')} has no locked liquidity")
            return False

        if blacklist_enabled:
            logger.warning(f"🚨 {token_data.get('symbol')} has a blacklist function")
            return False

        if max_tx_limit > 0 and max_tx_limit < 0.01:
            logger.warning(f"🚨 {token_data.get('symbol')} has a very low max TX limit")
            return False

        if suspicious_functions:
            logger.warning(f"🚨 {token_data.get('symbol')} contains suspicious contract functions: {suspicious_functions}")
            return False

        return True
    except Exception as e:
        logger.error(f"❌ Anti-rug scan failed: {e}")
        return False
