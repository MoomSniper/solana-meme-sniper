# modules/alpha_filters.py

def is_high_potential_token(token_data):
    """
    Godest-level filter for Solana meme coins likely to 2.5–25x+.
    Combines market, volume, wallet behavior, and social trigger proxies.
    """

    try:
        if not token_data:
            return False

        # Basic essentials
        mc = token_data.get("marketCap", 0)
        vol = token_data.get("volume", 0)
        buyers = token_data.get("buyers", 0)
        holders = token_data.get("holders", 0)
        telegram_members = token_data.get("telegramMembers", 0)
        twitter_followers = token_data.get("twitterFollowers", 0)
        smart_wallets = token_data.get("smartWallets", 0)
        score = 0

        # Filter 1: Market Cap sweet spot for 10x flips
        if 8000 < mc < 275000:
            score += 1

        # Filter 2: Real trading momentum
        if vol > 7500:
            score += 1

        # Filter 3: Early entry signs (at least 15 real buyers, not just whales)
        if buyers >= 14:
            score += 1

        # Filter 4: Community ignition
        if telegram_members > 300 or twitter_followers > 500:
            score += 1

        # Filter 5: Holder spread looks natural
        if 20 <= holders <= 800:
            score += 1

        # Filter 6: Smart wallets detected (optional but powerful)
        if smart_wallets >= 2:
            score += 1

        # Godest rule: minimum threshold of 4 triggers to pass
        return score >= 4

    except Exception as e:
        print(f"[AlphaFilter Error] {e}")
        return False
