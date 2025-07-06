import os
import httpx
import asyncio
import logging
from datetime import datetime, timedelta

# Logger setup
logger = logging.getLogger("sniper")
logger.setLevel(logging.INFO)

BIRDEYE_API_KEY = os.getenv("BIRDEYE_API")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))

# New working endpoint
API_URL = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
HEADERS = {"X-API-KEY": BIRDEYE_API_KEY}

# Minimum alpha score threshold
ALPHA_SCORE_THRESHOLD = 85

# Store processed tokens to avoid spam
processed_tokens = {}

async def fetch_token_data():
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(API_URL, headers=HEADERS)
            response.raise_for_status()
            return response.json().get("data", [])
    except Exception as e:
        logger.warning(f"Birdeye fetch failed: {e}")
        return []

def calculate_alpha_score(token):
    try:
        mc = float(token.get("market_cap", 0))
        volume = float(token.get("volume_1h_usd", 0))
        buyers = int(token.get("tx_count_1h", 0))

        if mc <= 0 or volume <= 0:
            return 0

        score = 0
        if mc < 300000: score += 30
        if volume > 5000: score += 30
        if buyers > 15: score += 20
        if token.get("symbol") and len(token["symbol"]) <= 5: score += 10

        return score
    except:
        return 0

async def monitor_market(bot):
    while True:
        tokens = await fetch_token_data()
        now = datetime.utcnow()

        for token in tokens:
            address = token.get("address")
            if not address or address in processed_tokens:
                continue

            score = calculate_alpha_score(token)
            if score >= ALPHA_SCORE_THRESHOLD:
                symbol = token.get("symbol", "N/A")
                mc = token.get("market_cap", "N/A")
                vol = token.get("volume_1h_usd", "N/A")
                buyers = token.get("tx_count_1h", "N/A")

                msg = (
                    "<b>Alpha Detected</b>\n"
                    f"<b>Symbol:</b> {symbol}\n"
                    f"<b>Market Cap:</b> ${mc}\n"
                    f"<b>1h Volume:</b> ${vol}\n"
                    f"<b>Buyers (1h):</b> {buyers}\n"
                    f"<b>Alpha Score:</b> {score}/100\n"
                    f"<b>Time:</b> {now.strftime('%H:%M:%S UTC')}\n\n"
                    "Tracking initiated... ð"
                )
                await bot.send_message(chat_id=TELEGRAM_ID, text=msg, parse_mode="HTML")
                processed_tokens[address] = now

        await asyncio.sleep(4)
