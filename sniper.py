async def monitor_market(bot):
    logging.info("🧠 Sniper loop: scanning live token list...")

    try:
        tokens = await fetch_token_list()
        logging.info(f"📊 Fetched {len(tokens)} tokens from Birdeye.")
    except Exception as e:
        await bot.send_message(chat_id=TELEGRAM_ID, text=f"❌ Error fetching token list: {e}")
        return

    if not tokens:
        await bot.send_message(chat_id=TELEGRAM_ID, text="⚠️ No tokens found. Token list is empty.")
        return

    for token in tokens:
        try:
            msg = f"""
📡 LIVE TOKEN FOUND
Name: {token.get('name', 'N/A')}
Symbol: {token.get('symbol', 'N/A')}
Chart: https://birdeye.so/token/{token.get('address')}
"""
            await bot.send_message(chat_id=TELEGRAM_ID, text=msg)
        except Exception as e:
            logging.error(f"Error sending message for token: {e}")
