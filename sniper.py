import httpx
import time
import asyncio

BIRDEYE_API = "8ecb4290bb4d485aae3b9a89b116eeb3"
headers = {
    "X-API-KEY": BIRDEYE_API
}

async def fetch_token_list():
    url = "https://public-api.birdeye.so/defi/market/most_traded?limit=100&offset=0&dex=all&chain=solana"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        data = response.json()
        tokens = data.get("data", [])

        # Sniper-grade filters
        filtered = []
        for token in tokens:
            mcap = token.get("mcap", 0)
            volume = token.get("volume_1h", 0)
            txns = token.get("txns_1h", 0)
            symbol = token.get("symbol", "")

            if (
                mcap > 5_000 and mcap < 300_000 and
                volume > 10_000 and
                txns >= 20 and
                symbol.upper() not in ["SOL", "USDC", "BONK", "RAY", "USDT"]
            ):
                filtered.append(token)

        return filtered

async def sniper_loop():
    print("🧠 Oblivion Mode Sniper is scanning for alpha coins...")
    while True:
        try:
            tokens = await fetch_token_list()
            print(f"📊 Alpha Candidates Found: {len(tokens)}")
            for t in tokens:
                print(f"🚀 {t.get('symbol')} — MC: {t.get('mcap')} — 1h Vol: {t.get('volume_1h')} — TXNs: {t.get('txns_1h')}")

            await asyncio.sleep(3)
        except Exception as e:
            print(f"[ERROR] {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(sniper_loop())
