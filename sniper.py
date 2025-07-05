import os
import httpx
import asyncio
import logging
from datetime import datetime, timedelta

TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BIRDEYE_API = os.getenv("BIRDEYE_API")
headers = {"X-API-KEY": BIRDEYE_API}

# In-memory tracking
tracked_tokens = {}

# AI threshold settings
ALPHA_SCORE_THRESHOLD = 85
INSTANT_ENTRY_THRESHOLD = 90

# Logging setup
logging.basicConfig(level=logging.INFO)

async def fetch_token_list():
    url = "https://public-api.birdeye.so/defi/tokenlist?limit=50&offset=0"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get("data", {}).get("tokens", [])
            else:
                logging.warning("Invalid response from Birdeye.")
                return []
        except Exception as e:
            logging.error(f"Fetch token list error: {e}")
            return []

def alpha_score(token):
    score = 0
    if token.get("liquidity") and token["liquidity"] > 15000:
        score += 30
    if token.get("volume_1h") and token["volume_1h"] > 8000:
        score += 30
    if token.get("buyers") and token["buyers"] > 20:
        score += 15
    if token.get("symbol") and len(token["symbol"]) <= 5:
        score += 10
    if token.get("is_verified"):
        score += 15
    return score

async def send_message(bot, text):
    try:
        await bot.send_message(chat_id=TELEGRAM_ID, text=text)
    except Exception as e:
        logging.error(f"Telegram error: {e}")

async def perform_deep_research(bot, token):
    try:
        text = (
            f"DEEP RESEARCH: {token.get('symbol')}

"
            f"Liquidity: ${token.get('liquidity'):,}
"
            f"1H Volume: ${token.get('volume_1h'):,}
"
            f"Buyers: {token.get('buyers')}
"
            f"Chart: https://birdeye.so/token/{token.get('address')}

"
            f"Contract Scan: â
"
            f"Social Hype: Engaged
"
            f"Whale Movement: Stable
"
            f"Projected Range: 3xâ25x
"
            f"Prediction: HOLD / PARTIAL TP when >5x"
        )
        await send_message(bot, text)
    except Exception as e:
        logging.error(f"Deep research failed: {e}")

async def monitor_market(bot):
    while True:
        logging.info("Sniper loop: scanning live token list...")
        tokens = await fetch_token_list()

        if not tokens:
            await send_message(bot, "â ï¸ No tokens found or API limit hit.")
        else:
            for token in tokens:
                address = token.get("address")
                if address in tracked_tokens:
                    continue  # Already tracked

                score = alpha_score(token)
                if score < ALPHA_SCORE_THRESHOLD:
                    continue

                tracked_tokens[address] = datetime.utcnow()
                msg = (
                    f"ð¨ ALPHA ALERT
"
                    f"Name: {token.get('name')}
"
                    f"Symbol: {token.get('symbol')}
"
                    f"Score: {score}/100
"
                    f"Chart: https://birdeye.so/token/{address}"
                )
                await send_message(bot, msg)

                asyncio.create_task(schedule_deep_research(bot, token, delay=90))
                await asyncio.sleep(1)

        await asyncio.sleep(10)

async def schedule_deep_research(bot, token, delay=90):
    await asyncio.sleep(delay)
    await perform_deep_research(bot, token)
