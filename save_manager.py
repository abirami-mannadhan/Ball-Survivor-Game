import json
import os
import time

SAVE_FILE = "save_data.json"
WAIT_SECONDS = 20 * 60  # 20 minutes


def load_state():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                s = json.load(f)
            return {
                "unlocked": s.get("unlocked", 1),
                "stars": s.get("stars", {}),
                "lives": s.get("lives", 3),
                "wait_start": s.get("wait_start", None),
            }
        except Exception:
            pass
    return {"unlocked": 1, "stars": {}, "lives": 3, "wait_start": None}


def save_state(state):
    with open(SAVE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def check_wait_timer(state):
    """Refill lives if wait period is over."""
    if state["lives"] >= 3:
        state["wait_start"] = None
        return state
    if state["wait_start"] is not None:
        elapsed = time.time() - state["wait_start"]
        if elapsed >= WAIT_SECONDS:
            state["lives"] = 3
            state["wait_start"] = None
            save_state(state)
    return state


def get_remaining_wait(state):
    if state["wait_start"] is None:
        return 0
    return max(0, WAIT_SECONDS - (time.time() - state["wait_start"]))


def fmt_wait(seconds):
    s = int(seconds)
    return f"{s // 60:02d}:{s % 60:02d}"
