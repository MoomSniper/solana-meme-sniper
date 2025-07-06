import asyncio
import logging
import httpx
import json
from datetime import datetime
from pytz import timezone
from modules.alpha_filters import is_high_potential_token
from modules.logger import log_alpha_found
from modules.solana_tracker import fetch_token_data
from modules.telegram_engine import send_telegram_alert
from websockets import connect

# Timezone setup
eastern = timezone('US/Eastern')

# Config
BIRDEYE_WS = "wss://public-api.birdeye.so/ws"
WATCHED_TOKENS = set()

async def handle_birdeye_stream():
    async with connect(BIRDEYE_WS) as ws:
        subscribe_payload = json.dumps({
            "type": "subscribe_new_pairs",
            "network": "solana"
        })
        await ws.send(subscribe_payload)
        logging.info("✅ [WebSocket] Subscribed to new Solana pairs")

        while True:
            try:
                raw_msg = await ws.recv()
                data = json.loads(raw_msg)

                if data.get("type") == "pair_created":
                    token_info = data.get("pair", {})
                    token_address = token_info.get("address")
                    token_name = token_info.get("name")
                    token_symbol = token_info.get("symbol")

                    if token_address in WATCHED_TOKENS:
                        continue
                    WATCHED_TOKENS.add(token_address)

                    logging.info(f"🆕 New Token Detected: {token_name} ({token_symbol})")

                    # Fetch metadata from Solana Tracker
                    token_data = await fetch_token_data(token_address)
                    if not token_data:
                        logging.warning(f"⚠️ No token data found for {token_address}")
                        continue

                    # Run sniper-grade filters
                    is_alpha, alpha_score = is_high_potential_token(token_data)
                    if is_alpha:
                        logging.info(f"💥 ALPHA FOUND: {token_name} ({token_symbol}) | Score: {alpha_score}")
                        log_alpha_found(token_data, alpha_score)
                        await send_telegram_alert(token_data, alpha_score)

                await asyncio.sleep(0.01)  # keep loop tight but not overwhelming
            except Exception as e:
                logging.error(f"❌ [WebSocket Error] {e}")
                await asyncio.sleep(3)

async def scan_and_score_market():
    # Not used now — replaced by websocket scanner for live coins
    logging.info("⚠️ Obsidian Mode only uses WebSocket scanner now.")
    return

def start_sniper():
    now = datetime.now(eastern)
    if 7 <= now.hour < 24:
        logging.info("🚀 Sniper is live — Obsidian Mode active")
        asyncio.run(handle_birdeye_stream())
    else:
        logging.info("💤 Sleeping hours (12am–7am) — sniper paused")
