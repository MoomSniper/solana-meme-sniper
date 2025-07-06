import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Global bot state
watchlist = []

# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Sniper bot activated.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not watchlist:
        await update.message.reply_text("🕵️ No active coins being tracked.")
    else:
        tracked = "\n".join([f"- {c['symbol']} ({c['score']}%)" for c in watchlist])
        await update.message.reply_text(f"🧠 Currently tracking:\n{tracked}")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    watchlist.clear()
    await update.message.reply_text("🛑 All coin tracking has been stopped.")

async def in_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /in SYMBOL")
        return

    symbol = context.args[0].upper()
    # Placeholder structure — this should be updated dynamically in main
    coin = {"symbol": symbol, "score": "???"}
    watchlist.append(coin)
    await update.message.reply_text(f"✅ Tracking {symbol}.")

async def out_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /out SYMBOL")
        return

    symbol = context.args[0].upper()
    global watchlist
    watchlist = [coin for coin in watchlist if coin["symbol"] != symbol]
    await update.message.reply_text(f"❎ Stopped tracking {symbol}.")

# --- Bot Setup ---
def setup_telegram_commands(app: Application):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("in", in_command))
    app.add_handler(CommandHandler("out", out_command))
