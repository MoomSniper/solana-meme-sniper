import random
import logging

logger = logging.getLogger("obsidian")

async def score_token(token_data):
    try:
        # Basic mock scoring logic — replace with your own logic as needed
        market_cap = token_data.get("market_cap", 0)
        volume = token_data.get("volume_1h", 0)
        buyers = token_data.get("buyers", 0)

        score = 0
        if market_cap < 300_000:
            score += 30
        if volume > 5_000:
            score += 30
        if buyers >= 15:
            score += 30

        # Add small randomness for tie-breakers
        score += random.uniform(0, 10)

        logger.info(f"[SCORING] {token_data.get('symbol')} scored {score:.2f}")
        return score

    except Exception as e:
        logger.error(f"[SCORING ERROR] Failed to score token: {e}")
        return 0

async def get_coin_details(symbol: str):
    return {
        "symbol": symbol,
        "market_cap": 120_000,
        "volume_1h": 25_000,
        "buyers": 22,
        "score": 91.5
    }
