import random

def evaluate_alpha(token_data):
    score = 0
    reasons = []

    # Price filter
    price = token_data.get("price", 0)
    if 0.00001 <= price <= 0.1:
        score += 15
        reasons.append("✅ Price in snipe range")
    else:
        reasons.append("❌ Price out of range")

    # Market Cap
    market_cap = token_data.get("market_cap", 0)
    if market_cap and market_cap <= 500000:
        score += 20
        reasons.append("✅ MC under 500K")
    else:
        reasons.append("❌ MC too high")

    # Volume
    volume = token_data.get("volume", 0)
    if volume >= 10000:
        score += 20
        reasons.append("✅ Good volume")
    else:
        reasons.append("❌ Weak volume")

    # Buyers vs Sellers
    buyers = token_data.get("buyers", 0)
    sellers = token_data.get("sellers", 0)
    if buyers > sellers:
        score += 15
        reasons.append("✅ Buyer pressure")
    else:
        reasons.append("❌ Seller pressure")

    # Liquidity lock (mocked here)
    if token_data.get("liquidity_locked", True):
        score += 10
        reasons.append("✅ Liquidity locked")
    else:
        reasons.append("❌ Unlocked liquidity")

    # Simulated hype score (to be replaced with real scraping)
    social_score = random.randint(0, 20)
    score += social_score
    reasons.append(f"🔍 Hype factor: {social_score}/20")

    return score, reasons
