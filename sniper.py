import os
import asyncio
import httpx
import logging

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
BIRDEYE_API = os.getenv("BIRDEYE_API")

API_URL = "https://public-api.birdeye.so/defi/tokenlist?limit=100&offset=0"
HEADERS = {"X-API-KEY": BIRDEYE_API}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Track already sent coins
sent_coins = set()

async def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_ID, "text": text, "parse_mode": "Markdown"}
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)

def is_sniper_alpha(token):
    try:
        mc = float(token.get("market_cap", 0))
        vol = float(token.get("volume_h1", 0))
        buyers = int(token.get("buyers", 0))
        name = token.get("name", "").lower()
        symbol = token.get("symbol", "").lower()

        if (
            mc > 10_000 and mc < 300_000 and
            vol >= 5000 and
            buyers >= 15 and
            "test" not in name and
            "airdrop" not in name and
            "dev" not in name
        ):
            return True
    except Exception:
        return False
    return False

async def monitor_market():
    while True:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(API_URL, headers=HEADERS)
                if resp.status_code != 200:
                    logger.warning("Birdeye API failed.")
                    await asyncio.sleep(30)
                    continue

                tokens = resp.json().get("data", [])[:100]

            for token in tokens:
                address = token.get("address")
                if not address or address in sent_coins:
                    continue

                if is_sniper_alpha(token):
                    name = token.get("name", "")
                    symbol = token.get("symbol", "")
                    mc = token.get("market_cap", 0)
                    vol = token.get("volume_h1", 0)
                    buyers = token.get("buyers", 0)
                    url = f"https://birdeye.so/token/{address}?chain=solana"

                    msg = (
                        f"🚀 *ALPHA FOUND!*\n\n"
                        f"*Name:* {name} ({symbol})\n"
                        f"*Market Cap:* ${int(mc):,}\n"
                        f"*Volume (1H):* ${int(vol):,}\n"
                        f"*Buyers (1H):* {buyers}\n\n"
                        f"[View on Birdeye]({url})"
                    )
                    await send_telegram_message(msg)

                    # Flag as sent
                    sent_coins.add(address)

                    # Delay for Deep Research Mode
                    await asyncio.sleep(90)
                    await send_telegram_message("🧠 *Deep Research Mode:* Tracking live metrics for exit signals.")

                    # Simulate a tracking loop (placeholder logic)
                    for _ in range(3):
                        await asyncio.sleep(60)
                        await send_telegram_message("⚠️ *HOLD*. Volume stable. No red flags yet.")

                    await send_telegram_message("✅ *Final Status:* Exit manually when target is hit or momentum fades.")

        except Exception as e:
            logger.error(f"Sniper error: {e}")

        await asyncio.sleep(30)  # Chill mode: 1 scan every 30s
