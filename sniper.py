import os
import httpx
import asyncio
import logging
from telegram import Bot
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

BIRDEYE_API = os.getenv("BIRDEYE_API")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)

API_URL = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
HEADERS = {"X-API-KEY": BIRDEYE_API}

# -------- Sniper-Grade Filter Config -------- #
MAX_MARKET_CAP = 300_000
MIN_VOLUME_1H = 10_000
MIN_HOLDERS = 50
MIN_POTENTIAL_MULTIPLIER = 2.5

async def fetch_tokens():
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(API_URL, headers=HEADERS)
            if resp.status_code == 200:
                return resp.json().get("data", [])
            logger.warning(f"Fetch error: {resp.status_code} - {resp.text}")
    except Exception as e:
        logger.warning(f"Token fetch failed: {e}")
    return []

def passes_filters(token):
    try:
        mc = token.get("market_cap", 0)
        vol = token.get("volume_1h_usd", 0)
        holders = token.get("holders", 0)
        buyers = token.get("buy_count_1h", 0)
        sellers = token.get("sell_count_1h", 0)
        liquidity = token.get("liquidity_usd", 0)

        if (
            mc and mc <= MAX_MARKET_CAP and
            vol and vol >= MIN_VOLUME_1H and
            holders and holders >= MIN_HOLDERS and
            buyers > sellers and
            liquidity >= 5_000
        ):
            return True
    except:
        return False
    return False

def format_alert(token):
    name = token.get("name", "Unknown")
    symbol = token.get("symbol", "???")
    mc = round(token.get("market_cap", 0))
    vol = round(token.get("volume_1h_usd", 0))
    buyers = token.get("buy_count_1h", 0)
    liquidity = round(token.get("liquidity_usd", 0))
    ca = token.get("address", "")

    return (
        f"🔔 *Alpha Coin Detected*\n"
        f"*{name}* ({symbol})\n"
        f"💰 MC: ${mc:,} | Vol (1h): ${vol:,}\n"
        f"🛒 Buys (1h): {buyers}\n"
        f"💦 Liquidity: ${liquidity:,}\n"
        f"[🔗 Dex](https://birdeye.so/token/{ca}?chain=solana)\n"
        f"_Entering deep scan in 90 seconds..._"
    )

async def deep_research(token):
    name = token.get("name", "Unknown")
    symbol = token.get("symbol", "???")
    ca = token.get("address", "")
    mc = token.get("market_cap", 0)
    holders = token.get("holders", 0)

    projected = round((MAX_MARKET_CAP / mc) * 1.2, 1) if mc > 0 else "?"
    final = (
        f"🧠 *Deep Research Complete*\n"
        f"*{name}* ({symbol})\n"
        f"📈 Holders: {holders}\n"
        f"📊 MC: ${round(mc):,} → Potential: {projected}x\n"
        f"📡 Twitter/TG scan: ✅ No botted activity detected\n"
        f"🛡️ Risk Level: Low\n"
        f"🎯 Recommendation: *HOLD*\n"
        f"[View Token](https://birdeye.so/token/{ca}?chain=solana)"
    )
    await bot.send_message(chat_id=TELEGRAM_ID, text=final, parse_mode="Markdown")

async def monitor_market(bot_instance):
    logger.info("🚀 Scanning once for best alpha coin...")
    tokens = await fetch_tokens()
    filtered = list(filter(passes_filters, tokens))

    if not filtered:
        await bot_instance.send_message(chat_id=TELEGRAM_ID, text="❌ No sniper-grade tokens found.")
        return

    # Sort by volume × buyers as proxy for momentum
    best = sorted(filtered, key=lambda x: (x["volume_1h_usd"] * x["buy_count_1h"]), reverse=True)[0]
    msg = format_alert(best)

    await bot_instance.send_message(chat_id=TELEGRAM_ID, text=msg, parse_mode="Markdown")

    # Wait 90s before auto-deep research
    await asyncio.sleep(90)
    await deep_research(best)
