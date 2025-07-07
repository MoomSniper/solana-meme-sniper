import os
import logging
import httpx
import asyncio
from bs4 import BeautifulSoup
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder
import re

# Init logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ENV
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Flask app
app = Flask(__name__)

# Send Telegram message
async def send_telegram_message(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_ID, "text": text}
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload)
    except Exception as e:
        logger.error(f"❌ Telegram send failed: {e}")

# Main Obsidian Scanner Loop
async def scan_dexscreener():
    url = "https://dexscreener.com/solana"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/114.0.0.0 Safari/537.36"
        )
    }

    while True:
        try:
            logger.info("⚡️ Scanning Dexscreener HTML...")
            async with httpx.AsyncClient() as client:
                res = await client.get(url, headers=headers)
                soup = BeautifulSoup(res.text, "html.parser")

            rows = soup.find_all("a", href=re.compile("^/solana/"))
            for row in rows:
                name_tag = row.find("h3")
                if not name_tag:
                    continue

                name = name_tag.text.strip()
                info = row.find_all("span")
                mc, vol, txns = 0, 0, 0

                for span in info:
                    text = span.text.lower()
                    if "mc" in text:
                        mc = parse_number(text)
                    elif "volume" in text:
                        vol = parse_number(text)
                    elif "txns" in text:
                        txns = parse_number(text)

                if mc < 300_000 and vol > 5_000 and txns > 15:
                    address = row["href"].split("/")[-1]
                    msg = (
                        f"🚨 ALPHA FOUND\n\n"
                        f"🪙 {name}\n"
                        f"💰 MC: ${mc:,.0f}\n"
                        f"📈 Vol (1h): ${vol:,.0f}\n"
                        f"🛒 Txns: {txns}\n"
                        f"🔗 https://dexscreener.com/solana/{address}"
                    )
                    logger.info(msg)
                    await send_telegram_message(msg)

            await asyncio.sleep(44)

        except Exception as e:
            logger.error(f"❌ Scanner error: {e}")
            await asyncio.sleep(44)

# Parse shorthand numbers like $8.3K
def parse_number(text):
    try:
        num = re.findall(r"\$?([\d,.]+)([kKmMbB]?)", text)
        if not num:
            return 0
        base, suffix = num[0]
        base = float(base.replace(",", ""))
        if suffix.lower() == "k":
            return int(base * 1_000)
        if suffix.lower() == "m":
            return int(base * 1_000_000)
        return int(base)
    except:
        return 0

# /start is not used – removed for Obsidian++
# Flask Index
@app.route("/", methods=["GET"])
def index():
    return "Obsidian Sniper is live."

# Flask Webhook
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    logger.info(f"📥 Incoming Telegram update: {data}")
    return "OK"

# Init Telegram app and scanner
application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .post_init(lambda app: asyncio.get_event_loop().create_task(scan_dexscreener()))
    .build()
)

# Start App
if __name__ == "__main__":
    logger.info("✅ Telegram webhook set.")
    logger.info("🧠 Obsidian Mode active. Scanner running.")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 10000)),
        webhook_url=WEBHOOK_URL,
    )
