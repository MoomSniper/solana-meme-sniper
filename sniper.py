import asyncio
import logging
import os
import time
import requests
from telegram import Bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper-test")

BIRDEYE_API = os.getenv("BIRDEYE_API")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")

bot = Bot(token=BOT_TOKEN)

def get_top_coins():
    url = "https://public-api.birdeye.so/public/tokenlist?sort_by=volume_24h&sort_type=desc&limit=10"
    headers = {"X-API-KEY": BIRDEYE_API}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json().get("data", [])
    except Exception as e:
        logger.error(f"Error fetching top coins: {e}")
        return []

def filter_and_alert(coins):
    for coin in coins:
        try:
            name = coin.get("name")
            symbol = coin.get("symbol")
            address = coin.get("address")
            volume = float(coin.get("volume_24h", 0))
            market_cap = float(coin.get("mc", 0))
            if market_cap >= 80000 and volume >= 25000:
                text = f"🔔 *Test Coin Alert!*"
{name} ({symbol})
MC: ${int(market_cap):,}
24h Volume: ${int(volume):,}
Birdeye: https://birdeye.so/token/{address}?chain=solana"
                bot.send_message(chat_id=TELEGRAM_ID, text=text, parse_mode="Markdown")
                logger.info(f"Alert sent for {symbol}")
                return True
        except Exception as e:
            logger.error(f"Error parsing coin: {e}")
    return False

async def run_test_sniper():
    logger.info("ð Running test sniper...")
    while True:
        coins = get_top_coins()
        if filter_and_alert(coins):
            logger.info("â Test alert sent. Stopping sniper.")
            break
        logger.info("ð No eligible coins yet. Retrying in 60s...")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(run_test_sniper())
