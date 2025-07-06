import os
import time
import httpx
import asyncio
import logging
from datetime import datetime
from telegram import Bot

# === Environment Vars ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")

# === Config ===
DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/pairs"
CHECK_INTERVAL = 2  # seconds between scans
SEEN_LIMIT = 10000  # memory cap

# === Logger ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

# === Telegram Setup ===
bot = Bot(token=BOT_TOKEN)

# === Token Memory ===
seen_tokens = set()

# === Scoring Engine ===
def score_token(token):
    try:
        mc = float(token.get("fdv", 0))
        volume = float(token.get("volume", {}).get("h1", 0))
        buyers = token.get("txns", {}).get("h1", {}).get("buys", 0)
        score = 0

        if 5000 <= volume <= 300000:
            score += 40
        if 10 <= buyers <= 150:
            score += 30
        if mc and mc < 300000:
            score += 30

        return score
    except Exception as e:
        logger.warning(f"[Score Error] {e}")
        return 0

# === Formatter ===
def format_alert(token, score):
    try:
        name = token.get("baseToken", {}).get("name", "Unknown")
        symbol = token.get("baseToken", {}).get("symbol", "?")
        url = token.get("url", "")
        mc = float(token.get("fdv", 0))
        volume = float(token.get("volume", {}).get("h1", 0))
        buyers = token.get("txns", {}).get("h1", {}).get("buys", 0)

        return (
            f"🚨 <b>ALPHA ALERT [{score}%]</b>\n"
            f"<b>{name} ({symbol})</b>\n"
            f"Market Cap: ${int(mc):,}\n"
            f"Volume (1h): ${int(volume):,}\n"
            f"Buys (1h): {buyers}\n"
            f"<a href='{url}'>View Chart</a>"
        )
    except Exception as e:
        logger.warning(f"[Format Error] {e}")
        return "❌ Error formatting alert."

# === Sniper Core Loop ===
async def start_sniping():
    logger.info("📡 Starting sniper scan...")

    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(DEXSCREENER_API)
                data = resp.json()

                if not data or "pairs" not in data:
                    logger.info(f"🔎 Scanning {len(data['pairs'])} pairs at {datetime.now().isoformat()}")
                    logger.warning("❌ DEX Screener: No pairs returned.")
                    await asyncio.sleep(CHECK_INTERVAL)
                    continue

                for token in data["pairs"]:
                    pair_address = token.get("pairAddress")
                    if pair_address in seen_tokens:
                        continue

                    score = score_token(token)
                    if score >= 85:
                        alert_msg = format_alert(token, score)
                        await bot.send_message(
                            chat_id=TELEGRAM_ID,
                            text=alert_msg,
                            parse_mode="HTML",
                            disable_web_page_preview=False
                        )
                        seen_tokens.add(pair_address)
                        logger.info(f"✅ Alert sent for {pair_address} [{score}%]")

        except Exception as e:
            logger.error(f"[Sniper Error] {e}")

        await asyncio.sleep(CHECK_INTERVAL)

        if len(seen_tokens) > SEEN_LIMIT:
            seen_tokens.clear()
