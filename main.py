import os
import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Env
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

# Flask
app = Flask(__name__)

# Telegram App
application = Application.builder().token(BOT_TOKEN).build()

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 God Mode Meme Sniper Activated.")
    logger.info(f"/start triggered by {update.effective_user.id}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.lower().strip()
    user_id = update.effective_user.id
    logger.info(f"Message from {user_id}: {msg}")
    
    if msg == "watch":
        await update.message.reply_text("✅ Watching radar-ready coins...")
    elif msg == "in":
        await update.message.reply_text("🟢 You’re IN. Doing deeper scan on this one.")
    elif msg == "out":
        await update.message.reply_text("🔴 Out. Removing from radar.")
    else:
        await update.message.reply_text("🤖 Unrecognized command. Use: watch, in, or out")

# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    try:
        if request.headers.get("Content-Type") == "application/json":
            update = Update.de_json(request.get_json(force=True), application.bot)
            application.update_queue.put_nowait(update)
            logger.info("✅ Update pushed to queue")
            return jsonify({"status": "ok"})
        else:
            logger.warning("❌ Invalid content type")
            return "Invalid content type", 400
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "error", 500

# Flask boot
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
