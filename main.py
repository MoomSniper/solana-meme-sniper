import os
import logging
import asyncio
import httpx
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder
from bs4 import BeautifulSoup

# ENV VARS
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
HELIUS_API = os.getenv("HELIUS_API")
PORT = int(os.getenv("PORT", 10000))

# INIT
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SEND MESSAGE
async def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_ID, "text": text}
    try:
        async with httpx.AsyncClient() as client:
            await client.post(url, json=payload)
    except Exception as e:
        logger.error(f"Telegram error: {e}")

# HELIUS CHECK
async def check_helius(address):
    url = f"https://mainnet.helius-rpc.com/?api-key={HELIUS_API}"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [address, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}, {"encoding": "json"}]
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, json=payload)
            return res.status_code == 200
    except:
        return False

# SCANNER LOOP
async def sniper_loop():
    url = "https://dexscreener.com/solana"
    while True:
        try:
            logger.info("⚡️ Scanning Dexscreener HTML...")
            async with httpx.AsyncClient() as client:
                res = await client.get(url)
            soup = BeautifulSoup(res.text, "html.parser")
            rows = soup.select("a[href^='/solana/']")[:10]  # top 10 new pairs

            for row in rows:
                link = row.get("href", "")
                address = link.split("/")[-1]
                full_link = f"https://dexscreener.com{link}"
                name_tag = row.select_one("div > div > div > div > div")
                name = name_tag.text.strip() if name_tag else "Unknown"

                valid = await check_helius(address)
                if not valid:
                    continue

                msg = (
                    f"🚨 ALPHA FOUND\n\n"
                    f"🪙 {name}\n"
                    f"🔍 Helius check: ✅\n"
                    f"🔗 {full_link}"
                )
                await send_telegram(msg)
                logger.info(msg)

            await asyncio.sleep(30)

        except Exception as e:
            logger.error(f"Scanner error: {e}")
            await asyncio.sleep(30)

# WEBHOOK ENTRYPOINT
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    application.update_queue.put_nowait(Update.de_json(data, application.bot))
    return "OK"

@app.route("/", methods=["GET"])
def index():
    return "Sniper bot active."

# INIT APP + LAUNCH
application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .post_init(lambda _: asyncio.get_event_loop().create_task(sniper_loop()))
    .build()
)

if __name__ == "__main__":
    logger.info("✅ Telegram webhook set.")
    logger.info("🧠 Obsidian Mode active. Scanner running.")
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL,
    )
