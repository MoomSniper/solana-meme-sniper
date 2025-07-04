import os
import telebot
import requests
import time
import threading

BIRDEYE_API = os.getenv("BIRDEYE_API")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = os.getenv("TELEGRAM_ID")

if not all([BIRDEYE_API, BOT_TOKEN, TELEGRAM_ID]):
    raise Exception("❌ One or more environment variables are missing. Check BIRDEYE_API, BOT_TOKEN, and TELEGRAM_ID.")

bot = telebot.TeleBot(BOT_TOKEN)
active_coin = None
track_deep = False

def send_alert(message):
    bot.send_message(TELEGRAM_ID, message)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Sniper bot is LIVE. Send 'in' to track, 'out' to stop.")

@bot.message_handler(func=lambda message: message.text.lower() == 'in')
def handle_in(message):
    global track_deep
    track_deep = True
    bot.reply_to(message, "🧠 Deep tracking mode enabled.")

@bot.message_handler(func=lambda message: message.text.lower() == 'out')
def handle_out(message):
    global track_deep
    track_deep = False
    bot.reply_to(message, "🛑 Tracking stopped.")

def is_coin_alpha(coin):
    try:
        mc = coin['fdv_usd']
        vol = coin['volume_1h_quote']
        buyers = coin['txns']['buys']
        base = coin['base_token']['symbol']
        telegram = coin['dex_info'].get('telegram')
        twitter = coin['dex_info'].get('twitter')

        if (
            mc and mc < 300000 and
            vol and vol > 5000 and
            buyers and buyers >= 15 and
            base and
            telegram and twitter
        ):
            return True
    except Exception:
        return False
    return False

def format_alert(coin):
    name = coin['base_token']['name']
    symbol = coin['base_token']['symbol']
    mc = round(coin['fdv_usd'])
    vol = round(coin['volume_1h_quote'])
    link = f"https://birdeye.so/token/{coin['address']}?chain=solana"
    return f"🔥 **ALPHA FOUND**\n{name} (${symbol})\nMarket Cap: ${mc}\n1h Volume: ${vol}\n[View on Birdeye]({link})"

def track_coins():
    seen = set()
    while True:
        try:
            url = f"https://public-api.birdeye.so/public/tokenlist?sort=volume_1h&order=desc&limit=50&chain=solana"
            headers = {'X-API-KEY': BIRDEYE_API}
            response = requests.get(url, headers=headers)
            tokens = response.json().get('data', [])

            for token in tokens:
                address = token.get('address')
                if address and address not in seen:
                    if is_coin_alpha(token):
                        seen.add(address)
                        alert_msg = format_alert(token)
                        send_alert(alert_msg)
        except Exception as e:
            print(f"[ERROR] {str(e)}")

        time.sleep(2)

# Background polling thread
t = threading.Thread(target=track_coins)
t.start()

send_alert("🚀 Sniper Bot deployed and monitoring new alpha coins.")

print("🚀 Sniper bot running in GOD MODE +++++")
bot.infinity_polling()
