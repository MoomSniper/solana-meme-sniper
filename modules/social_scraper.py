import aiohttp
import re
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# === Utility ===
def extract_mentions(text):
    hashtags = re.findall(r"#\w+", text)
    return hashtags

def is_organic(text):
    # Basic filter for botted spam
    suspicious_keywords = ["airdrops", "giveaway", "claim now", "retweet to win"]
    return not any(keyword.lower() in text.lower() for keyword in suspicious_keywords)

# === Social Scraper ===
async def scrape_twitter_x(session, coin_name):
    try:
        query = f"{coin_name} crypto"
        url = f"https://nitter.net/search?f=tweets&q={query}&since=&until=&near="  # Nitter is a lightweight Twitter frontend

        async with session.get(url, timeout=10) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            tweets = soup.find_all("div", class_="tweet-content")
            mentions = []
            count = 0

            for tweet in tweets:
                text = tweet.get_text().strip()
                if is_organic(text):
                    mentions.extend(extract_mentions(text))
                    count += 1

            score = min(count * 10, 100)
            return {"platform": "twitter", "mentions": list(set(mentions)), "score": score, "raw_count": count}

    except Exception as e:
        logger.error(f"❌ Twitter scrape failed: {e}")
        return {"platform": "twitter", "mentions": [], "score": 0, "raw_count": 0}

async def scrape_telegram(session, token_symbol):
    try:
        query = token_symbol.lower()
        url = f"https://t.me/s/{query}"

        async with session.get(url, timeout=10) as response:
            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            posts = soup.find_all("div", class_="tgme_widget_message_text")
            count = len(posts)

            score = min(count * 5, 100)
            return {"platform": "telegram", "score": score, "raw_count": count}

    except Exception as e:
        logger.error(f"❌ Telegram scrape failed: {e}")
        return {"platform": "telegram", "score": 0, "raw_count": 0}

# === Combined Social Hype Check ===
async def get_social_score(token_name, token_symbol):
    try:
        async with aiohttp.ClientSession() as session:
            twitter_task = scrape_twitter_x(session, token_name)
            telegram_task = scrape_telegram(session, token_symbol)

            twitter, telegram = await asyncio.gather(twitter_task, telegram_task)
            combined_score = round((twitter["score"] + telegram["score"]) / 2)

            return {
                "score": combined_score,
                "details": {
                    "twitter": twitter,
                    "telegram": telegram
                }
            }
    except Exception as e:
        logger.error(f"❌ Social score failed: {e}")
        return {"score": 0, "details": {}}
