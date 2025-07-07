import time
import requests
import logging
from telegram import Bot

# === BASIC CONFIG ===
TELEGRAM_ID = '6881063420'
BOT_TOKEN = '7619311236:AAFzjBR3N1oVi31J2WqU4cgZDiJgBxDPWRo'
HELIUS_API = 'e61da153-6986-43c3-b19f-380099c1e335a'

# === SETUP LOGGING ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
log = logging.getLogger()

# === TELEGRAM BOT SETUP ===
bot = Bot(token=BOT_TOKEN)

def send_telegram(msg):
    try:
        bot.send_message(chat_id=TELEGRAM_ID, text=msg)
        log.info(f"Sent to Telegram: {msg}")
    except Exception as e:
        log.error(f"Failed to send Telegram message: {e}")

# === MAIN SCANNER ===
def run_sniper():
    log.info("🟢 Sniper bot started.")
    send_telegram("🚀 Sniper bot is live and scanning...")

    while True:
        try:
            # Dummy scan simulation (replace this with real logic later)
            log.info("🔎 Scanning for new coins...")
            time.sleep(5)

            # Fake alpha (simulate alert every 30s)
            if int(time.time()) % 30 < 5:
                alert = f"🪙 Fake Coin Detected! MC: ${round(time.time() % 100000)}"
                send_telegram(alert)
        except Exception as e:
            log.error(f"Sniper error: {e}")
            send_telegram(f"❌ Sniper crashed: {e}")
            time.sleep(10)

if __name__ == '__main__':
    run_sniper()
