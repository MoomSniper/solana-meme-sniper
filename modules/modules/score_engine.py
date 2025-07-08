def calculate_alpha_score(volume_usd: float, buyers: int, hype_score: int, smart_wallets: int, contract_safety: bool) -> float:
    """
    Computes alpha score for a token based on volume, buyers, social traction, wallets, and safety.
    """

    score = 0

    # Volume weighting
    if volume_usd >= 10000:
        score += 25
    elif volume_usd >= 5000:
        score += 15
    elif volume_usd >= 2000:
        score += 10

    # Buyer activity
    if buyers >= 25:
        score += 20
    elif buyers >= 15:
        score += 15
    elif buyers >= 5:
        score += 10

    # Hype influence
    if hype_score >= 85:
        score += 25
    elif hype_score >= 70:
        score += 15
    elif hype_score >= 50:
        score += 10

    # Smart wallet boost
    if smart_wallets >= 5:
        score += 20
    elif smart_wallets >= 2:
        score += 10

    # Contract safety bonus
    if contract_safety:
        score += 10

    return min(round(score, 2), 100.0)
