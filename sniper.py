import time
import httpx
import asyncio
import logging

BIRDEYE_API = os.getenv("BIRDEYE_API")
MIN_VOLUME = 5000
MIN_LIQUIDITY = 3000
MIN_MULTIPLIER = 2.5

def is_token_alpha(token):
    try:
        volume = float(token.get("volume_1h", 0))
        liquidity = float(token.get("liquidity", 0))
        mc = float(token.get("market_cap", 0))

        if (
            volume >= MIN_VOLUME and
            liquidity >= MIN_LIQUIDITY and
            mc <= 300000 and
            token.get("is_liquidity_locked", False)
        ):
            return True
    except Exception as e:
        logging.warning(f"Alpha check failed: {e}")
    return False

async def get_token_list():
    try:
        url = f"https://public-api.birdeye.so/defi/tokenlist?limit=100&offset=0"
        headers = {"X-API-KEY": BIRDEYE_API}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                logging.warning(f"Birdeye error: {response.status_code}")
    except Exception as e:
        logging.warning(f"Token fetch failed: {e}")
    return []

async def sniper_loop(bot, chat_id):
    while True:
        tokens = await get_token_list()
        for token in tokens:
            if is_token_alpha(token):
                message = (
                    f"ð *ALPHA FOUND*

"
                    f"Name: {token.get('name')}
"
                    f"Symbol: {token.get('symbol')}
"
                    f"Market Cap: ${token.get('market_cap'):,}
"
                    f"Liquidity: ${token.get('liquidity'):,}
"
                    f"1h Volume: ${token.get('volume_1h'):,}
"
                    f"Link: https://birdeye.so/token/{token.get('address')}

"
                    f"_Tracking deep research and exit signals..._"
                )
                await bot.send_message(chat_id=chat_id, text=message, parse_mode="Markdown")
                await asyncio.sleep(90)
                # Place deep research logic here...
        await asyncio.sleep(30)  # Scan every 30 seconds
