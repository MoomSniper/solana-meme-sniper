import os
import logging
import asyncio
import httpx
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters
from bs4 import BeautifulSoup
import cloudscraper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route(f"/{os.environ['BOT_TOKEN']}", methods=["POST"])
async def webhook_handler():
    await application.process_update(Update.de_json(request.get_json(force=True), application.bot))
    return "ok"

async def scan_dexscreener():
    scraper = cloudscraper.create_scraper()
    url = "https://dexscreener.com/solana"
    headers = {"User-Agent": "Mozilla/5.0"}

    while True:
        try:
            res = scraper.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html.parser")
            pairs = soup.find_all("a", class_="chakra-link css-1n8x036")
            logger.info(f"Found {len(pairs)} pairs on Dexscreener")
        except Exception as e:
            logger.error(f"Error during scan: {e}")
        await asyncio.sleep(10)

async def start_bot():
    global application
    application = (
        ApplicationBuilder()
        .token(os.environ["BOT_TOKEN"])
        .build()
    )

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("✅ Bot is running in Obsidian Mode.")

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    webhook_url = f"{os.environ.get('WEBHOOK_URL')}/{os.environ.get('BOT_TOKEN')}"
    await application.initialize()
    await application.bot.set_webhook(url=webhook_url)
    logger.info("✅ Telegram webhook set.")

    asyncio.create_task(scan_dexscreener())
    logger.info("🧠 Obsidian Mode active. Scanner running.")
    await application.start()
    await application.updater.start_polling()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
