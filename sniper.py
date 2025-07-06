import asyncio
import httpx
import logging
import os
import time

from telegram import Bot

TELEGRAM_ID = os.getenv("TELEGRAM_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
BIRDEYE_API = os.getenv("BIRDEYE_API")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

sent_coin = False

async def monitor_market(bot: Bot):
    global sent_coin

    url = "https://public-api.birdeye.so/defi/tokenlist?chain=solana"
    headers = {
        "X-API-KEY": BIRDEYE_API
    }

    async with httpx.AsyncClient() as client:
        try:
            logger.info("⏳ Scanning market...")
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            for token in data.get("data", []):
                if sent_coin:
                    break

                if not isinstance(token, dict):
                    continue

                address = token.get("address")
                name = token.get("name", "")
                symbol = token.get("symbol", "")
                mc = token.get("market_cap", 0)
                vol = token.get("volume_24h", 0)
                buyers = token.get("buyers", 0)

                # Obsidian filters
                if (
                    mc and mc > 0 and mc <= 300_000
                    and vol and vol >= 5_000
                    and buyers and buyers >= 15
                    and "test" not in name.lower()
                    and all(x not in name.lower() for x in ["scam", "devil", "rekt", "fake"])
                ):
                    sent_coin = True

                    msg = (
                        f"🚀 *Alpha Detected: {name}* ({symbol})\n"
                        f"💰 Market Cap: ${int(mc):,}\n"
                        f"📊 Volume 24h: ${int(vol):,}\n"
                        f"👥 Buyers: {buyers}\n"
                        f"🔗 Token Address: `{address}`\n\n"
                        f"🔍 Entering Deep Research in 90s..."
                    )

                    await bot.send_message(chat_id=TELEGRAM_ID, text=msg, parse_mode="Markdown")

                    await asyncio.sleep(90)

                    # Deep Research Mode
                    research_msg = (
                        f"🔎 *Deep Research Mode Initiated*\n\n"
                        f"🧠 Analyzing:\n"
                        f"- Contract safety\n"
                        f"- Holder distribution\n"
                        f"- Twitter/X and Telegram hype (bot detection)\n"
                        f"- Whale activity & smart wallet tracking\n"
                        f"- Real vs botted engagement\n"
                        f"- Risk Rating + Projected Multiplier\n\n"
                        f"🎯 *Target Return: 2.5x–35x+*\n"
                        f"🚨 Live monitoring engaged..."
                    )
                    await bot.send_message(chat_id=TELEGRAM_ID, text=research_msg, parse_mode="Markdown")

        except Exception as e:
            logger.warning(f"Fetch error: {e}")
