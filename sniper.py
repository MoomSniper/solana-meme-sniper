import asyncio
import logging
import httpx
from datetime import datetime
from pytz import timezone

# === CONFIG ===
TELEGRAM_ID = "6881063420"
TIMEZONE = timezone("America/Toronto")
SCAN_INTERVAL = 44  # seconds
ACTIVE_HOURS = range(7, 24)  # 7AM to 11:59PM
MIN_VOLUME = 5000
MIN_BUYERS = 15
MAX_MARKET_CAP = 300_000

# === LOGGING ===
logger = logging.getLogger("sniper")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# === CORE FUNCTION ===
async def scan_and_score_market():
    while True:
        now = datetime.now(TIMEZONE)
        if now.hour not in ACTIVE_HOURS:
            logger.info("🌙 Sleeping hours. Sniper in rest mode.")
            await asyncio.sleep(300)  # Sleep 5 mins
            continue

        try:
            logger.info("🔍 Scanning market...")
            tokens = await fetch_latest_tokens()
            if not tokens:
                logger.warning("⚠️ No tokens fetched from SolanaTracker.")
                await asyncio.sleep(SCAN_INTERVAL)
                continue

            for token in tokens:
                await evaluate_token(token)

        except Exception as e:
            logger.error(f"[Sniper Fatal] {e}")

        await asyncio.sleep(SCAN_INTERVAL)

# === FETCH TOKENS ===
async def fetch_latest_tokens():
    url = "https://public-api.solanatracker.io/tokens?sort=createdAt&order=desc&limit=10&offset=0"
    headers = {"accept": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                logger.warning(f"[SolanaTracker] Token fetch failed: {response.status_code}")
                return []
    except Exception as e:
        logger.error(f"[SolanaTracker Error] {e}")
        return []

# === EVALUATE TOKEN ===
async def evaluate_token(token):
    try:
        symbol = token.get("symbol", "N/A")
        mint = token.get("mintAddress", "")
        volume = float(token.get("volume1hQuote", 0))
        buyers = int(token.get("txns1h", 0))
        market_cap = int(token.get("fdv", 0))

        logger.info(f"🧪 {symbol} | MC: {market_cap} | Volume: {volume} | Buyers: {buyers}")

        if market_cap > MAX_MARKET_CAP:
            return
        if volume < MIN_VOLUME:
            return
        if buyers < MIN_BUYERS:
            return

        # === Placeholder for Smart Wallet Logic, Hype Score, and Contract Safety ===
        # Replace these with actual intelligence checks in deep mode
        logger.info(f"🎯 [ALPHA] {symbol} meets all filters! Sending to Telegram...")

        # await send_telegram_alert(symbol, mint, market_cap, volume, buyers)

    except Exception as e:
        logger.error(f"[Eval Error] Token eval failed: {e}")

# === SEND TELEGRAM ALERT ===
# async def send_telegram_alert(symbol, mint, market_cap, volume, buyers):
#     message = f"<b>🚀 {symbol} Potential Alpha</b>\nMC: ${market_cap}\nVol: ${volume}\n👥 Buyers: {buyers}\nMint: <code>{mint}</code>"
#     await bot.send_message(chat_id=TELEGRAM_ID, text=message, parse_mode='HTML')
