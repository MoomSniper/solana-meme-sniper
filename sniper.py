import time
import logging
from birdeye import get_top_coins
from telegram_bot import bot, TELEGRAM_ID

logger = logging.getLogger(__name__)

def format_price(price):
    try:
        return round(float(price), 6)
    except:
        return 0

async def run_test_sniper():
    logger.info("🧪 Running test sniper...")

    while True:
        coins = get_top_coins()
        for coin in coins:
            try:
                symbol = coin.get("symbol")
                token_name = coin.get("name")
                token_symbol = coin.get("symbol")
                address = coin.get("address")
                price = format_price(coin.get("price", 0))
                volume = float(coin.get("volume_24h", 0))
                market_cap = float(coin.get("mc", 0))
                dexscreener_url = f"https://dexscreener.com/solana/{address}"

                if market_cap >= 80000 and volume >= 25000:
                    text = (
                        f"🔔 *Test Coin Alert!*\n\n"
                        f"Name: {token_name}\n"
                        f"Symbol: {token_symbol}\n"
                        f"Price: ${price:.6f}\n"
                        f"24h Volume: ${int(volume):,}\n"
                        f"Market Cap: ${int(market_cap):,}\n"
                        f"[Buy Link (DEX Screener)]({dexscreener_url})"
                    )

                    await bot.send_message(chat_id=TELEGRAM_ID, text=text, parse_mode="Markdown")
                    logger.info(f"✅ Alert sent for {symbol}")
                    return True

            except Exception as e:
                logger.error(f"Error parsing coin: {e}")
                continue

        time.sleep(5)
