import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from modules.coinhall_ws import listen_for_pairs
from modules.helius_wallets import check_wallet_quality
from modules.contract_check import run_rug_check
from modules.social_scraper import get_social_hype_score
from modules.alpha_scoring import calculate_alpha_score
from modules.exit_logic import analyze_exit

# Load .env variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
PORT = int(os.getenv("PORT", 10000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)

# Command: /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Oblivion Sniper Bot is running and scanning.")

# Core token scoring callback
async def handle_token(token_info):
    print(f"🟡 New coin detected: {token_info['token_name']} | MC: {token_info['market_cap']} | Volume 1h: {token_info['volume_1h']}")

    # Placeholder values — to be replaced with live scan targets
    wallet_score = check_wallet_quality("HOLDER_WALLET_ADDRESS")
    rug_score = run_rug_check("TOKEN_ADDRESS")
    social_score = get_social_hype_score(500, 1000, 3.2)

    score = calculate_alpha_score(token_info, wallet_score, rug_score, social_score)

    print(f"🔍 Alpha Scoring Result for {token_info['token_name']}:")
    print(f"- Wallet Score: {wallet_score['score']}")
    print(f"- RugCheck Score: {rug_score['score']}")
    print(f"- Social Hype Score: {social_score}")
    print(f"= Final Confidence: {score}%")

    if score >= 90:
        print(f"🚨 ALPHA COIN TRIGGERED: {token_info['token_name']} | Score: {score}%")

        msg = f"""🚨 *ALPHA COIN DETECTED* 🚨

*Name:* {token_info['token_name']}
*Market Cap:* ${round(token_info['market_cap'], 2)}
*Volume (1h):* ${round(token_info['volume_1h'], 2)}
*Alpha Score:* {score}%

Scoring Breakdown:
- 📊 Wallets: {wallet_score['score']}
- 🛡️ RugCheck: {100 - rug_score['score']}
- 🔥 Social Hype: {social_score}

Get in early or stay watching 👀
"""
        await app.telegram_bot.send_message(chat_id=TELEGRAM_ID, text=msg, parse_mode="Markdown")
        print("✅ Alpha alert sent to Telegram.")
    else:
        print(f"❌ Score too low for {token_info['token_name']}. Skipping.\n")

# Start Telegram bot + WebSocket listener
async def start_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("status", status))

    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=WEBHOOK_URL)
    app.telegram_bot = application.bot

    print("✅ Webhook connected. Sniper bot is scanning live Solana pairs...")

    asyncio.create_task(listen_for_pairs(handle_token))

    await application.updater.start_polling()

if __name__ == "__main__":
    asyncio.run(start_bot())
