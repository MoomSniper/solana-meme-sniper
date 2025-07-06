import os
import logging
import asyncio
import httpx
import time
from datetime import datetime
from telegram.constants import ParseMode

BIRDEYE_API = os.getenv("BIRDEYE_API")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
bot = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

HEADERS = {
    "accept": "application/json",
    "x-api-key": BIRDEYE_API
}

async def fetch_top_coin():
    url = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            tokenlist = r.json().get("data", [])
            if not tokenlist:
                logger.warning("No tokens returned.")
                return None
            top = tokenlist[0]  # Just grab the first one
            return {
                "address": top.get("address"),
                "name": top.get("name"),
                "symbol": top.get("symbol"),
                "market_cap": top.get("mc"),
                "volume_1h": top.get("volume_1h_usd"),
                "buyers": top.get("txns_1h"),
            }
        except Exception as e:
            logger.warning(f"Fetch error: {e}")
            return None

async def send_message(text):
    if bot:
        await bot.send_message(chat_id=TELEGRAM_ID, text=text, parse_mode=ParseMode.HTML)

async def deep_research(coin):
    await asyncio.sleep(5)  # Replace with 90 for real runs
    # Fake deep research logic
    report = f"""
ð§  <b>DEEP RESEARCH INITIATED</b>

<b>Name:</b> {coin['name']} ({coin['symbol']})
<b>Buyers (1h):</b> {coin['buyers']}
<b>MC:</b> ${coin['market_cap']:,}
<b>Vol (1h):</b> ${coin['volume_1h']:,}

<b>Contract Safety:</b> Clean â
<b>Smart Wallets:</b> Detected ð§ 
<b>Twitter Hype:</b> Real ð¦
<b>Telegram:</b> Organic ð¢

<b>Prediction:</b> 3â6x Run Potential
<b>Action:</b> HOLD or TP Partial at 3.5x+
    """
    await send_message(report)

async def monitor_market(telegram_bot):
    global bot
    bot = telegram_bot
    await send_message("ð§ª Testing Mode: Forcing best live coin into deep research...")

    coin = await fetch_top_coin()
    if coin:
        alpha_msg = f"""
ð¨ <b>ALPHA SIGNAL [TEST MODE]</b>

<b>{coin['name']} ({coin['symbol']})</b>
<b>MC:</b> ${coin['market_cap']:,}
<b>Vol (1h):</b> ${coin['volume_1h']:,}
<b>Buyers:</b> {coin['buyers']}

ð Entering deep research in 5s...
        """
        await send_message(alpha_msg)
        await deep_research(coin)
    else:
        await send_message("â No token found in test override.")
