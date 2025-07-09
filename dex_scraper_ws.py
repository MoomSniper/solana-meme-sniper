import asyncio, json, logging, ssl
import websockets
from telegram import Bot
from config import TELEGRAM_ID, BOT_TOKEN

logger = logging.getLogger("DEXScraperWS")
bot = Bot(token=BOT_TOKEN)
sent = set()

WS_URL = (
    "wss://io.dexscreener.com/dex/screener/pairs/h24/1?"
    "rankBy[key]=trendingScoreH6&rankBy[order]=desc"
)

HEADERS = {
    "Host": "io.dexscreener.com",
    "Origin": "https://dexscreener.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

ssl_context = ssl.create_default_context()

async def run_ws_sniper():
    while True:
        try:
            async with websockets.connect(WS_URL, extra_headers=HEADERS, ssl=ssl_context) as ws:
                logger.info("🔌 WebSocket connected")
                async for msg in ws:
                    data = json.loads(msg)
                    if data.get("type") != "pairs": continue

                    for p in data["pairs"]:
                        addr = p.get("pairAddress")
                        if not addr or addr in sent: continue
                        sent.add(addr)

                        name = p["baseTokenName"]
                        price = p.get("priceUsd")
                        vol = p.get("volume", {}).get("h24")
                        text = f"🚨 *Live Token*\n{name}\nPrice: ${price}\nVolume24h: ${vol}"
                        await bot.send_message(chat_id=TELEGRAM_ID, text=text, parse_mode="Markdown")
                        logger.info(f"📤 Alert sent for {name}")

        except Exception as e:
            logger.error(f"🛑 WS connect error: {e}. Retrying in 5s...")
            await asyncio.sleep(5)
