def analyze_exit(volume_now, volume_prev, whale_exit_detected):
    if whale_exit_detected:
        return "EXIT NOW"

    drop = (volume_prev - volume_now) / volume_prev if volume_prev else 0
    if drop > 0.4:
        return "PARTIAL TP"
    elif drop > 0.7:
        return "EXIT NOW"
    else:
        return "HOLD"
