import re
import logging
import random

logger = logging.getLogger("social")

# === Simulated Lightweight Social Scraper ===
def scrape_social_hype(token_symbol, token_name):
    try:
        logger.info(f"[SOCIAL] Scraping X/Telegram for {token_symbol}...")

        # Simulated results (randomized for now — upgrade with real API later)
        telegram_mentions = random.randint(50, 500)
        twitter_mentions = random.randint(80, 700)
        bot_ratio = random.uniform(0.05, 0.3)  # % of suspected bots

        total_mentions = telegram_mentions + twitter_mentions
        real_engagement = int(total_mentions * (1 - bot_ratio))

        # Hype Score (basic)
        score = 0
        if real_engagement > 300:
            score += 40
        elif real_engagement > 150:
            score += 25
        else:
            score += 10

        if bot_ratio < 0.1:
            score += 30
        elif bot_ratio < 0.2:
            score += 20

        logger.info(f"[SOCIAL] Real Mentions: {real_engagement}, Bot %: {round(bot_ratio*100, 1)}%")

        return {
            "score": score,
            "real_mentions": real_engagement,
            "bot_percent": round(bot_ratio * 100, 1),
            "telegram": telegram_mentions,
            "twitter": twitter_mentions
        }

    except Exception as e:
        logger.warning(f"[SOCIAL ERROR] {e}")
        return {
            "score": 0,
            "real_mentions": 0,
            "bot_percent": 100.0,
            "telegram": 0,
            "twitter": 0
        }
