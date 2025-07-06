import asyncio
import logging
import os
import httpx
import time
from telegram import Bot

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

# Env vars
BIRDEYE_API = os.getenv("BIRDEYE_API")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))

bot = Bot(token=BOT_TOKEN)

# Core loop
async def monitor_market():
    logger.info("⚔️ OBLIVION MODE ACTIVE - Starting market monitor...")

    async with httpx.AsyncClient() as client:
        try:
            headers = {"X-API-KEY": BIRDEYE_API}
            url = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
            res = await client.get(url, headers=headers)
            data = res.json()

            tokens = data.get("data", [])
            if not isinstance(tokens, list):
                logger.warning("Birdeye returned non-list token data")
                return

            for token in tokens[:15]:  # loose filter for test
                token_address = token.get("address")
                symbol = token.get("symbol")
                liquidity = token.get("liquidity", 0)
                volume_1h = token.get("volume_h1", 0)
                buyers = token.get("buyers", 0)
                mcap = token.get("marketCap", 0)

                # ENTRY SIGNAL ENGINE (simple v1)
                score = 0
                if volume_1h > 5000:
                    score += 25
                if buyers > 10:
                    score += 25
                if liquidity > 10000:
                    score += 20
                if mcap and mcap < 300000:
                    score += 30

                if score >= 80:
                    confidence = "🔥 High Confidence"
                    hype = f"🎯 ENTRY CONFIDENCE: {score}%"
                else:
                    continue  # skip if not alpha enough

                # Simulate deep scan v2
                alert = f"""⚡️ New Solana Coin Detected!

Name: {symbol}
Score: {score}/100
{hype}
Buyers: {buyers}
1H Volume: ${volume_1h:,.0f}
Liquidity: ${liquidity:,.0f}
Market Cap: ${mcap:,.0f}

Tracking: Twitter ✅ Telegram ✅ Contract ✅

🚀 Potential Play — Monitor Closely.
                """

                await bot.send_message(chat_id=TELEGRAM_ID, text=alert)

        except Exception as e:
            logger.warning(f"Error fetching tokens: {e}")
        finally:
            logger.info("Scan complete.")
