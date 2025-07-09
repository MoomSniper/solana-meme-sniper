# sniper.py
import logging
import requests
import time
import os
from dotenv import load_dotenv
from telegram import Bot

TELEGRAM_ID = os.getenv("TELEGRAM_ID")
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
bot = Bot(token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

BIRDEYE_API = os.getenv("BIRDEYE_API")
HEADERS = {"X-API-KEY": BIRDEYE_API}


def get_top_coins(limit=30):
    url = f"https://public-api.birdeye.so/public/tokenlist?sort_by=volume_24h&sort_type=desc&limit={limit}&offset=0"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    return data.get("data", [])


def run_sniper():
    logger.info("🧠 Obsidian Mode Sniper Live")

    while True:
        try:
            logger.info("🔎 Scanning...")

            coins = get_top_coins()
            for coin in coins:
                name = coin["name"]
                symbol = coin["symbol"]
                address = coin["address"]
                volume = float(coin["volume_24h"])
                market_cap = float(coin.get("market_cap", 0))

                if market_cap >= 100_000 and volume >= 20_000:
                    price = coin["price"]
                    url = f"https://birdeye.so/token/{address}?chain=solana"

                    text = (
                        f"💥 *Test Coin Alert!*\n\n"
                        f"*Name:* {name} ({symbol})\n"
                        f"*Price:* ${price:.6f}\n"
                        f"*Market Cap:* ${int(market_cap):,}\n"
                        f"*24h Volume:* ${int(volume):,}\n"
                        f"[View on Birdeye]({url})"
                    )

                    try:
                        bot.send_message(chat_id=TELEGRAM_ID, text=text, parse_mode="Markdown", disable_web_page_preview=True)
                        logger.info("✅ Alert sent to Telegram")
                    except Exception as e:
                        logger.error(f"Telegram send failed: {e}")

                    time.sleep(60)
                    return

            time.sleep(15)

        except Exception as e:
            logger.error(f"❌ Error in sniper: {e}")
            time.sleep(10)
