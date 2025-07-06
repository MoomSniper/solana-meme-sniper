import os
import httpx
import logging
import asyncio
from telegram import Bot

BIRDEYE_API = os.getenv("BIRDEYE_API")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")

API_URL = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

def is_sniper_grade(token):
    try:
        mc = float(token.get("mc", 0))
        volume = float(token.get("volume", 0))
        buyers = int(token.get("buyers", 0))

        return (
            mc > 10_000 and mc < 300_000 and
            volume > 5_000 and buyers > 15
        )
    except Exception as e:
        logger.warning(f"Token parse error: {e}")
        return False

async def send_message(bot, text):
    await bot.send_message(chat_id=TELEGRAM_ID, text=text)

async def monitor_market(bot: Bot):
    headers = {"X-API-KEY": BIRDEYE_API}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(API_URL, headers=headers, timeout=10)
            if response.status_code == 429:
                await send_message(bot, "❌ Birdeye rate limited. Upgrade your API or slow down.")
                return

            data = response.json()
            tokens = data.get("data", [])

            sniper_tokens = [t for t in tokens if is_sniper_grade(t)]

            if not sniper_tokens:
                await send_message(bot, "❌ No sniper-grade tokens found.")
                return

            # Pick best token by volume
            best_token = max(sniper_tokens, key=lambda t: float(t.get("volume", 0)))
            symbol = best_token.get("symbol", "Unknown")
            address = best_token.get("address")
            mc = best_token.get("mc", "N/A")
            volume = best_token.get("volume", "N/A")

            msg = f"🎯 *Alpha Token Detected!*\n\n" \
                  f"Token: `{symbol}`\n" \
                  f"MC: ${mc}\n" \
                  f"Volume: ${volume}\n" \
                  f"[View on DexScreener](https://dexscreener.com/solana/{address})\n\n" \
                  f"🔍 Entering deep research..."
            await send_message(bot, msg)

            # 🔍 Add your deep research function here if needed

        except Exception as e:
            logger.error(f"Fetch error: {e}")
            await send_message(bot, f"❌ Error during token fetch: {e}")
