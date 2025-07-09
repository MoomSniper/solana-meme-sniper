import asyncio
import json
import logging
import websockets
from telegram import Bot
from config import TELEGRAM_ID, BOT_TOKEN

logger = logging.getLogger("DEXScraperWS")
bot = Bot(token=BOT_TOKEN)
sent = set()

WS_URL = (
    "wss://io.dexscreener.com/dex/screener/pairs/h24/1"
    "?rankBy[key]=trendingScoreH6&rankBy[order]=desc"
)

HEADERS = {
    "Origin": "https://dexscreener.com",
    "User-Agent": "Mozilla/5.0",
}

async def run_ws_sniper():
    async for ws in websockets.connect(WS_URL, extra_headers=HEADERS):
        try:
            logger.info("🔌 WebSocket connected")
            async for message in ws:
                data = json.loads(message)
                if data.get("type") != "pairs":
                    continue
                for p in data.get("pairs", []):
                    addr = p.get("pairAddress")
                    if not addr or addr in sent:
                        continue
                    sent.add(addr)
                    name = p["baseTokenName"]
                    price = p.get("priceUsd")
                    vol = p.get("volume", {}).get("h24")
                    msg = (
                        f"🚨 *Live Coin Detected!*\n"
                        f"Name: {name}\n"
                        f"Price: ${price}\n"
                        f"24h Volume: ${vol}"
                    )
                    await bot.send_message(
                        chat_id=TELEGRAM_ID,
                        text=msg,
                        parse_mode="Markdown"
                    )
                    logger.info(f"📤 Alert sent for {name}")
        except Exception as e:
            logger.error(f"🛑 WebSocket error: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)
