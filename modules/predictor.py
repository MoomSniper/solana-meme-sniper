# modules/predictor.py

import random

def predict_multiplier(hype_score, smart_wallets, contract_score, volume):
    """Predicts potential multiplier based on current signals"""
    base = 1.0

    # Weight social hype
    if hype_score > 90:
        base += 2.0
    elif hype_score > 80:
        base += 1.5
    elif hype_score > 70:
        base += 1.2
    else:
        base += 0.8

    # Weight smart wallets
    if smart_wallets >= 5:
        base += 1.8
    elif smart_wallets >= 3:
        base += 1.3
    elif smart_wallets >= 1:
        base += 0.7

    # Weight contract safety
    if contract_score == "A":
        base += 1.5
    elif contract_score == "B":
        base += 1.0
    elif contract_score == "C":
        base += 0.5
    else:
        base -= 1.0

    # Weight volume
    if volume > 50000:
        base += 1.5
    elif volume > 25000:
        base += 1.0
    elif volume > 10000:
        base += 0.5
    else:
        base -= 0.5

    # Add noise to simulate variance
    noise = random.uniform(0.1, 0.4)
    prediction = round(base + noise, 2)

    # Clamp to realistic floor/ceiling
    return max(1.0, min(prediction, 30.0))


def estimate_risk(contract_score, social_bot_percent):
    """Estimates coin risk level"""
    risk = 0

    if contract_score in ["C", "D"]:
        risk += 2
    elif contract_score == "B":
        risk += 1

    if social_bot_percent > 60:
        risk += 2
    elif social_bot_percent > 30:
        risk += 1

    if risk >= 3:
        return "HIGH"
    elif risk == 2:
        return "MEDIUM"
    else:
        return "LOW"
