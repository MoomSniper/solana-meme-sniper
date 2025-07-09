import asyncio
import websockets
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebSocketSniper")

COINHALL_WS_URL = "wss://stream.coinhall.org/socket.io/?EIO=4&transport=websocket"

async def listen():
    async with websockets.connect(COINHALL_WS_URL) as ws:
        logger.info("✅ Connected to Coinhall WebSocket")
        
        await ws.send('40')  # WebSocket handshake

        while True:
            try:
                message = await ws.recv()
                if message.startswith("42"):
                    payload = message[2:]
                    data = json.loads(payload)
                    
                    if isinstance(data, list) and len(data) > 1:
                        event_type = data[0]
                        if event_type == "pair:new":
                            token_info = data[1]
                            logger.info(f"🚨 New token detected: {token_info}")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(listen())
