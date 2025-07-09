# sniper.py
# 🔧 Standalone Sniper Mode (NO Telegram)
# Use only for testing sniper engine output without full bot

import asyncio
import logging
from dex_scraper import run_sniper

# === Logging ===
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("SniperTest")

# === Main Sniper Loop ===
async def run():
    logger.info("🧠 Obsidian Sniper (Standalone) Activated")
    await run_sniper()

if __name__ == "__main__":
    asyncio.run(run())
