
import requests
import logging

logger = logging.getLogger(__name__)

RUGCHECK_API = "https://api.rugcheck.xyz/solana/"
SOLANAFM_API = "https://api.solana.fm/v0/token/"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "OblivionBot/1.0"
}

def check_rugcheck(contract_address: str) -> dict:
    try:
        url = f"{RUGCHECK_API}{contract_address}"
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            score = data.get("score", "N/A")
            locked = data.get("liquidity", {}).get("locked", False)
            renounced = data.get("ownership", {}).get("renounced", False)
            return {
                "rug_score": score,
                "liquidity_locked": locked,
                "ownership_renounced": renounced
            }
        else:
            logger.warning(f"RugCheck API failed for {contract_address}: {response.status_code}")
            return {"error": f"RugCheck API error: {response.status_code}"}
    except Exception as e:
        logger.error(f"RugCheck error: {e}")
        return {"error": str(e)}

def check_solanafm(contract_address: str) -> dict:
    try:
        url = f"{SOLANAFM_API}{contract_address}"
        response = requests.get(url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            data = response.json()
            token_info = data.get("tokenInfo", {})
            is_verified = token_info.get("isVerified", False)
            creators = token_info.get("creators", [])
            return {
                "is_verified": is_verified,
                "creator_count": len(creators)
            }
        else:
            logger.warning(f"SolanaFM API failed for {contract_address}: {response.status_code}")
            return {"error": f"SolanaFM API error: {response.status_code}"}
    except Exception as e:
        logger.error(f"SolanaFM error: {e}")
        return {"error": str(e)}

def run_contract_checks(contract_address: str) -> dict:
    rug_data = check_rugcheck(contract_address)
    fm_data = check_solanafm(contract_address)

    return {
        "rugcheck": rug_data,
        "solanafm": fm_data
    }
