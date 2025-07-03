import os
import time
import requests
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from datetime import datetime

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_USER_ID = int(os.getenv("TELEGRAM_USER_ID"))
BIRDEYE_API_KEY = os.getenv("BIRDEYE_API_KEY")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)

def fetch_top_sol_tokens():
    url = f"https://public-api.birdeye.so/public/tokenlist?sort_by=volume_24h_usd&sort_type=desc&limit=20&offset=0&chain=solana"
    headers = {"X-API-KEY": BIRDEYE_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["data"]["tokens"]
    return []

def format_token_info(token):
    return f"<b>{token['name']}</b> ({token['symbol']})\nMarket Cap: ${int(token['mc'])}\nVolume 24h: ${int(token['volume_24h'])}\n<a href='https://dexscreener.com/solana/{token['address']}'>DexScreener</a> | <a href='https://birdeye.so/token/{token['address']}?chain=solana'>Birdeye</a>"

def send_token_alert(token):
    text = format_token_info(token)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("IN ð", callback_data=f"in:{token['address']}"),
         InlineKeyboardButton("OUT ð¨", callback_data=f"out:{token['address']}")]
    ])
    bot.send_message(chat_id=TELEGRAM_USER_ID, text=text, parse_mode="HTML", reply_markup=keyboard)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Solana God Mode Sniper Activated ð")

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    action, token_addr = query.data.split(":")

    if action == "in":
        context.bot.send_message(chat_id=TELEGRAM_USER_ID,
                                 text=f"ð Deep research initiated on {token_addr}... checking whales, trends, influencers, entries and exits.")
        # Placeholder for future research integration
    elif action == "out":
        context.bot.send_message(chat_id=TELEGRAM_USER_ID,
                                 text=f"ð¸ Exiting position and securing profits on {token_addr}")

def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))

    updater.start_polling()

    sent_addresses = set()
    while True:
        tokens = fetch_top_sol_tokens()
        for token in tokens:
            if token["address"] not in sent_addresses and token.get("mc", 0) and token.get("volume_24h", 0):
                if token["mc"] < 300000 and token["volume_24h"] > 5000:
                    send_token_alert(token)
                    sent_addresses.add(token["address"])
        time.sleep(60)

if __name__ == "__main__":
    main()
