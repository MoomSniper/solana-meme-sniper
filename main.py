import logging
import os
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
import pytz
import datetime

# Globals
user_data = {
    "entries": [],
    "profits": [],
}

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Flask App
app = Flask(__name__)

@app.route(f"/{os.environ['BOT_TOKEN']}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "ok"

# Telegram Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot active. Use commands like /alpha, in 50, tp 80, exit 100, /status")

async def alpha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Best alpha: 🚀 $RIZZ — 2.7x potential, volume surge + smart wallet activity. Still early.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now(pytz.timezone("America/Toronto"))
    day_total = sum([x['profit'] for x in user_data['profits'] if x['timestamp'].date() == now.date()])
    week_total = sum([x['profit'] for x in user_data['profits'] if now - x['timestamp'] < datetime.timedelta(days=7)])
    open_entries = "\n".join([f"- ${x['amount']} in {x['coin']}" for x in user_data['entries']]) or "None"

    msg = f"""📊 Portfolio Status:
Open Positions:
{open_entries}

📈 Today’s PnL: ${day_total:.2f}
📆 Weekly PnL: ${week_total:.2f}"""

    await update.message.reply_text(msg)

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower().strip()

    if msg.startswith("in "):
        try:
            amount = float(msg.split(" ")[1])
            user_data['entries'].append({
                "amount": amount,
                "coin": "Unknown",
                "timestamp": datetime.datetime.now(pytz.timezone("America/Toronto")),
            })
            await update.message.reply_text(f"📥 Logged: ${amount:.2f} entry.")
        except:
            await update.message.reply_text("❌ Couldn't log entry. Use `in 50` format.")

    elif msg.startswith("tp ") or msg.startswith("exit "):
        try:
            amount = float(msg.split(" ")[1])
            now = datetime.datetime.now(pytz.timezone("America/Toronto"))
            user_data['profits'].append({
                "profit": amount,
                "timestamp": now,
            })
            await update.message.reply_text(f"✅ Logged profit: ${amount:.2f}")
        except:
            await update.message.reply_text("❌ Couldn't log profit. Use `tp 80` or `exit 120` format.")

    else:
        await update.message.reply_text("🤖 Unknown command. Try /alpha, in 50, tp 80, exit 120, or /status.")

# Setup bot
application = ApplicationBuilder().token(os.environ["BOT_TOKEN"]).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("alpha", alpha))
application.add_handler(CommandHandler("status", status))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# Run polling (only if needed)
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ["PORT"]),
        webhook_url=f"{os.environ['WEBHOOK_URL']}/{os.environ['BOT_TOKEN']}"
    )
