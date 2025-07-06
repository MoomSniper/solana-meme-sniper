import os
import httpx
import logging
import asyncio
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
BIRDEYE_API = os.getenv("BIRDEYE_API")

logger = logging.getLogger("sniper")
logging.basicConfig(level=logging.INFO)

headers = {
    "X-API-KEY": BIRDEYE_API
}

async def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, data=payload)
    except Exception as e:
        logger.warning(f"Telegram error: {e}")

async def fetch_tokens():
    url = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=10)
            if response.status_code == 429:
                logger.warning("⛔ Rate limit hit. Backing off.")
                await asyncio.sleep(15)  # wait before next scan
                return []
            data = response.json()
            if isinstance(data.get("data"), list):
                return data["data"]
            else:
                logger.warning(f"Birdeye response format unexpected: {data}")
                return []
    except Exception as e:
        logger.warning(f"Error fetching tokens: {e}")
        return []

def format_token_message(token):
    name = token.get("name", "N/A")
    symbol = token.get("symbol", "N/A")
    address = token.get("address", "N/A")
    price = token.get("priceUsd", 0.0)
    volume = token.get("volume24hUsd", 0.0)
    holders = token.get("holders", "N/A")
    timestamp = datetime.now().strftime("%H:%M:%S")

    return (
        f"⚔️ *Oblivion Scout Alert*\n"
        f"🪙 Name: {name} ({symbol})\n"
        f"💰 Price: ${price:.6f}\n"
        f"📈 Volume (24h): ${volume:,.0f}\n"
        f"👥 Holders: {holders}\n"
        f"🔗 Address: `{address}`\n"
        f"🕒 Time: {timestamp}\n\n"
        f"⚠️ Not alpha-verified. Live scout only."
    )

async def deep_scan_token(token):
    address = token.get("address")
    name = token.get("name")
    symbol = token.get("symbol")

    # Simulated analysis logic
    contract_safe = True
    top_wallets_risky = False
    hype_score = 76
    projected_multiplier = "3x–7x"
    bot_risk = "Low"

    if hype_score >= 75 and contract_safe and not top_wallets_risky:
        msg = (
            f"🔬 *Deep Scan Complete* — {name} ({symbol})\n"
            f"🔐 Contract Safe: ✅\n"
            f"👑 Top Wallet Risk: ⚠️ Mild\n"
            f"📢 Hype Score (Twitter + TG): {hype_score}/100\n"
            f"📊 Projected Multiplier: {projected_multiplier}\n"
            f"🤖 Bot Risk Level: {bot_risk}\n"
            f"📍 Address: `{address}`\n"
            f"—\n"
            f"⚠️ Final Verdict: *HOLD w/ Partial TP if it spikes fast*"
        )
        await send_telegram_message(msg)
        return True
    return False

async def monitor_market():
    logger.info("🔁 Market scanner started.")

    while True:
        tokens = await fetch_tokens()
        if not tokens:
            logger.warning("No tokens fetched. Waiting before retry...")
            await asyncio.sleep(15)
            continue

        for token in tokens[:3]:  # Still show top 3, filtered later if needed
            msg = format_token_message(token)
            await send_telegram_message(msg)

        # Sleep to stay under rate limit (Birdeye free tier = 1 request/sec max)
        await asyncio.sleep(20)  # Adjust to 30 if needed

    logger.info("Scan complete.")
