def predict_multiplier(hype_score: int, smart_wallets: int, liquidity_locked: bool) -> float:
    """
    Predicts the potential multiplier of a token.
    """
    multiplier = 1.0

    if hype_score > 85:
        multiplier += 1.5
    elif hype_score > 70:
        multiplier += 1.0
    elif hype_score > 55:
        multiplier += 0.5

    if smart_wallets >= 5:
        multiplier += 1.0
    elif smart_wallets >= 2:
        multiplier += 0.5

    if liquidity_locked:
        multiplier += 0.5
    else:
        multiplier -= 1.0

    return round(multiplier, 2)


def predict_risk(hype_score: int, contract_risk_score: int, bot_ratio: float) -> str:
    """
    Returns risk level: Low / Medium / High
    """
    risk_score = 0

    if hype_score < 50:
        risk_score += 1
    if contract_risk_score > 5:
        risk_score += 2
    if bot_ratio > 0.4:
        risk_score += 2
    elif bot_ratio > 0.25:
        risk_score += 1

    if risk_score <= 1:
        return "Low"
    elif risk_score == 2:
        return "Medium"
    else:
        return "High"
