import os
import time
import httpx
import logging
from telegram import Bot

TELEGRAM_ID = os.getenv("TELEGRAM_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BIRDEYE_API = os.getenv("BIRDEYE_API")

bot = Bot(token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

headers = {
    "accept": "application/json",
    "X-API-KEY": BIRDEYE_API
}

def send_message(text):
    try:
        bot.send_message(chat_id=TELEGRAM_ID, text=text)
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

def fetch_tokens():
    try:
        url = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
        response = httpx.get(url, headers=headers)
        data = response.json()
        return data.get("data", [])[:3]  # Only return top 3 tokens
    except Exception as e:
        logger.warning(f"Error fetching tokens: {e}")
        return []

def monitor_market():
    send_message("⚙️ TEST MODE: Loosened filters. Fetching up to 3 live tokens now...")

    tokens = fetch_tokens()
    if not tokens:
        send_message("❌ No tokens found in test scan.")
        return

    for token in tokens:
        try:
            name = token.get("name", "N/A")
            symbol = token.get("symbol", "N/A")
            address = token.get("address", "N/A")
            link = f"https://birdeye.so/token/{address}?chain=solana"

            send_message(
                f"🔍 **Token Found in Test Mode**\n"
                f"Name: {name}\n"
                f"Symbol: {symbol}\n"
                f"[Chart Link]({link})"
            )

            # Simulate Deep Research Mode trigger
            send_message(
                f"🧠 Deep Research Mode Initiated for {symbol}...\n"
                f"🔗 {link}"
            )
        except Exception as e:
            logger.warning(f"Token parse error: {e}")
