import os
import time
import httpx
import asyncio
import logging
import json
import websockets
from datetime import datetime
from telegram import Bot
from modules.alpha_scoring import calculate_alpha_score
from modules.exit_logic import analyze_exit
from modules.deep_research import deep_research
from modules.wallet_scan import check_smart_wallets
from modules.social_check import assess_social_hype
from modules.contract_check import contract_risk_check

# === ENV ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")
DEEP_DELAY = 90  # seconds after alert before deep research
bot = Bot(token=BOT_TOKEN)

seen_tokens = {}
CHECK_INTERVAL = 2
SEEN_TIMEOUT = 3600  # seconds

# === Logging ===
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("sniper")

def format_alert(data, score):
    return (
        f"🚨 <b>ALPHA [{score}%]</b>\n"
        f"<b>{data['name']} ({data['symbol']})</b>\n"
        f"MC: ${data['mc']:,}\n"
        f"Vol (1h): ${data['volume']:,}\n"
        f"Buys (1h): {data['buyers']}\n"
        f"<a href='{data['url']}'>Chart</a>"
    )

async def handle_token(token):
    address = token.get("id")
    if not address or address in seen_tokens:
        return

    name = token.get("baseToken", {}).get("name", "")
    symbol = token.get("baseToken", {}).get("symbol", "")
    mc = float(token.get("fdv") or 0)
    volume = float(token.get("volume", {}).get("h1", 0))
    buyers = int(token.get("txns", {}).get("h1", {}).get("buys", 0))
    url = token.get("url", "")

    data = {
        "name": name,
        "symbol": symbol,
        "mc": mc,
        "volume": volume,
        "buyers": buyers,
        "url": url,
        "address": address
    }

    wallet_score = check_smart_wallets(address)
    rug_score = contract_risk_check(address)
    social_score = assess_social_hype(name, symbol)

    alpha_score = calculate_alpha_score(data, wallet_score, rug_score, social_score)

    if alpha_score >= 85:
        msg = format_alert(data, alpha_score)
        await bot.send_message(chat_id=TELEGRAM_ID, text=msg, parse_mode="HTML")
        seen_tokens[address] = time.time()
        log.info(f"📡 Alpha: {symbol} {alpha_score}%")

        asyncio.create_task(schedule_deep_check(data, wallet_score, rug_score, social_score))

async def schedule_deep_check(data, wallet_score, rug_score, social_score):
    await asyncio.sleep(DEEP_DELAY)
    try:
        result = await deep_research(data, wallet_score, rug_score, social_score)
        await bot.send_message(chat_id=TELEGRAM_ID, text=result, parse_mode="HTML")
        log.info(f"🔍 Research complete: {data['symbol']}")
        await monitor_exit(data["address"])
    except Exception as e:
        log.warning(f"[Research Error] {e}")

async def monitor_exit(address):
    prev_volume = None
    while True:
        await asyncio.sleep(20)
        try:
            async with httpx.AsyncClient() as client:
                url = f"https://public-api.coinhall.org/api/v1/swap/pair/{address}"
                r = await client.get(url)
                token = r.json().get("pair", {})
                if not token:
                    break

                volume = float(token.get("volume", {}).get("h1", 0))
                whale_exit = check_smart_wallets(address)["exited"]

                decision = analyze_exit(volume, prev_volume or volume, whale_exit)
                if decision != "HOLD":
                    await bot.send_message(chat_id=TELEGRAM_ID, text=f"⚠️ {decision} on {token.get('baseToken', {}).get('symbol')}")
                    break

                prev_volume = volume
        except Exception as e:
            log.warning(f"[Exit Monitor Error] {e}")
            break

async def start_coinhall_ws():
    uri = "wss://api.dexscreener.com/ws"  # Placeholder WebSocket URL
    async with websockets.connect(uri) as ws:
        log.info("🧠 Obsidian Sniper listening on Coinhall WS.")
        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=30)
                data = json.loads(msg)

                if isinstance(data, dict) and "pair" in data:
                    token = data["pair"]
                    await handle_token(token)

                now = time.time()
                for addr in list(seen_tokens.keys()):
                    if now - seen_tokens[addr] > SEEN_TIMEOUT:
                        del seen_tokens[addr]

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                log.error(f"[WebSocket Error] {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(start_coinhall_ws())
