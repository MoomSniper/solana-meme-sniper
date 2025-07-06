import os
import asyncio
from flask import Flask, request
from telegram.ext import Application
from sniper import monitor_market

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)

async def setup():
    application = Application.builder().token(TOKEN).build()

    # Set webhook for Telegram
    await application.bot.set_webhook(url=WEBHOOK_URL)

    # Start sniper logic (once, on boot)
    await monitor_market()

    return application

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    return {"status": "ok"}

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(setup())
    app.run(host="0.0.0.0", port=PORT)
