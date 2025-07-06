import logging
import aiohttp
from modules.alpha_scoring import score_token

logger = logging.getLogger("sniper")

BIRDEYE_API_KEY = "8ecb4290bb4d485aae3b9a89b116eeb3"
BIRDEYE_URL = "https://public-api.birdeye.so/public/tokenlist?sort_by=volume_1h&sort_type=desc&limit=50"

async def fetch_tokens():
    headers = {"X-API-KEY": BIRDEYE_API_KEY}
    async with aiohttp.ClientSession() as session:
        async with session.get(BIRDEYE_URL, headers=headers) as response:
            if response.status != 200:
                logger.error(f"[Fetch Error] Birdeye API status: {response.status}")
                return []
            data = await response.json()
            return data.get("data", [])

async def scan_and_score_market():
    try:
        tokens = await fetch_tokens()
        for token in tokens:
            mint = token.get("address")
            symbol = (token.get("symbol") or "").encode("utf-8").decode("utf-8")

            if not mint or not symbol:
                continue

            logger.info(f"ð¡ Scanning {symbol} ({mint})")
            score = await score_token(symbol, mint)

            if score and score.get("alpha_score", 0) >= 85:
                logger.info(f"ð¨ Alpha found: {symbol} | Score: {score['alpha_score']}")
                return {
                    "symbol": symbol,
                    "mint": mint,
                    **score
                }

    except Exception as e:
        logger.error(f"[Scan Error] {e}")
    return None

