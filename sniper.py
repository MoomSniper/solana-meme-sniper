import os
import httpx
import asyncio
import random

TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
BIRDEYE_API = os.getenv("BIRDEYE_API")
birdeye_headers = {"X-API-KEY": BIRDEYE_API}

async def monitor_market(bot):
    while True:
        print("🔍 Scanning market for hot coins...")

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get("https://public-api.birdeye.so/public/pair/all?chain=solana", headers=birdeye_headers)
                pairs = resp.json().get("data", [])

                # Filter coins with decent volume + liquidity
                filtered = [p for p in pairs if float(p.get("volume_h24", 0)) > 10000 and float(p.get("liquidity_usd", 0)) > 5000]

                if not filtered:
                    await bot.send_message(chat_id=TELEGRAM_ID, text="⚠️ No hot coins found right now.")
                else:
                    coin = random.choice(filtered)
                    name = coin.get("name", "Unknown")
                    symbol = coin.get("symbol", "")
                    volume = float(coin.get("volume_h24", 0))
                    liquidity = float(coin.get("liquidity_usd", 0))
                    url = f"https://birdeye.so/token/{coin.get('address')}?chain=solana"

                    msg = f"""
🚨 Hot Coin Spotted
Name: {name} ({symbol})
Volume (24h): ${volume:,.0f}
Liquidity: ${liquidity:,.0f}
Chart: {url}
"""
                    await bot.send_message(chat_id=TELEGRAM_ID, text=msg.strip())

        except Exception as e:
            print(f"❌ Error in monitor_market: {e}")

        await asyncio.sleep(60)
