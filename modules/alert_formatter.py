# modules/alert_formatter.py
import logging

def format_alert(token, score):
    try:
        name = token.get("name", "Unknown")
        symbol = token.get("symbol", "?")
        url = token.get("chart_url", "")
        mc = float(token.get("fdv", 0))
        volume = float(token.get("volume_usd_1h", 0))
        holders = token.get("holder_count", 0)

        return (
            f"🚨 <b>ALPHA ALERT [{score}%]</b>\n"
            f"<b>{name} ({symbol})</b>\n"
            f"Market Cap: ${int(mc):,}\n"
            f"Volume (1h): ${int(volume):,}\n"
            f"Holders: {holders}\n"
            f"<a href='{url}'>View Chart</a>"
        )
    except Exception as e:
        logging.warning(f"[Format Error] {e}")
        return "❌ Error formatting alert."
