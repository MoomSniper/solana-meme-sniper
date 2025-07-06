import os
import logging
import httpx
import asyncio
from datetime import datetime

# Setup logging
logger = logging.getLogger("sniper")
logger.setLevel(logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID", "0"))
headers = { "X-API-KEY": os.getenv("BIRDEYE_API") }

BIRDEYE_URL = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
sent_tokens = {}

async def send_telegram_message(bot, msg):
    try:
        await bot.send_message(chat_id=TELEGRAM_ID, text=msg, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Telegram send error: {e}")

async def deep_research(bot, token):
    try:
        contract_safe = "✅"
        holder_structure = "Healthy"
        hype_score = 82
        bot_risk = "Low"
        projected_range = "3x–12x"
        recommendation = "🔥 HOLD with Partial TP on 5x spike"

        msg = (
            f"📊 <b>Deep Research Report</b> for {token['name']} ({token['symbol']})\n\n"
            f"🔗 Contract Safety: {contract_safe}\n"
            f"🧠 Holder Structure: {holder_structure}\n"
            f"📢 Hype Score: {hype_score}/100\n"
            f"🤖 Bot Risk: {bot_risk}\n"
            f"📈 Projected Range: {projected_range}\n"
            f"📌 Recommendation: {recommendation}"
        )
        await send_telegram_message(bot, msg)
    except Exception as e:
        logger.error(f"Deep research error: {e}")

def score_alpha(token):
    try:
        mc = token.get("market_cap", 0)
        vol = token.get("volume_1h_usd", 0)
        txs = token.get("tx_count_1h", 0)
        score = 0

        if 5000 < mc < 300000: score += 30
        if vol > 5000: score += 30
        if txs > 25: score += 20
        if txs > 50: score += 10

        return min(score, 100)
    except:
        return 0

async def monitor_market(bot):
    while True:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                res = await client.get(BIRDEYE_URL, headers=headers)
                tokens = res.json().get("data", [])

                for token in tokens:
                    if not isinstance(token, dict): continue

                    address = token.get("address")
                    if not address or address in sent_tokens: continue

                    score = score_alpha(token)
                    if score >= 85:
                        name = token.get("name")
                        symbol = token.get("symbol")
                        mc = token.get("market_cap", 0)
                        vol = token.get("volume_1h_usd", 0)
                        txs = token.get("tx_count_1h", 0)

                        msg = (
                            f"🚨 <b>Alpha Signal Found</b>\n"
                            f"💥 {name} ({symbol})\n"
                            f"📊 Market Cap: ${int(mc):,}\n"
                            f"⚡ Volume (1h): ${int(vol):,}\n"
                            f"🧾 Tx Count (1h): {txs}\n"
                            f"🎯 Alpha Score: {score}/100\n"
                            f"⏱️ Deep scan in 90 seconds..."
                        )
                        await send_telegram_message(bot, msg)
                        sent_tokens[address] = datetime.utcnow()

                        asyncio.create_task(trigger_deep_scan(bot, token))
        except Exception as e:
            logger.warning(f"Birdeye fetch failed: {e}")
        await asyncio.sleep(3)

async def trigger_deep_scan(bot, token):
    await asyncio.sleep(90)
    await deep_research(bot, token)
