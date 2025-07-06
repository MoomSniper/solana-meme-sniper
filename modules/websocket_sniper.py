import asyncio
import websockets
import json
import logging
from sniper import process_token_from_websocket

BIRDEYE_WS_URL = "wss://birdeye-api-v1.deno.dev/ws"

async def listen_for_new_tokens():
    try:
        async with websockets.connect(BIRDEYE_WS_URL) as websocket:
            logging.info("🟢 [Birdeye WS] Connected to WebSocket")
            await websocket.send(json.dumps({
                "type": "subscribe",
                "channel": "new_token",
                "network": "solana"
            }))

            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data.get("type") == "new_token":
                        token_info = data.get("data", {})
                        address = token_info.get("address")
                        if address:
                            logging.info(f"🚀 [Birdeye WS] New token detected: {address}")
                            await process_token_from_websocket(address)
                except Exception as e:
                    logging.warning(f"⚠️ [Birdeye WS] Error in message loop: {e}")
                    await asyncio.sleep(2)
    except Exception as e:
        logging.error(f"❌ [Birdeye WS] Connection failed: {e}")
        await asyncio.sleep(10)
        await listen_for_new_tokens()

def start_websocket_sniper():
    loop = asyncio.get_event_loop()
    loop.create_task(listen_for_new_tokens())
