# modules/logger.py

import logging
import datetime

logger = logging.getLogger("sniper")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Stream to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def log_alpha_found(token_data):
    symbol = token_data.get("symbol", "Unknown")
    mc = token_data.get("marketCap", 0)
    vol = token_data.get("volume", 0)
    buyers = token_data.get("buyers", 0)
    hype_score = token_data.get("hypeScore", "?")
    smart_wallets = token_data.get("smartWallets", "?")
    social_score = token_data.get("socialScore", "?")

    summary = (
        f"\n🚀 [ALPHA FOUND] {symbol}\n"
        f"📈 MC: ${mc:,} | 💸 Volume: ${vol:,} | 🧠 Smart Wallets: {smart_wallets}\n"
        f"👥 Buyers: {buyers} | 🔥 Hype Score: {hype_score} | 📣 Social Score: {social_score}\n"
        f"⏰ Found at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )

    print(summary)
    logger.info(summary.strip())
