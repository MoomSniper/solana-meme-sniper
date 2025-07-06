import os
import requests

HELIUS_API = os.getenv("HELIUS_API")  # Add this key in your env vars

def check_wallet_quality(wallet_address):
    try:
        url = f"https://api.helius.xyz/v0/addresses/{wallet_address}/balances?api-key={HELIUS_API}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        token_count = len(data.get("tokens", []))
        sol_balance = float(data.get("nativeBalance", {}).get("sol", 0))

        score = 0
        if sol_balance >= 0.5:
            score += 1
        if token_count >= 3:
            score += 1

        return score  # 0 = weak wallet, 2 = good wallet

    except Exception as e:
        print(f"[Helius Error] {e}")
        return 0
