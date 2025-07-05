import os
import httpx
import asyncio
import logging

TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SCAN_INTERVAL = 30  # seconds

async def fetch_token_list():
    url = "https://public-api.birdeye.so/defi/tokenlist?limit=100&offset=0"
    headers = {
        "accept": "application/json",
        "X-API-KEY": os.getenv("BIRDEYE_API")
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                logger.warning(f"Invalid response from Birdeye: {response.status_code}")
                return []
    except Exception as e:
        logger.error(f"Failed to fetch token list: {e}")
        return []

async def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        async with httpx.AsyncClient() as client:
            await client.post(url, data=payload)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

def is_alpha(token):
    try:
        mc = float(token.get("market_cap", 0))
        vol = float(token.get("volume_1h", 0))
        locked = token.get("is_liquidity_locked", False)
        return mc < 300000 and vol > 5000 and locked
    except:
        return False

async def monitor_market():
    logger.info("ð§  Sniper loop: scanning live token list...")

    tokens = await fetch_token_list()
    logger.info(f"ð Fetched {len(tokens)} tokens from Birdeye.")

    for token in tokens:
        if not is_alpha(token):
            continue

        msg = (
            f"ð *ALPHA FOUND!*
"
            f"Name: {token.get('name')}
"
            f"Symbol: {token.get('symbol')}
"
            f"Market Cap: ${token.get('market_cap')}
"
            f"1h Volume: ${token.get('volume_1h')}
"
            f"Chart: https://birdeye.so/token/{token.get('address')}"
        )
        await send_telegram_message(msg)

    await asyncio.sleep(SCAN_INTERVAL)
    await monitor_market()
