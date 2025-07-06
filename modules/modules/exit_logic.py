def analyze_exit(current_volume, previous_volume, whale_exited):
    volume_drop = (previous_volume - current_volume) / previous_volume if previous_volume > 0 else 0

    if whale_exited:
        return "🚨 EXIT NOW — Smart money has left"

    if volume_drop >= 0.5:
        return "⚠️ EXIT NOW — Volume collapse detected"

    elif volume_drop >= 0.3:
        return "🔁 PARTIAL TAKE PROFIT — Momentum fading"

    else:
        return "✅ HOLD — Momentum intact"
