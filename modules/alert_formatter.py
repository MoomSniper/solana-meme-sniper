def format_alert(coin_data, alpha_score, entry_confidence, projected_multiplier, telegram_score, twitter_score):
    name = coin_data.get("baseToken", {}).get("name", "Unknown")
    symbol = coin_data.get("baseToken", {}).get("symbol", "???")
    mc = coin_data.get("marketCap", "N/A")
    vol = coin_data.get("volume24h", "N/A")
    buyers = coin_data.get("buyers", "N/A")
    url = coin_data.get("url", "N/A")

    return f"""
🚨 NEW ALPHA SNIPED — {symbol}
━━━━━━━━━━━━━━━━━━━━
🧠 Name: {name}
📊 MC: ${int(mc):,} | 24H Vol: ${int(vol):,}
👥 Buyers: {buyers}
🔥 Alpha Score: {alpha_score:.1f}/100
⚡️ Entry Confidence: {entry_confidence:.1f}%
📈 Projected Multiplier: {projected_multiplier:.1f}x
💬 Twitter Score: {twitter_score:.2f}/1.00
🗨️ Telegram Score: {telegram_score:.2f}/1.00
🔗 Chart: {url}
━━━━━━━━━━━━━━━━━━━━
⚠️ ENTER NOW if you trust the play.
"""

def format_exit_alert(reason):
    return f"""
❌ EXIT NOW — Play is cooling down
━━━━━━━━━━━━━━━━━━━━
⚠️ Reason: {reason}
🚪 Close position immediately or scale out.
"""

def format_partial_tp():
    return f"""
🟡 PARTIAL TAKE PROFIT
━━━━━━━━━━━━━━━━━━━━
Momentum is shaky. Lock some gains.
"""

def format_hold():
    return f"""
🟢 HOLD
━━━━━━━━━━━━━━━━━━━━
Momentum strong. Continue riding.
"""
