import asyncio
import websockets
import json

async def listen_for_pairs(callback):
    url = "wss://api.coinhall.org/v1/ws"
    async with websockets.connect(url) as ws:
        await ws.send(json.dumps({
            "type": "subscribe",
            "chain_id": "solana",
            "channel": "pairs"
        }))

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if data.get("type") == "pair_created":
                token_info = {
                    "pair_address": data.get("pair_address"),
                    "token_name": data.get("token0_symbol"),
                    "price": data.get("price_usd"),
                    "volume_1h": data.get("volume_1h"),
                    "market_cap": data.get("market_cap")
                }
                await callback(token_info)
