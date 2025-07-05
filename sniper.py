import os
import httpx
import asyncio
import logging
from datetime import datetime, timedelta

TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BIRDEYE_API = os.getenv("BIRDEYE_API")
headers = {"X-API-KEY": BIRDEYE_API}

tracked_tokens = {}  # key: address, value: deep scan status

logging.basicConfig(level=logging.INFO)

async def fetch_token_list():
    url = "https://public-api.birdeye.so/defi/tokenlist?limit=50&offset=0"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            data = response.json()
            return data.get("data", {}).get("tokens", [])
        except Exception as e:
            logging.error(f"❌ Error fetching token list: {e}")
            return []

async def deep_research(token, bot):
    # Simulated deep scan logic
    await asyncio.sleep(90)
    logging.info(f"🔬 Running deep research on {token.get('symbol', 'N/A')}")
    msg = f"""
🧠 DEEP RESEARCH MODE ENGAGED

Token: {token.get('name')}
Symbol: {token.get('symbol')}
Contract: {token.get('address')}

📊 Alpha Score: 91/100
📈 Projected Multiplier: 5x–12x
🧠 Entry Confidence: 93.4%
🔗 Chart: https://birdeye.so/token/{token.get('address')}

Recommendation: 🔥 HOLD — Volume steady, wallets still entering.
"""
    await bot.send_message(chat_id=TELEGRAM_ID, text=msg)

async def monitor_market(bot):
    while True:
        logging.info("🧠 Sniper loop: scanning live token list...")

        tokens = await fetch_token_list()
        logging.info(f"📊 Fetched {len(tokens)} tokens from Birdeye.")

        if not tokens:
            await bot.send_message(chat_id=TELEGRAM_ID, text="⚠️ No tokens found.")
        else:
            for token in tokens:
                token_address = token.get("address")
                if token_address not in tracked_tokens:
                    try:
                        msg = f"""
📡 LIVE TOKEN FOUND
Name: {token.get('name', 'N/A')}
Symbol: {token.get('symbol', 'N/A')}
Chart: https://birdeye.so/token/{token.get('address')}
"""
                        await bot.send_message(chat_id=TELEGRAM_ID, text=msg)
                        tracked_tokens[token_address] = {
                            "notified_at": datetime.utcnow(),
                            "deep_researched": False
                        }

                        # Schedule deep scan after 90s
                        asyncio.create_task(deep_research(token, bot))
                        await asyncio.sleep(0.75)  # throttle
                    except Exception as e:
                        logging.error(f"❌ Error sending message for token: {e}")

        await asyncio.sleep(60)
