def calculate_alpha_score(data, wallet_score, rug_score, social_score):
    score = 0

    # Volume
    if 5000 <= data["volume"] <= 300000:
        score += 30

    # Buyers
    if 10 <= data["buyers"] <= 150:
        score += 20

    # Market Cap
    if data["mc"] and data["mc"] < 300000:
        score += 20

    # Smart Wallets
    score += wallet_score  # up to +10

    # Contract Safety
    score += rug_score  # up to +10

    # Social Hype
    score += social_score  # up to +10

    return score
