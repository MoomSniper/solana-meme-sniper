# config.py — Obsidian Mode Config

BIRDEYE_API = "6bda2c7ab409427f8632ad6c244d55e4"
HELIUS_API = "e61da153-6986-43c3-b19f-38099c1e335a"

BOT_TOKEN = "8086252105:AAF-_xAzlorVkq-Lq9mGP2lLA99dRYj12BQ"
TELEGRAM_ID = "6881063420"

# Scanner logic
MIN_VOLUME = 5000  # USD
MAX_MARKET_CAP = 300000  # USD
MIN_SCORE = 85  # Alpha score threshold

# Alert filtering
REQUIRED_TELEGRAM_MEMBERS = 150
REQUIRED_TWITTER_FOLLOWERS = 200
REQUIRED_LIQUIDITY_LOCK = True
REQUIRED_HYPE_SCORE = 70

# Behavior
ALERT_INTERVAL = 10  # Seconds between alert checks
COOLDOWN_AFTER_CALL = 180  # Seconds to avoid spam
DEEP_RESEARCH_DELAY = 90  # Seconds after initial alpha call

# Risk logic
MIN_HOLDER_COUNT = 25
MAX_BUY_TAX = 5  # %
MAX_SELL_TAX = 5  # %
SMART_WALLET_SIGNAL_WEIGHT = 1.5

# Internal
VERSION = "Obsidian Mode++"
