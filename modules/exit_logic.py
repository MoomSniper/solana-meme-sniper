import logging

logger = logging.getLogger(__name__)

# === Exit Intelligence Engine ===
def evaluate_exit_decision(token_data):
    try:
        volume = token_data.get("volume", 0)
        buyers = token_data.get("buyers", 0)
        sellers = token_data.get("sellers", 0)
        smart_wallet_exits = token_data.get("smart_wallet_exits", 0)
        trend = token_data.get("trend", "stable")

        alerts = []

        if smart_wallet_exits > 3:
            alerts.append("🚨 Smart wallets exiting")

        if sellers > buyers * 2:
            alerts.append("⚠️ Heavy sell pressure")

        if volume < token_data.get("previous_volume", 0) * 0.4:
            alerts.append("📉 Volume drop >60%")

        if trend == "down" and len(alerts) > 0:
            return {
                "action": "EXIT NOW",
                "reasons": alerts
            }

        if trend == "uncertain":
            return {
                "action": "PARTIAL TAKE PROFIT",
                "reasons": alerts if alerts else ["⚠️ Trend unclear"]
            }

        if trend == "up" and sellers < buyers:
            return {
                "action": "HOLD",
                "reasons": ["📈 Buyers still dominate"]
            }

        return {
            "action": "HOLD",
            "reasons": alerts if alerts else ["🟢 Stable conditions"]
        }

    except Exception as e:
        logger.error(f"❌ Exit decision failed: {e}")
        return {
            "action": "HOLD",
            "reasons": ["❌ Failed to evaluate exit"]
        }
