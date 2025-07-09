import asyncio
import logging
from dex_scraper import run_sniper

# === Logging ===
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sniper")

# === Main Sniper Loop ===
async def run():
    logger.info("🧠 Obsidian Mode DEX Sniper Active")
    await run_sniper()

if __name__ == "__main__":
    asyncio.run(run())
