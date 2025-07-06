import os
import asyncio
import nest_asyncio
from flask import Flask, request
from telegram.ext import Application
from sniper import monitor_market

TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)
application = None

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    return await application.update_webhook(request)

async def setup():
    global application
    application = Application.builder().token(TOKEN).build()

    # Set Telegram webhook
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

    # Start sniper engine (runs once)
    asyncio.create_task(monitor_market())

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(setup())
    app.run(host="0.0.0.0", port=PORT)
