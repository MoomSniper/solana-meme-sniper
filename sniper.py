import os
import httpx
import asyncio
import logging

# Setup
logging.basicConfig(level=logging.INFO)
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BIRDEYE_API = os.getenv("BIRDEYE_API")
headers = {"X-API-KEY": BIRDEYE_API}

# --- Advanced Alpha Filter Config ---
MIN_VOLUME = 5000  # Minimum 1h volume
MAX_MARKETCAP = 300000  # Max MC
MIN_TRADERS = 15  # Unique traders

# --- Token Fetching ---
async def fetch_token_list():
    url = "https://public-api.birdeye.so/defi/tokenlist?limit=100&offset=0"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        data = response.json()
        return data.get("data", {}).get("tokens", [])

# --- Token Deep Check ---
async def fetch_token_details(address):
    url = f"https://public-api.birdeye.so/defi/token/latest/token_info?address={address}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        data = response.json()
        return data.get("data", {})

# --- Sniper Market Monitor ---
async def monitor_market(bot):
    while True:
        logging.info("🧠 Sniper loop: scanning live token list...")
        try:
            tokens = await fetch_token_list()
            logging.info(f"📊 Fetched {len(tokens)} tokens from Birdeye.")
        except Exception as e:
            await bot.send_message(chat_id=TELEGRAM_ID, text=f"❌ Error fetching token list: {e}")
            logging.error(f"Token fetch error: {e}")
            await asyncio.sleep(60)
            continue

        for token in tokens:
            try:
                address = token.get("address")
                info = await fetch_token_details(address)
                volume = info.get("volume_h1", 0)
                market_cap = info.get("market_cap", 0)
                traders = info.get("unique_traders", 0)

                if volume >= MIN_VOLUME and market_cap <= MAX_MARKETCAP and traders >= MIN_TRADERS:
                    msg = f"""
🚨 ALPHA COIN DETECTED
Name: {token.get('name', 'N/A')}
Symbol: {token.get('symbol', 'N/A')}
Volume (1h): ${int(volume):,}
Market Cap: ${int(market_cap):,}
Traders: {traders}
Chart: https://birdeye.so/token/{address}
"""
                    await bot.send_message(chat_id=TELEGRAM_ID, text=msg)
                    await asyncio.sleep(1)
            except Exception as e:
                logging.error(f"Error processing token: {e}")

        await asyncio.sleep(60)
