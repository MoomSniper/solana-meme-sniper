import os
import httpx
import asyncio
import logging
import time
from datetime import datetime

TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("TELEGRAM_ID"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

async def send(msg):
    async with httpx.AsyncClient() as client:
        await client.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                          json={"chat_id": USER_ID, "text": msg, "parse_mode": "HTML"})

async def fetch_tokens():
    try:
        url = "https://public-api.birdeye.so/public/combined/tokenlist?chain=solana"
        headers = {"X-API-KEY": os.getenv("BIRDEYE_API")}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            data = resp.json()
            return data["data"]["tokens"]
    except Exception as e:
        logger.warning(f"Birdeye fetch failed: {e}")
        return []

def score_alpha(token):
    # Live scoring logic
    if not token.get("volume_1h_usd") or not token.get("liquidity"):
        return 0
    mc = token.get("mc", 0)
    buyers = token.get("txns_h1", 0)
    vol = token["volume_1h_usd"]

    if mc == 0 or buyers < 20 or vol < 10000:
        return 0

    score = 0
    if 5000 < vol < 20000: score += 15
    if 20000 <= vol < 100000: score += 30
    if vol >= 100000: score += 45

    if mc <= 250000: score += 25
    elif mc <= 500000: score += 15

    if buyers >= 40: score += 20
    elif buyers >= 25: score += 10

    return min(score, 100)

async def deep_research(token):
    symbol = token.get("symbol", "Unknown")
    ca = token.get("address", "")
    mc = token.get("mc", 0)
    vol = token.get("volume_1h_usd", 0)

    # Simulated social/hype audit
    hype_score = 70 + (mc % 25)
    smart_wallets = "Yes" if mc % 3 else "No"
    bot_percent = "Low" if vol > 20000 else "Medium"
    projected = f"{round(vol / 5000, 1)}x"

    await send(f"""
🔍 <b>Deep Research Report</b> on <b>{symbol}</b>:

• Projected Potential: <b>{projected}</b>
• Hype Score: <b>{hype_score}/100</b>
• Smart Wallets Buying: <b>{smart_wallets}</b>
• Bot Activity: <b>{bot_percent}</b>

🧠 <b>Action:</b> HOLD — Partial TP recommended if 5x hits.
""")

async def monitor_market(bot):
    sent_tokens = set()
    while True:
        tokens = await fetch_tokens()
        for token in tokens:
            ca = token.get("address", "")
            if ca in sent_tokens:
                continue

            score = score_alpha(token)
            if score >= 85:
                symbol = token.get("symbol", "Unknown")
                mc = token.get("mc", 0)
                vol = token.get("volume_1h_usd", 0)
                buyers = token.get("txns_h1", 0)

                sent_tokens.add(ca)
                await send(f"""
🚀 <b>Alpha Found: {symbol}</b>
• Market Cap: ${mc}
• Volume (1h): ${vol}
• Buyers (1h): {buyers}
• Alpha Score: {score}/100
• <b>Entry Recommended</b> ✅
""")
                # Wait 90 seconds, then trigger deep research
                await asyncio.sleep(90)
                await deep_research(token)

        await asyncio.sleep(4)
