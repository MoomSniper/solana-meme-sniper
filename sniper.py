import requests
import time
from datetime import datetime
from telegram import Bot
import logging

TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
TELEGRAM_ID = 'YOUR_TELEGRAM_USER_ID'
bot = Bot(token=TELEGRAM_TOKEN)

logging.basicConfig(level=logging.INFO)

def get_live_data():
    url = "https://api.dexscreener.com/latest/dex/pairs/solana"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()['pairs']
    except Exception as e:
        logging.error(f"Error getting live data: {e}")
    return []

def is_alpha(pair):
    try:
        mc = float(pair.get('fdv') or 0)
        volume = float(pair.get('volume', {}).get('h1', 0))
        buyers = int(pair.get('txns', {}).get('h1', {}).get('buys', 0))
        sells = int(pair.get('txns', {}).get('h1', {}).get('sells', 0))
        liq = float(pair.get('liquidity', {}).get('usd', 0))

        if mc < 5000 or mc > 300000:
            return False
        if volume < 3000:
            return False
        if buyers < 15:
            return False
        if sells == 0 or (buyers / sells) < 1.5:
            return False
        if liq < 0.05 * mc:
            return False
        return True
    except Exception as e:
        logging.error(f"Filter error: {e}")
        return False

def format_message(pair):
    return (
        f"🚨 *ALPHA ALERT* 🚨\n"
        f"🪙 Token: {pair['baseToken']['name']} ({pair['baseToken']['symbol']})\n"
        f"📊 MC: ${round(float(pair.get('fdv') or 0))}\n"
        f"💧 Liquidity: ${round(float(pair['liquidity']['usd']))}\n"
        f"📈 1H Volume: ${round(float(pair['volume']['h1']))}\n"
        f"🛒 Buyers: {pair['txns']['h1']['buys']} | Sellers: {pair['txns']['h1']['sells']}\n"
        f"🔗 [Dexscreener]({pair['url']})"
    )

def main_loop():
    seen = set()
    while True:
        pairs = get_live_data()
        for pair in pairs:
            if pair['pairAddress'] not in seen and is_alpha(pair):
                seen.add(pair['pairAddress'])
                message = format_message(pair)
                bot.send_message(chat_id=TELEGRAM_ID, text=message, parse_mode='Markdown')
                logging.info(f"ALPHA SENT: {pair['baseToken']['symbol']}")
        time.sleep(3)

if __name__ == "__main__":
    main_loop()
