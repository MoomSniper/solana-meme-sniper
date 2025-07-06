# modules/alpha_scoring.py
import logging

def score_token(token):
    try:
        score = 0

        mc = float(token.get("fdv", 0))
        volume = float(token.get("volume_usd_1h", 0))
        holders = token.get("holder_count", 0)
        liq_locked = token.get("is_liquidity_locked", False)

        if 5000 <= volume <= 300000:
            score += 40
        if 20 <= holders <= 300:
            score += 30
        if liq_locked:
            score += 20
        if mc < 300000:
            score += 10

        return min(score, 100)
    except Exception as e:
        logging.warning(f"[Scoring Error] {e}")
        return 0

    async def get_coin_details(symbol: str):
    # ✅ MUST be indented under the function
    return {
        "symbol": symbol,
        "market_cap": 120_000,
        "volume_1h": 25_000,
        "buyers": 22,
        "score": 91.5
    }
