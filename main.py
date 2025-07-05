import os
import logging
import asyncio
import httpx
import time
from flask import Flask, request
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from sniper import analyze_coin_and_track

TOKEN = os.environ.get("BOT_TOKEN")
USER_ID = int(os.environ.get("TELEGRAM_ID"))
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)

# Initialize PTB app
application = Application.builder().token(TOKEN).build()

watchlist = set()

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK"

@app.route("/")
def index():
    return "Bot is live"

async def send_alert(msg):
    await bot.send_message(chat_id=USER_ID, text=msg, parse_mode=ParseMode.HTML)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot is active and ready to snipe alpha")

async def watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        token = context.args[0]
        watchlist.add(token)
        await update.message.reply_text(f"👀 Watching: {token}")
    else:
        await update.message.reply_text("Usage: /watch <token_address>")

async def in_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        token = context.args[0]
        await update.message.reply_text(f"🔍 Starting deep scan for: {token}")
        await analyze_coin_and_track(token, bot, USER_ID)
    else:
        await update.message.reply_text("Usage: /in <token_address>")

async def out_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📤 Marked for exit. Bot will stop tracking this coin.")

async def setup_webhook():
    await bot.delete_webhook()
    url = f"{WEBHOOK_URL}/{TOKEN}"
    await bot.set_webhook(url)
    logging.info(f"✅ Webhook set: {url}")

if __name__ == '__main__':
    import nest_asyncio
    nest_asyncio.apply()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("watch", watch_command))
    application.add_handler(CommandHandler("in", in_command))
    application.add_handler(CommandHandler("out", out_command))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup_webhook())

    app.run(host="0.0.0.0", port=PORT)
