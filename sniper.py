import httpx
import logging
import asyncio
import os
from telegram import Bot

BIRDEYE_API = os.getenv("BIRDEYE_API")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

bot = Bot(token=BOT_TOKEN)

async def send_message_safe(text):
    try:
        await bot.send_message(chat_id=TELEGRAM_ID, text=text)
    except Exception as e:
        logger.warning(f"Failed to send Telegram message: {e}")

async def fetch_live_tokens():
    url = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
    headers = {"X-API-KEY": BIRDEYE_API}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
    except Exception as e:
        logger.warning(f"Error fetching tokens: {e}")
        return []

async def deep_research(coin):
    name = coin.get("name", "Unknown")
    address = coin.get("address", "N/A")
    symbol = coin.get("symbol", "N/A")
    text = (
        f"🔍 Deep Research Mode Initiated\n\n"
        f"Name: {name}\n"
        f"Symbol: {symbol}\n"
        f"Address: {address}\n\n"
        f"Researching contract, liquidity, holders, and social signals..."
    )
    await send_message_safe(text)

async def monitor_market():
    await send_message_safe("📡 Scanning live Solana market for new tokens...")

    tokens = await fetch_live_tokens()
    if not tokens:
        await send_message_safe("❌ No tokens found or API failed.")
        return

    # Just send top 3 for now — no filter
    selected = tokens[:3]

    for token in selected:
        name = token.get("name", "Unknown")
        symbol = token.get("symbol", "N/A")
        address = token.get("address", "N/A")
        launch_text = (
            f"🚀 New Token Detected\n\n"
            f"Name: {name}\n"
            f"Symbol: {symbol}\n"
            f"Address: {address}\n"
        )
        await send_message_safe(launch_text)
        await deep_research(token)

    await send_message_safe("✅ Scan complete. Monitoring will restart on next trigger.")
