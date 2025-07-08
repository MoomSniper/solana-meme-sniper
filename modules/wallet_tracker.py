import requests
import os

HELIUS_API = os.getenv("HELIUS_API")
SMART_WALLET_LABELS = ["airdrop sniper", "meme coin sniper", "influencer", "early buyer", "volume whale"]

def is_smart_wallet(address):
    url = f"https://api.helius.xyz/v0/addresses/{address}/labels?api-key={HELIUS_API}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            labels = res.json()
            for label in labels:
                label_name = label.get("label", "").lower()
                if any(tag in label_name for tag in SMART_WALLET_LABELS):
                    return True
        return False
    except Exception as e:
        print(f"[WalletTracker] Error checking wallet: {e}")
        return False
