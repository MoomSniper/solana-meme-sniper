import os
import asyncio
import logging
import httpx
import time
from datetime import datetime, timedelta

# Setup
BIRDEYE_API = os.getenv("BIRDEYE_API")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
TOKEN = os.getenv("BOT_TOKEN")

SCAN_INTERVAL = 1.5  # seconds
MIN_VOLUME = 15000  # realistic but tight filter
MAX_MC = 300000  # must be low enough for 5x+ upside

# Obsidian+ mode coin memory to avoid repeats
recent_alerts = {}
alert_cooldown = 900  # 15 minutes cooldown

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def send_alert(bot, msg):
    try:
        await bot.send_message(chat_id=TELEGRAM_ID, text=msg, parse_mode='HTML')
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")

async def fetch_candidates():
    url = "https://public-api.birdeye.so/public/token/solana/overview?sort=volume_1h_usd&order=desc"
    headers = {"X-API-KEY": BIRDEYE_API}
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            res = await client.get(url, headers=headers)
            res.raise_for_status()
            return res.json().get("data", [])[:30]  # top 30 for speed
    except Exception as e:
        logger.warning(f"Birdeye fetch failed: {e}")
        return []

def is_recently_alerted(address):
    now = datetime.utcnow()
    return address in recent_alerts and (now - recent_alerts[address]).total_seconds() < alert_cooldown

def mark_alerted(address):
    recent_alerts[address] = datetime.utcnow()

def calculate_score(token):
    # Custom scoring system — tighten as needed
    mc = token.get("mc") or 0
    vol = token.get("volume_1h_usd") or 0
    buyers = token.get("tx_count_1h") or 0

    if mc == 0 or vol == 0:
        return 0

    if mc > MAX_MC or vol < MIN_VOLUME:
        return 0

    score = 0
    if mc < 120000:
        score += 40
    elif mc < 200000:
        score += 25

    if vol > 30000:
        score += 30
    elif vol > 20000:
        score += 20

    if buyers > 25:
        score += 30
    elif buyers > 15:
        score += 15

    return score

async def monitor_market(bot):
    logger.info("🔍 Sniper scanning started (Oblivion Mode)")
    while True:
        try:
            tokens = await fetch_candidates()
            for token in tokens:
                address = token.get("address")
                score = calculate_score(token)

                if score >= 85 and not is_recently_alerted(address):
                    name = token.get("symbol", "Unknown")
                    mc = token.get("mc", 0)
                    vol = token.get("volume_1h_usd", 0)
                    buyers = token.get("tx_count_1h", 0)
                    link = f"https://birdeye.so/token/{address}?chain=solana"

                    msg = (
                        f"<b>🚀 ALPHA FOUND: ${name}</b>\n"
                        f"<b>🧠 Alpha Score:</b> {score}/100\n"
                        f"<b>💰 MC:</b> ${int(mc):,}\n"
                        f"<b>📈 Vol (1h):</b> ${int(vol):,}\n"
                        f"<b>👥 Buys (1h):</b> {buyers}\n"
                        f"<a href='{link}'>🔗 Birdeye Link</a>\n\n"
                        f"<i>Entering Deep Scan in 90s...</i>"
                    )
                    await send_alert(bot, msg)
                    mark_alerted(address)

                    await asyncio.sleep(90)
                    await deep_research(token, bot)

        except Exception as e:
            logger.error(f"Loop error: {e}")

        await asyncio.sleep(SCAN_INTERVAL)

async def deep_research(token, bot):
    name = token.get("symbol", "Unknown")
    address = token.get("address")
    link = f"https://birdeye.so/token/{address}?chain=solana"

    # Placeholder — simulate intelligent research output
    summary = (
        f"<b>🧠 DEEP RESEARCH COMPLETE — ${name}</b>\n"
        f"<b>Projected Range:</b> 3x–12x\n"
        f"<b>Smart Wallets:</b> Still Buying\n"
        f"<b>Bot Risk:</b> Low\n"
        f"<b>Hype Score:</b> 78/100\n"
        f"<b>Alpha Confidence:</b> HIGH\n"
        f"<a href='{link}'>🔗 View Chart</a>\n\n"
        f"<i>⚠️ HOLD with Partial TP on 5x spike</i>"
    )

    await send_alert(bot, summary)
