import asyncio
import logging
import requests
from config import TELEGRAM_ID, BOT_TOKEN, BIRDEYE_API
from telegram import Bot

# === Setup ===
bot = Bot(token=BOT_TOKEN)
logger = logging.getLogger("sniper")
logging.basicConfig(level=logging.INFO)

# === Config Constants ===
DEX_API = "https://public-api.birdeye.so/public/tokenlist?sort_by=volume_24h"
HEADERS = {"X-API-KEY": BIRDEYE_API}

# === Global Throttle ===
SCAN_INTERVAL = 10  # seconds
VOLUME_THRESHOLD = 5000  # USD
MAX_REQUESTS_PER_DAY = 1000

# === Track Sent Coins ===
sent_alerts = set()

# === Helper Functions ===
 fetch_tokens():
    try:
        response = requests.get(DEX_API, headers=HEADERS)
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        logger.error(f"Fetch error: {e}")
        return []

def is_valid_token(token):
    try:
        volume = float(token.get("volume_24h", 0))
        market_cap = float(token.get("mc", 0))
        buyers = int(token.get("tx_count_24h", 0))
        symbol = token.get("symbol", "").lower()
        name = token.get("name", "").lower()

        if volume < VOLUME_THRESHOLD:
            return False
        if "test" in name or "dev" in name or "scam" in name:
            return False
        if any(s in symbol for s in ["rug", "test", "dev"]):
            return False

        return True
    except:
        return False

def format_alert(token):
    name = token.get("name", "N/A")
    symbol = token.get("symbol", "N/A")
    address = token.get("address", "N/A")
    volume = float(token.get("volume_24h", 0))
    market_cap = float(token.get("mc", 0))
    buyers = int(token.get("tx_count_24h", 0))
    token_address = token.get("address", "N/A")

    return (
        "🚨 *Sniper Alert - Potential Alpha*\n"
        f"Name: {name} (${symbol})\n"
        f"MC: ${market_cap:,.0f}\n"
        f"Volume: ${volume:,.0f}\n"
        f"Buyers: {buyers}\n"
        f"https://birdeye.so/token/{token_address}?chain=solana\n"
        f"https://dexscreener.com/solana/{token_address}"
    )

async def send_alert(token):
    try:
        msg = format_alert(token)
        await bot.send_message(chat_id=TELEGRAM_ID, text=msg, parse_mode="Markdown", disable_web_page_preview=False)
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")

# === Main Sniper Loop ===
async def run_sniper():
    logger.info("🧠 Obsidian Mode Sniper Live")
    while True:
        try:
            tokens = fetch_tokens()  # ✅ THIS WAS MISSING
logger.info(f"✅ Pulled {len(tokens)} tokens from Birdeye")
            for token in tokens:
                address = token.get("address")
                logger.info(f"🔄 Checking token: {token.get('symbol')} | Volume: {token.get('volume_24h')} | MC: {token.get('mc')}")
                if address in sent_alerts:
                    continue
                if is_valid_token(token):
                    await send_alert(token)
                    sent_alerts.add(address)
            logger.info("🔎 Scanning...")
        except Exception as e:
            logger.error(f"Sniper error: {e}")
        await asyncio.sleep(SCAN_INTERVAL)
