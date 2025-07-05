import os
import asyncio
import httpx
import time

BOT_TOKEN = os.environ['BOT_TOKEN']
TELEGRAM_ID = int(os.environ['TELEGRAM_ID'])
BIRDEYE_API = os.environ['BIRDEYE_API']

HEADERS = {"X-API-KEY": BIRDEYE_API}
BASE_URL = "https://public-api.birdeye.so/public/tokenlist?sort_by=volume_1h&sort_type=desc&dex=JUPITER&chain=solana"

last_alerted = set()

async def send_telegram_message(text: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_ID, "text": text, "parse_mode": "HTML"}
        )

def passes_filters(token):
    try:
        mc = float(token.get("market_cap", 0))
        vol = float(token.get("volume_1h", 0))
        buyers = int(token.get("tx_count_1h", 0))
        symbol = token.get("symbol", "")

        return (
            mc < 300000
            and vol > 5000
            and buyers >= 15
            and symbol not in last_alerted
        )
    except:
        return False

async def fetch_tokens():
    async with httpx.AsyncClient() as client:
        resp = await client.get(BASE_URL, headers=HEADERS)
        return resp.json().get("data", [])

async def sniper_loop():
    while True:
        try:
            tokens = await fetch_tokens()
            for token in tokens:
                if passes_filters(token):
                    symbol = token["symbol"]
                    name = token["name"]
                    mc = token.get("market_cap", 0)
                    vol = token.get("volume_1h", 0)
                    buyers = token.get("tx_count_1h", 0)
                    address = token["address"]

                    msg = (
                        f"<b>🚨 ALPHA FOUND</b>\n"
                        f"<b>Name:</b> {name} ({symbol})\n"
                        f"<b>Market Cap:</b> ${int(mc):,}\n"
                        f"<b>1h Volume:</b> ${int(vol):,}\n"
                        f"<b>1h Buyers:</b> {buyers}\n"
                        f"<b>Chart:</b> https://birdeye.so/token/{address}?chain=solana"
                    )
                    await send_telegram_message(msg)
                    last_alerted.add(symbol)

            await asyncio.sleep(6)
        except Exception as e:
            print(f"Error in sniper_loop: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(sniper_loop())
