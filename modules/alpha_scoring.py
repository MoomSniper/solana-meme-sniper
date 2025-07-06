def calculate_alpha_score(token_data, wallet_score, rug_score, social_score):
    total = (
        (token_data["volume_1h"] / 1000) * 0.2 +
        wallet_score["score"] * 0.3 +
        (100 - rug_score["score"]) * 0.2 +
        social_score * 0.3
    )

    confidence = min(100, round(total, 2))
    return confidence
