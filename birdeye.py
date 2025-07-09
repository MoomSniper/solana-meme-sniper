import requests
import os

BIRDEYE_API = os.getenv("BIRDEYE_API")

def get_top_coins(limit=50):
    url = f"https://public-api.birdeye.so/public/tokenlist?sort_by=volume_24h_usd&order=desc&limit={limit}&offset=0"
    headers = {"X-API-KEY": BIRDEYE_API}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        print(f"[Birdeye API ERROR] {e}")
        return []
