import asyncio
import logging
import aiohttp
from bs4 import BeautifulSoup
from telegram import Bot
from config import TELEGRAM_ID, BOT_TOKEN

# === Setup ===
logger = logging.getLogger("DEXScraper")
bot = Bot(token=BOT_TOKEN)

DEX_URL = "https://dexscreener.com/solana"
SCAN_INTERVAL = 10  # seconds
sent_tokens = set()

def is_valid_token(name, volume, buyers):
    if not name or "test" in name.lower() or "dev" in name.lower() or "rug" in name.lower():
        return False
    if volume < 3000 or buyers < 10:
        return False
    return True

def parse_token_info(token_block):
    try:
        name_tag = token_block.select_one("a span.token-name")
        name = name_tag.text.strip() if name_tag else "Unknown"

        volume_tag = token_block.select_one("div.volume")
        volume_text = volume_tag.text.strip().replace("$", "").replace(",", "") if volume_tag else "0"
        volume = float(volume_text)

        buyers_tag = token_block.select_one("div.txns")
        buyers_text = buyers_tag.text.strip().split()[0] if buyers_tag else "0"
        buyers = int(buyers_text)

        link_tag = token_block.select_one("a.dapp-link")
        link = "https://dexscreener.com" + link_tag["href"] if link_tag else "N/A"
        address = link.split("/")[-1]

        return {
            "name": name,
            "volume": volume,
            "buyers": buyers,
            "link": link,
            "address": address
        }
    except Exception as e:
        logger.error(f"Parse error: {e}")
        return None

async def send_alert(token):
    try:
        msg = (
            "🚨 *Alpha Alert - DEX Screener*\n"
            f"Name: {token['name']}\n"
            f"Volume: ${token['volume']:,.0f}\n"
            f"Buyers: {token['buyers']}\n"
            f"[DEX Screener]({token['link']})"
        )
        await bot.send_message(chat_id=TELEGRAM_ID, text=msg, parse_mode="Markdown", disable_web_page_preview=False)
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")

async def run_sniper():
    logger.info("🔎 DEX Screener Sniper Live")
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(DEX_URL, timeout=15) as resp:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    blocks = soup.select("div.dapp-trading-pair")

                    for block in blocks:
                        token = parse_token_info(block)
                        if not token:
                            continue
                        logger.info(f"🔍 Scanned token: {token['name']}")

                        if token["address"] in sent_tokens:
                            continue
                        if is_valid_token(token["name"], token["volume"], token["buyers"]):
                            await send_alert(token)
                            sent_tokens.add(token["address"])

        except Exception as e:
            logger.error(f"Scraper error: {e}")

        await asyncio.sleep(SCAN_INTERVAL)
