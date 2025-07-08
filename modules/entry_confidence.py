import random
import logging

from modules.wallet_tracker import get_smart_wallet_score
from modules.contract_check import check_contract_safety
from modules.social_scraper import get_social_score

logger = logging.getLogger(__name__)

# === Entry Confidence Engine ===
async def calculate_entry_confidence(token_info):
    try:
        token_name = token_info.get("name", "")
        token_symbol = token_info.get("symbol", "")
        address = token_info.get("address", "")
        market_cap = token_info.get("market_cap", 0)
        volume = token_info.get("volume", 0)

        # Contract safety check
        contract_result = await check_contract_safety(address)
        contract_score = 25 if contract_result.get("is_safe", False) else 0

        # Smart wallet tracking
        wallet_score = await get_smart_wallet_score(address)
        wallet_score = min(wallet_score, 25)

        # Social score
        social_result = await get_social_score(token_name, token_symbol)
        social_score = min(social_result.get("score", 0), 25)

        # Market/Volume weight (basic logic, expand later)
        mv_score = 0
        if 50_000 <= market_cap <= 300_000 and volume > 10_000:
            mv_score = 25
        elif 300_000 < market_cap <= 600_000 and volume > 25_000:
            mv_score = 15
        else:
            mv_score = 5

        # Total confidence
        confidence = contract_score + wallet_score + social_score + mv_score
        confidence = min(confidence, 100)
        return {
            "confidence": confidence,
            "breakdown": {
                "contract": contract_score,
                "wallets": wallet_score,
                "social": social_score,
                "market_volume": mv_score
            },
            "social_detail": social_result,
            "contract_detail": contract_result
        }

    except Exception as e:
        logger.error(f"❌ Entry confidence calculation failed: {e}")
        return {"confidence": 0, "breakdown": {}}
