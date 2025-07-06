import requests

def run_rug_check(token_address):
    url = f"https://api.rugcheck.xyz/solana/token/{token_address}"
    try:
        res = requests.get(url)
        data = res.json()
        return {
            "score": data.get("score", 0),
            "is_rug": data.get("is_rug", True),
            "details": data.get("reasons", [])
        }
    except:
        return {"score": 0, "is_rug": True, "details": ["API failed"]}
