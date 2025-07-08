# modules/live_logger.py

from datetime import datetime
import json
import os

LOG_PATH = "logs/live_log.json"

def init_logger():
    """Ensure log directory exists"""
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            json.dump([], f)

def log_event(event_type, token_info, status=None, notes=None):
    """Append structured event to live log"""
    init_logger()
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type,
        "token": token_info,
        "status": status,
        "notes": notes
    }
    with open(LOG_PATH, "r+") as f:
        logs = json.load(f)
        logs.append(log_entry)
        f.seek(0)
        json.dump(logs, f, indent=2)

def get_current_tracked():
    """Return list of currently tracked coins"""
    try:
        with open(LOG_PATH, "r") as f:
            logs = json.load(f)
        active = [entry for entry in logs if entry.get("status") in ["HOLD", "TRACKING", "IN"]]
        return active[-5:]  # return latest 5 tracked
    except Exception:
        return []

def clear_logs():
    """Reset the log file"""
    with open(LOG_PATH, "w") as f:
        json.dump([], f)
