import asyncio
import httpx
import logging
import os
import random
import time

BIRDEYE_API = os.environ.get("BIRDEYE_API")
TELEGRAM_ID = os.environ.get("TELEGRAM_ID")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TG_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

def send_to_telegram(text):
    try:
        httpx.post(TG_URL, data={"chat_id": TELEGRAM_ID, "text": text})
    except Exception as e:
        logger.error(f"Failed to send message: {e}")

async def fetch_tokens():
    try:
        url = f"https://public-api.birdeye.so/defi/tokenlist?chain=solana"
        headers = {"X-API-KEY": BIRDEYE_API}
        resp = await httpx.AsyncClient().get(url, headers=headers, timeout=10)
        data = resp.json()
        return data.get("data", [])[:3]
    except Exception as e:
        logger.warning(f"Error fetching tokens: {e}")
        return []

def simulate_confidence_score():
    return round(random.uniform(65, 98), 2)

def simulate_hype_score():
    return round(random.uniform(55, 95), 2)

def simulate_exit_signal():
    return random.choice(["HOLD", "PARTIAL TP", "EXIT NOW"])

async def monitor_market():
    logger.info("Starting market monitor...")
    while True:
        tokens = await fetch_tokens()
        for token in tokens:
            try:
                symbol = token.get("symbol", "Unknown")
                address = token.get("address", "")
                confidence = simulate_confidence_score()
                hype = simulate_hype_score()
                exit_decision = simulate_exit_signal()

                msg = (
                    f"🧠 *OBLIVION PHASE 3 DETECTED*\n"
                    f"Token: {symbol}\n"
                    f"Confidence Score: {confidence}%\n"
                    f"Social Hype Score: {hype}/100\n"
                    f"Action: {exit_decision}\n"
                    f"Link: https://birdeye.so/token/{address}?chain=solana"
                )
                send_to_telegram(msg)
                await asyncio.sleep(3)

            except Exception as e:
                logger.error(f"Failed during token eval: {e}")
        logger.info("Scan complete.")
        await asyncio.sleep(10)
