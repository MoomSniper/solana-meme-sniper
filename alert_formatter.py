def format_alert(symbol, mint, score, mc, vol, buyers, tg_members, twitter_followers, link):
    return (
        f"<b>🚀 ALPHA CALL: {symbol}</b>\n"
        f"<b>🧠 Score:</b> {score}/100\n"
        f"<b>💰 Market Cap:</b> ${mc:,}\n"
        f"<b>📈 1h Volume:</b> ${vol:,}\n"
        f"<b>👥 Buyers (1h):</b> {buyers}\n"
        f"<b>📢 Telegram:</b> {tg_members} members\n"
        f"<b>🐦 Twitter:</b> {twitter_followers} followers\n"
        f"<b>🔗</b> <a href='{link}'>Chart</a>\n"
        f"\n<b>🟢 Ready to snipe. Use /in to confirm entry.</b>"
    )
