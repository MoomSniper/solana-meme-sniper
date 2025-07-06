import os
import asyncio
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from modules.telegram_engine import setup_telegram_commands
from modules.solana_tracker_api import fetch_token_data
from modules.alpha_scoring import score_token
from modules.contract_check import run_contract_safety_check
from modules.social_scraper import scrape_social_signals
from modules.deep_research import run_deep_research
from modules.alert_formatter import format_alert
from sniper import scan_and_score_market

# --- Logging ---
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("obsidian")

# --- Load Env Vars ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", "10000"))

# --- Flask App ---
flask_app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()

setup_telegram_commands(telegram_app)

@flask_app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    await telegram_app.update_queue.put(Update.de_json(request.json, telegram_app.bot))
    return "OK", 200

@flask_app.route("/", methods=["GET"])
def health_check():
    return "✅ Obsidian Bot Alive", 200

# --- Alpha Scanning Loop ---
async def sniper_loop():
    while True:
        try:
            alpha_coin = await scan_and_score_market()
            if alpha_coin:
                alert = await format_alert(alpha_coin)
                await telegram_app.bot.send_message(
                    chat_id=TELEGRAM_ID,
                    text=alert,
                    parse_mode="HTML",
                    disable_web_page_preview=False
                )
                logger.info(f"🚨 Alpha alert sent for {alpha_coin.get('symbol')}")
        except Exception as e:
            logger.error(f"[SNIPER ERROR] {e}")
        await asyncio.sleep(2)

# --- Main Entry ---
async def main():
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    logger.info("🧠 Obsidian Bot Online")

    # Flask in async thread
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, lambda: flask_app.run(host="0.0.0.0", port=PORT))

    # Start scanner
    await sniper_loop()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    try:
        asyncio.run(main())
    except Exception as e:
        logger.exception("🔥 Bot crashed on startup:")
