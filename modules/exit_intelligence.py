import asyncio
import logging
from modules.sol_tracker import get_coin_details

logger = logging.getLogger("exit_mastermind")

async def run_exit_intelligence(symbol, mint):
    try:
        logger.info(f"🎯 Exit tracking started for {symbol} ({mint})")

        while True:
            coin = await get_coin_details(mint)
            if not coin:
                logger.warning("❌ Coin data not found.")
                await asyncio.sleep(10)
                continue

            volume_5m = coin.get("volume_5m", 0)
            volume_15m = coin.get("volume_15m", 0)
            smart_wallets = coin.get("smart_wallets", 0)
            holders = coin.get("holders", 0)

            # === EXIT NOW ===
            if volume_5m < (0.25 * volume_15m) or smart_wallets < 2:
                return f"🚪 <b>EXIT NOW</b>\n• 5m Volume Crash\n• Smart Wallets: {smart_wallets}\n• Holders: {holders}"

            # === PARTIAL TAKE PROFIT ===
            if volume_5m < (0.5 * volume_15m) or holders < 100:
                return f"🟡 <b>PARTIAL TAKE PROFIT</b>\n• Volume slowing\n• Smart Wallets: {smart_wallets}\n• Holders: {holders}"

            # === HOLD ===
            return f"✅ <b>HOLD</b>\n• Volume Healthy\n• Smart Wallets: {smart_wallets}\n• Holders: {holders}"

            await asyncio.sleep(30)  # check every 30s

    except Exception as e:
        logger.error(f"[Exit Intelligence Error] {e}")
        return "❌ Exit check failed."
