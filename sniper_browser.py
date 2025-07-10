import asyncio
import logging
import json
import httpx
from playwright.async_api import async_playwright
from telegram import Bot
from config import TELEGRAM_ID, BOT_TOKEN

# Setup logging
logger = logging.getLogger("BrowserSniper")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

bot = Bot(token=BOT_TOKEN)
sent_tokens = set()
DEX_URL = "https://dexscreener.com/solana"

# Optional: API poller to show initial top 5 tokens by volume
async def poll_dexscreener_api():
    print("📡 Polling Dexscreener API...")

    url = "https://api.dexscreener.com/latest/dex/search/?q=sol"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

        if response.status_code != 200:
            print(f"❌ API request failed: {response.status_code}")
            return

        try:
            data = response.json()
            for pair in data.get("pairs", [])[:5]:
                name = pair["baseToken"]["name"]
                price = pair["priceUsd"]
                volume = pair["volume"]["h1"]
                print(f"{name} — ${price} | 1h Vol: ${volume}")
        except Exception as e:
            print(f"❌ Failed to parse API response: {e}")

# Main sniper that hooks into browser WebSocket
async def run_browser_sniper():
    print("🚀 Launching sniper browser...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        logger.info("🌐 Opening Dexscreener frontend...")
        await page.goto(DEX_URL, wait_until='networkidle')

        logger.info("🧠 Hooking into WebSocket...")

        async def handle_ws(ws):
            async def on_msg(msg):
                try:
                    data = json.loads(msg)
                    if data.get("type") != "pairs":
                        return

                    for pair in data["pairs"]:
                        address = pair.get("pairAddress")
                        if not address or address in sent_tokens:
                            continue

                        sent_tokens.add(address)
                        name = pair.get("baseTokenName")
                        price = pair.get("priceUsd")
                        vol = pair.get("volume", {}).get("h24")

                        text = (
                            f"🚨 *Live Token Detected!*\n"
                            f"Name: {name}\n"
                            f"Price: ${price}\n"
                            f"24h Volume: ${vol}"
                        )

                        await bot.send_message(chat_id=TELEGRAM_ID, text=text, parse_mode="Markdown")
                        logger.info(f"📤 Sent: {name}")

                except Exception as e:
                    logger.warning(f"❌ Message parse failed: {e}")

            ws.on("framereceived", lambda frame: asyncio.create_task(on_msg(frame.payload.decode())))

        context.on("websocket", handle_ws)

        logger.info("✅ Sniper live. Monitoring for new tokens...")
        await asyncio.sleep(999999)

# Entry point
if __name__ == "__main__":
    asyncio.run(run_browser_sniper())
