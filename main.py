import os
import asyncio
import logging
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")
API_URL = "https://public-api.birdeye.so/public/tokenlist?sort_by=volume_1h&sort_type=desc&limit=20"

logging.basicConfig(level=logging.INFO)
application = ApplicationBuilder().token(BOT_TOKEN).build()

sniped_tokens = set()

async def fetch_alpha_tokens():
    try:
        headers = {'X-API-KEY': BIRDEYE_API_KEY}
        response = requests.get(API_URL, headers=headers)
        tokens = response.json().get("data", [])
        alpha_calls = []

        for token in tokens:
            symbol = token.get("symbol")
            address = token.get("address")
            volume = float(token.get("volume_1h", 0))
            market_cap = float(token.get("mc", 0))
            buyers = int(token.get("txns_1h", 0))

            if (symbol and
                5_000 <= volume <= 300_000 and
                50_000 <= market_cap <= 300_000 and
                buyers >= 15 and
                address not in sniped_tokens):
                
                sniped_tokens.add(address)
                alpha_calls.append({
                    "symbol": symbol,
                    "address": address,
                    "volume": volume,
                    "market_cap": market_cap,
                    "buyers": buyers
                })

        return alpha_calls
    except Exception as e:
        logging.error(f"Error fetching tokens: {e}")
        return []

async def send_alpha_calls(context: ContextTypes.DEFAULT_TYPE):
    tokens = await fetch_alpha_tokens()
    for token in tokens:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Watch", callback_data=f"watch_{token['address']}")],
            [InlineKeyboardButton("In", callback_data=f"in_{token['address']}")],
            [InlineKeyboardButton("Out", callback_data=f"out_{token['address']}")]
        ])
        msg = (
            f"🚨 *Alpha Coin Detected*\n"
            f"Symbol: {token['symbol']}\n"
            f"Market Cap: ${token['market_cap']:,}\n"
            f"Volume (1h): ${token['volume']:,}\n"
            f"Buyers (1h): {token['buyers']}\n"
            f"[View on Birdeye](https://birdeye.so/token/{token['address']})"
        )
        await context.bot.send_message(
            chat_id=TELEGRAM_USER_ID,
            text=msg,
            reply_markup=keyboard,
            parse_mode='Markdown',
            disable_web_page_preview=True
        )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data.startswith("watch_"):
        await query.answer("👀 Watching closely...")
    elif data.startswith("in_"):
        await query.answer("🟢 Marked as 'In'")
    elif data.startswith("out_"):
        await query.answer("🔴 Marked as 'Out'")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot is live and scanning alpha coins on Solana.")

application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(handle_buttons))

job_queue = application.job_queue
job_queue.run_repeating(send_alpha_calls, interval=60, first=5)

if __name__ == "__main__":
    application.run_polling()
