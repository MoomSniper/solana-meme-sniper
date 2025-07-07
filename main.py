import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from sniper import (
    start,
    alpha,
    handle_in,
    handle_tp,
    handle_exit,
    sniper_loop
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TELEGRAM_ID = int(os.getenv("TELEGRAM_ID"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8443))

app = Flask(__name__)
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Telegram commands
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("alpha", alpha))
telegram_app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^in "), handle_in))
telegram_app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^tp "), handle_tp))
telegram_app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^exit$"), handle_exit))

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook() -> str:
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "✅ Sniper bot is running."

async def main():
    await telegram_app.initialize()
    await telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    await telegram_app.start()
    asyncio.create_task(sniper_loop(telegram_app))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    app.run(host="0.0.0.0", port=PORT)
