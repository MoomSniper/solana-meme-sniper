import os
import requests

def run_rug_check(contract_address):
    try:
        api_key = os.getenv("RUGCHECK_API")  # You must also add this to Render
        url = f"https://api.rugcheck.xyz/check/{contract_address}"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        if data.get("rug_score", 0) >= 80:
            return True
        return False

    except Exception as e:
        print(f"[RugCheck Error] {e}")
        return False
