import requests
import os

HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

def check_wallet_quality(wallet_address):
    url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/transactions?api-key={HELIUS_API_KEY}"
    res = requests.get(url)

    if res.status_code != 200:
        return {"score": 0, "reason": "API error"}

    txs = res.json()
    age_score = len(txs)
    smart = age_score > 50

    return {
        "score": min(100, age_score),
        "is_smart_money": smart,
        "tx_count": age_score
    }
