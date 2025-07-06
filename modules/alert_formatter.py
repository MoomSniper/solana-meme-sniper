def format_alert(coin):
    try:
        symbol = coin.get("symbol", "N/A")
        mc = coin.get("market_cap", 0)
        vol = coin.get("volume", 0)
        buyers = coin.get("buyers", 0)
        token_address = coin.get("mint", "")
        score = coin.get("score", "??")
        
        dexscreener = f"https://dexscreener.com/solana/{token_address}"
        solscan = f"https://solscan.io/token/{token_address}"

        return (
            f"🚨 <b>ALPHA ALERT [{score}%]</b>\n"
            f"<b>{symbol}</b>\n"
            f"Market Cap: ${int(mc):,}\n"
            f"Volume (1h): ${int(vol):,}\n"
            f"Buyers (1h): {buyers}\n"
            f"<a href='{dexscreener}'>Dexscreener</a> | "
            f"<a href='{solscan}'>Solscan</a>"
        )
    except Exception as e:
        return f"❌ Error formatting alert: {e}"
