import os
import asyncio
import logging
import httpx
from modules.alpha_scoring import score_token
from modules.alert_formatter import format_alert
from telegram import Bot

# === Config ===
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOLANATRACKER_API = "https://api.solanatracker.io/v1/tokens/live"
HEADERS = {"accept": "application/json", "x-api-key": os.getenv("SOLANATRACKER_API")}
CHECK_INTERVAL = 2  # Seconds between scans

# === Setup ===
bot = Bot(token=BOT_TOKEN)
seen = set()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

async def scan_and_score_market():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(SOLANATRACKER_API, headers=HEADERS, timeout=10)
            data = response.json()
            tokens = data.get("tokens", [])[:25]  # Limit tokens scanned per loop

            for token in tokens:
                address = token.get("address")
                if not address or address in seen:
                    continue

                score = score_token(token)
                if score >= 85:
                    seen.add(address)
                    return token

    except Exception as e:
        logger.error(f"[Scan Error] {e}")
    return None
