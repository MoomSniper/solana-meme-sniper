import asyncio
import logging
import os
import httpx

BOT_TOKEN = os.environ['BOT_TOKEN']
TELEGRAM_ID = os.environ['TELEGRAM_ID']
BIRDEYE_API = os.environ['BIRDEYE_API']

logging.basicConfig(level=logging.INFO)

async def send_telegram_message(text):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": TELEGRAM_ID, "text": text}
            )
    except Exception as e:
        logging.error(f"❌ Failed to send Telegram message: {e}")

async def sniper_loop():
    while True:
        try:
            logging.info("🔍 Scanning for coins...")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://public-api.birdeye.so/public/token/price?sort=volume_1h_usd&order=desc",
                    headers={"X-API-KEY": BIRDEYE_API}
                )
                data = response.json().get("data", [])

            if not data:
                logging.warning("⚠️ No tokens found or Birdeye limit hit.")
            else:
                for token in data:
                    symbol = token.get("symbol", "")
                    volume = token.get("volume_1h_usd", 0)
                    market_cap = token.get("market_cap", 0)

                    if volume > 5000 and market_cap and market_cap < 300_000:
                        msg = (
                            f"🚀 Alpha Coin Found: {symbol}\n"
                            f"MC: ${int(market_cap):,}\n"
                            f"1h Volume: ${int(volume):,}"
                        )
                        await send_telegram_message(msg)
                        break  # only send 1 at a time

        except Exception as e:
            logging.error(f"❌ Error in sniper_loop: {e}")

        await asyncio.sleep(30)  # quiet 30s interval to respect free tier
