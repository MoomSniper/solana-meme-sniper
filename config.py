import os

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

# API Keys
BIRDEYE_API = os.getenv("BIRDEYE_API")
HELIUS_API = os.getenv("HELIUS_API")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))

# Scanner Controls
SCAN_INTERVAL = 10  # seconds between scans (tuned for 30k/mo usage)
MIN_VOLUME = 4500   # minimum 24h volume
MIN_BUYERS = 8      # minimum number of buyers
MAX_MC = 300000     # max market cap
MIN_MC = 20000      # min market cap

# Sniper Logic Thresholds
ALPHA_SCORE_THRESHOLD = 85
ALPHA_CONFIDENCE_RECOMMEND = 90

# Runtime Limits
SLEEP_START_HOUR = 0   # 12 AM
SLEEP_END_HOUR = 7     # 7 AM

# Exit Intelligence
VOLUME_DROP_THRESHOLD = 0.33   # 33% drop triggers "EXIT NOW"
SMART_WALLET_EXIT_COUNT = 3    # how many whales have to exit before alert

# Social AI Layer
ENABLE_SOCIAL_SCAN = True
SOCIAL_ENGAGEMENT_THRESHOLD = 0.7  # 70%+ real engagement
