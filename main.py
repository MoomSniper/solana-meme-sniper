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
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

    # Start sniper logic (runs in background)
    asyncio.create_task(monitor_market(application.bot))

    return application

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    return {"status": "ok"}

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(setup())
    app.run(host="0.0.0.0", port=PORT)
