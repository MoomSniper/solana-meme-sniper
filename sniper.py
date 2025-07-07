import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from alpha_engine import scan_new_coins, deep_track_coin, get_best_alpha, log_entry, log_exit, log_profit
from utils import is_valid_coin, get_wallet_activity, get_social_hype, analyze_contract, predict_multiplier

# Bot Config
TELEGRAM_ID = 6881063420
BOT_TOKEN = "7619311236:AAFzjBR3N1oVi31J2WqU4cgZDiJgBxDPWRo"

logging.basicConfig(level=logging.INFO)
alpha_watchlist = {}
live_investments = {}

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != TELEGRAM_ID:
        return
    await update.message.reply_text("🚀 Sniper bot online. Ready to hunt alphas.")

# Alpha Command
async def alpha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != TELEGRAM_ID:
        return
    coin = get_best_alpha()
    await update.message.reply_text(f"👑 Best current alpha: {coin}")

# Handle “in {amount}” command
async def handle_in(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != TELEGRAM_ID:
        return
    try:
        text = update.message.text.strip().lower()
        if text.startswith("in"):
            amount = float(text.split()[1])
            live_investments['amount'] = amount
            live_investments['status'] = "active"
            await update.message.reply_text(f"📈 Tracking entry with ${amount} — sniper mode activated.")
            log_entry(amount)
    except:
        await update.message.reply_text("⚠️ Invalid amount. Use format like: in 50")

# Handle “tp {amount}” for profit logging
async def handle_tp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != TELEGRAM_ID:
        return
    try:
        text = update.message.text.strip().lower()
        if text.startswith("tp"):
            tp_amount = float(text.split()[1])
            log_profit(tp_amount)
            await update.message.reply_text(f"💰 Logged take profit of ${tp_amount}")
    except:
        await update.message.reply_text("⚠️ Invalid TP format. Use: tp 120")

# Exit handling
async def handle_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != TELEGRAM_ID:
        return
    live_investments.clear()
    log_exit()
    await update.message.reply_text("📤 Position exited. Tracker reset.")

# Deep Alpha Scanner Loop
async def sniper_loop(application):
    while True:
        new_coin = scan_new_coins()
        if new_coin and is_valid_coin(new_coin):
            confidence = predict_multiplier(new_coin)
            if confidence > 85:
                await application.bot.send_message(chat_id=TELEGRAM_ID,
                    text=f"🚨 New Alpha: {new_coin}\nConfidence: {confidence:.1f}%\nTracking in 90s...")
                await asyncio.sleep(90)
                asyncio.create_task(deep_track_coin(application, new_coin))
        await asyncio.sleep(2)

# Init Bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("alpha", alpha))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^in "), handle_in))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^tp "), handle_tp))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^exit$"), handle_exit))

async def main():
    await app.initialize()
    await app.start()
    asyncio.create_task(sniper_loop(app))
    await app.updater.start_polling()
    await app.idle()

if __name__ == "__main__":
    asyncio.run(main())
