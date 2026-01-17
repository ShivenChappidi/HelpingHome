"""
Laundry Room Demo for HelpingHome - Autism Assistance Application
Fully-automatic state machine with auto-start, finish detection, and reminders.
"""

import time
import sys
import os
import threading
from typing import Dict, Optional, Any

# Add project root to path so imports work when running this file directly
_script_dir = os.path.dirname(os.path.abspath(__file__))  # rooms/laundry/
_rooms_dir = os.path.dirname(_script_dir)  # rooms/
project_root = os.path.dirname(_rooms_dir)  # project root (HelpingHome/)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import audio agent
try:
    from utils.audio import speak_text
    AUDIO_AVAILABLE = True
    print("[DEBUG] Audio module imported successfully")
except Exception as e:
    AUDIO_AVAILABLE = False
    speak_text = None
    print(f"[DEBUG] Audio import failed: {e}")


# =============================================================================
# CONFIGURATION (User-customizable expected time defaults to 45)
# =============================================================================

DEFAULT_EXPECTED_CYCLE_MINUTES = 45
EXPECTED_CYCLE_MINUTES = DEFAULT_EXPECTED_CYCLE_MINUTES  # user can override in demo

# Sensory (optional)
SOUND_THRESHOLD_DB = 70
CALM_FEEDBACK_COLOR = "blue"

# Auto-start rules
AUTO_START_WINDOW_SECONDS = 120
START_VIBRATION_THRESHOLD = 0.6

# Finish detection rules
FINISH_EARLY_MINUTES = 5
FINISH_LATE_MINUTES = 20
FINISH_QUIET_SECONDS = 180  # no vibration for 180s inside finish window => done

# Automatic background polling (keep small so it "constantly scans")
AUTO_CHECK_INTERVAL_SECONDS = 1.0

# Reminder policy: max 3 reminders (Stage 1 is the "done" alert)
# Stage 2 & 3 are if the door remains closed after finish.
REMINDER_STAGE2_AFTER_MIN = 30
REMINDER_STAGE3_AFTER_MIN = 90

EARLY_FALSE_POSITIVE_QUIET_SECONDS = 600  # 10 minutes
CYCLE_CANCELLED_BY_FALSE_POSITIVE = False


# =============================================================================
# STATE
# =============================================================================

WASHER_RUNNING = False
WASHER_STARTED_AT: Optional[float] = None

LAST_VIBRATION_TIME: Optional[float] = None
LAST_VIBRATION_LEVEL: float = 0.0

DOOR_STATUS = "CLOSED"  # OPEN/CLOSED
LAST_DOOR_OPENED_AT: Optional[float] = None
LAST_DOOR_CLOSED_AT: Optional[float] = None

# "Armed" means we saw an OPEN then a CLOSE (user loaded washer)
CYCLE_ARMED = False

# Finish/reminders
LAUNDRY_FINISHED_AT: Optional[float] = None
REMINDER_STAGE = 0  # 0 none, 1 done alert sent, 2 stage2 sent, 3 stage3 sent/stopped
SNOOZE_UNTIL: Optional[float] = None

# One-time alerts during run
ALMOST_DONE_NOTIFIED = False
OVERRUN_MOTION_NOTIFIED = False

# If door opens at any point, we stop everything forever for that cycle
CYCLE_CANCELLED_BY_DOOR_OPEN = False


# =============================================================================
# Helpers
# =============================================================================

def _reset_for_next_cycle() -> None:
    """Clear latches so the next load can start normally."""
    global CYCLE_ARMED, ALMOST_DONE_NOTIFIED, OVERRUN_MOTION_NOTIFIED
    global CYCLE_CANCELLED_BY_DOOR_OPEN, CYCLE_CANCELLED_BY_FALSE_POSITIVE
    global REMINDER_STAGE, LAUNDRY_FINISHED_AT, SNOOZE_UNTIL
    global LAST_VIBRATION_TIME, LAST_VIBRATION_LEVEL

    # Clear reminder/finish state
    LAUNDRY_FINISHED_AT = None
    REMINDER_STAGE = 0
    SNOOZE_UNTIL = None

    # Clear one-cycle latches
    ALMOST_DONE_NOTIFIED = False
    OVERRUN_MOTION_NOTIFIED = False
    CYCLE_CANCELLED_BY_DOOR_OPEN = False
    CYCLE_CANCELLED_BY_FALSE_POSITIVE = False

    # Optional: reset vibration baseline so door jostle doesn't carry over
    LAST_VIBRATION_TIME = None
    LAST_VIBRATION_LEVEL = 0.0

    # Re-arm will be set after OPEN->CLOSE
    CYCLE_ARMED = False

def _say(text: str) -> None:
    if AUDIO_AVAILABLE and speak_text:
        speak_text(text)

def _now() -> float:
    return time.time()

def _elapsed_minutes(since: Optional[float]) -> Optional[float]:
    if since is None:
        return None
    return (_now() - since) / 60.0

def _finish_window() -> (float, float):
    window_start = EXPECTED_CYCLE_MINUTES - FINISH_EARLY_MINUTES
    window_end = EXPECTED_CYCLE_MINUTES + FINISH_LATE_MINUTES
    return window_start, window_end

def _in_finish_window(elapsed_min: float) -> bool:
    start, end = _finish_window()
    return start <= elapsed_min <= end


# =============================================================================
# Core Behaviors
# =============================================================================

def set_expected_cycle_minutes(minutes: int) -> Dict[str, Any]:
    """User customization. Default is 45, but can be changed anytime before start."""
    global EXPECTED_CYCLE_MINUTES
    if minutes <= 0:
        return {"action": "invalid_expected_time"}
    EXPECTED_CYCLE_MINUTES = minutes
    print(f"⏱️ Expected cycle time set to {EXPECTED_CYCLE_MINUTES} minutes (default={DEFAULT_EXPECTED_CYCLE_MINUTES})")
    return {"action": "expected_time_set", "expected_minutes": EXPECTED_CYCLE_MINUTES}


def start_laundry_cycle() -> Dict[str, Any]:
    """Start laundry cycle and reset alert state."""
    global WASHER_RUNNING, WASHER_STARTED_AT, LAST_VIBRATION_TIME, LAUNDRY_FINISHED_AT, REMINDER_STAGE
    global ALMOST_DONE_NOTIFIED, OVERRUN_MOTION_NOTIFIED, CYCLE_CANCELLED_BY_DOOR_OPEN, CYCLE_CANCELLED_BY_FALSE_POSITIVE

    WASHER_RUNNING = True
    WASHER_STARTED_AT = _now()
    LAST_VIBRATION_TIME = _now()  # assume motion at start
    LAUNDRY_FINISHED_AT = None
    REMINDER_STAGE = 0
    ALMOST_DONE_NOTIFIED = False
    OVERRUN_MOTION_NOTIFIED = False
    CYCLE_CANCELLED_BY_DOOR_OPEN = False
    CYCLE_CANCELLED_BY_FALSE_POSITIVE = False
    print(f"🧺 Laundry started automatically (expected: {EXPECTED_CYCLE_MINUTES} minutes)")
    _say("Laundry started.")
    return {"action": "laundry_started", "expected_minutes": EXPECTED_CYCLE_MINUTES}


def update_vibration(vibration_level: float) -> Dict[str, Any]:
    """Update vibration readings; triggers auto-start if conditions are met."""
    global LAST_VIBRATION_TIME, LAST_VIBRATION_LEVEL
    LAST_VIBRATION_LEVEL = vibration_level

    if vibration_level > 0:
        LAST_VIBRATION_TIME = _now()
        _maybe_auto_start()

    return {"action": "vibration_updated", "vibration": vibration_level}


def update_door_status(status: str) -> Dict[str, Any]:
    """
    Door logic:
    - OPEN then CLOSE arms the system for auto-start.
    - If door opens at ANY point while running or after finish: mark finished and stop ALL alerts.
    - If door opens while idle: reset latches so a new cycle can start.
    """
    global DOOR_STATUS, LAST_DOOR_OPENED_AT, LAST_DOOR_CLOSED_AT, CYCLE_ARMED
    global WASHER_RUNNING, LAUNDRY_FINISHED_AT, REMINDER_STAGE, SNOOZE_UNTIL
    global CYCLE_CANCELLED_BY_DOOR_OPEN

    DOOR_STATUS = status.strip().upper()

    if DOOR_STATUS == "OPEN":
        LAST_DOOR_OPENED_AT = _now()

        # If door opens during a running/finished cycle -> stop everything for THAT cycle
        if WASHER_RUNNING or LAUNDRY_FINISHED_AT is not None:
            WASHER_RUNNING = False
            LAUNDRY_FINISHED_AT = None
            REMINDER_STAGE = 3
            SNOOZE_UNTIL = None
            CYCLE_CANCELLED_BY_DOOR_OPEN = True
            print("🚪 Door opened → cycle marked finished, all alerts stopped.")
            _say("Door opened. Cycle complete.")
            return {"action": "door_open_stops_all"}

        # ✅ If idle -> this is the start of a new interaction, reset for next cycle
        _reset_for_next_cycle()
        print("🔄 Ready for next cycle (reset on door open).")
        return {"action": "door_opened_reset"}

    if DOOR_STATUS == "CLOSED":
        LAST_DOOR_CLOSED_AT = _now()

        # Arm auto-start only if we saw an OPEN recently (user loaded washer)
        if LAST_DOOR_OPENED_AT is not None and (LAST_DOOR_CLOSED_AT - LAST_DOOR_OPENED_AT) <= 300:
            CYCLE_ARMED = True

        return {"action": "door_closed", "armed": CYCLE_ARMED}

    return {"action": "door_updated", "status": DOOR_STATUS}


def _maybe_auto_start() -> Optional[Dict[str, Any]]:
    """
    Auto-start when:
    - Not already running
    - Door is CLOSED
    - We saw OPEN -> CLOSE (armed)
    - Strong vibration
    - Vibration occurs within 120s of the door closing
    """
    global CYCLE_ARMED
    if WASHER_RUNNING:
        return None
    if CYCLE_CANCELLED_BY_DOOR_OPEN:
        return None
    if DOOR_STATUS != "CLOSED":
        return None
    if not CYCLE_ARMED:
        return None
    if LAST_DOOR_CLOSED_AT is None:
        return None
    if LAST_VIBRATION_LEVEL < START_VIBRATION_THRESHOLD:
        return None

    if (_now() - LAST_DOOR_CLOSED_AT) <= AUTO_START_WINDOW_SECONDS:
        CYCLE_ARMED = False  # consume the arm
        result = start_laundry_cycle()
        print("✓ Auto-started: door cycle + vibration detected")
        return result

    return None


def _maybe_almost_done_alert() -> None:
    """At expected - 5 minutes: alert once."""
    global ALMOST_DONE_NOTIFIED
    if not WASHER_RUNNING or WASHER_STARTED_AT is None:
        return
    if CYCLE_CANCELLED_BY_DOOR_OPEN:
        return

    elapsed = _elapsed_minutes(WASHER_STARTED_AT)
    if elapsed is None:
        return

    trigger_time = EXPECTED_CYCLE_MINUTES - FINISH_EARLY_MINUTES
    if (not ALMOST_DONE_NOTIFIED) and elapsed >= trigger_time:
        ALMOST_DONE_NOTIFIED = True
        print("🟦 Almost done. Gentle cue activated.")
        _say("Laundry is almost done.")

def _check_early_false_positive() -> Dict[str, Any]:
    """
    If we auto-started but the washer is quiet for >= 5 minutes
    BEFORE the finish window starts (expected - 5), treat as false positive:
    stop the cycle and stop all future alerts.
    """
    global WASHER_RUNNING, REMINDER_STAGE, LAUNDRY_FINISHED_AT
    global CYCLE_CANCELLED_BY_FALSE_POSITIVE, CYCLE_ARMED

    if not WASHER_RUNNING or WASHER_STARTED_AT is None:
        return {"action": "not_running"}
    if CYCLE_CANCELLED_BY_DOOR_OPEN:
        return {"action": "cancelled_by_door"}
    if CYCLE_CANCELLED_BY_FALSE_POSITIVE:
        return {"action": "already_cancelled_false_positive"}

    elapsed = _elapsed_minutes(WASHER_STARTED_AT)
    if elapsed is None:
        return {"action": "unknown"}

    window_start, _ = _finish_window()  # expected - 5, expected + 20

    # Only applies BEFORE expected-5
    if elapsed < window_start:
        quiet_seconds = int(_now() - LAST_VIBRATION_TIME) if LAST_VIBRATION_TIME else 10**9

        if quiet_seconds >= EARLY_FALSE_POSITIVE_QUIET_SECONDS:
            WASHER_RUNNING = False
            LAUNDRY_FINISHED_AT = None         # don't start wet-clothes reminders
            REMINDER_STAGE = 3                 # hard stop reminders
            CYCLE_CANCELLED_BY_FALSE_POSITIVE = True
            CYCLE_ARMED = False                # require a new open->close to arm again

            print("🛑 False positive detected: quiet for 10+ minutes early. Cycle cancelled.")
            _say("It looks like that start was accidental. I stopped tracking this cycle.")
            return {"action": "false_positive_cancelled", "quiet_seconds": quiet_seconds}

        return {"action": "early_window_ok", "quiet_seconds": quiet_seconds}

    return {"action": "past_early_window"}

def _check_finish_logic() -> Dict[str, Any]:
    """
    Your exact rule:
    - Between (expected-5) and (expected+20), keep scanning for vibration.
    - If there's ever NO vibration for 180 seconds in this window => Stage 1 done alert.
    - If past expected+20 and vibration is still happening (never quiet enough) => overrun motion warning.
    """
    global WASHER_RUNNING, LAUNDRY_FINISHED_AT, REMINDER_STAGE
    global OVERRUN_MOTION_NOTIFIED

    if not WASHER_RUNNING or WASHER_STARTED_AT is None:
        return {"action": "not_running"}
    if CYCLE_CANCELLED_BY_DOOR_OPEN:
        return {"action": "cancelled_by_door"}

    elapsed = _elapsed_minutes(WASHER_STARTED_AT)
    if elapsed is None:
        return {"action": "unknown"}

    window_start, window_end = _finish_window()

    # Only evaluate finish based on quiet-time inside the window
    if elapsed >= window_start and elapsed <= window_end:
        if LAST_VIBRATION_TIME is None:
            quiet_seconds = 10**9
        else:
            quiet_seconds = int(_now() - LAST_VIBRATION_TIME)

        if quiet_seconds >= FINISH_QUIET_SECONDS:
            # Stage 1: Laundry done
            WASHER_RUNNING = False
            LAUNDRY_FINISHED_AT = _now()
            REMINDER_STAGE = 1
            print("✅ Laundry done (Stage 1) — no motion detected for 180 seconds.")
            _say("Laundry is done when you’re ready.")
            return {"action": "finished_stage1"}

        return {"action": "scanning_finish_window", "quiet_seconds": quiet_seconds}

    # If we get past expected+20 and it's still running, that means motion kept happening
    if elapsed > window_end:
        if not OVERRUN_MOTION_NOTIFIED:
            OVERRUN_MOTION_NOTIFIED = True
            print("⚠️ Motion detected, but cycle should be finished by now.")
            _say("Motion is still detected, but the cycle should be finished by now.")
        return {"action": "overrun_motion"}

    return {"action": "running_before_finish_window"}


def _reminder_engine() -> Dict[str, Any]:
    """
    Up to 3 total reminders max:
    - Stage 1 happens at finish detection.
    - If door not opened, Stage 2 at +30 min, Stage 3 at +90 min, then stop.
    If door opens, update_door_status stops everything.
    """
    global REMINDER_STAGE, LAUNDRY_FINISHED_AT

    if LAUNDRY_FINISHED_AT is None:
        return {"action": "no_finish_time"}
    if CYCLE_CANCELLED_BY_DOOR_OPEN:
        return {"action": "cancelled_by_door"}
    if DOOR_STATUS == "OPEN":
        return {"action": "door_open"}
    if SNOOZE_UNTIL is not None and _now() < SNOOZE_UNTIL:
        return {"action": "snoozed"}

    mins_since_finish = _elapsed_minutes(LAUNDRY_FINISHED_AT)
    if mins_since_finish is None:
        return {"action": "unknown"}

    # Stage 2
    if REMINDER_STAGE < 2 and mins_since_finish >= REMINDER_STAGE2_AFTER_MIN:
        REMINDER_STAGE = 2
        print("💧 Reminder Stage 2: Clothes may be sitting wet.")
        _say("Reminder. Clothes may still be in the washer.")
        return {"action": "reminder_stage2"}

    # Stage 3
    if REMINDER_STAGE < 3 and mins_since_finish >= REMINDER_STAGE3_AFTER_MIN:
        REMINDER_STAGE = 3
        print("🔕 Reminder Stage 3: Stopping further reminders.")
        _say("Please empty the washer and move to the dryer to avoid mold growth. Stopping further reminders.")
        return {"action": "reminder_stage3_stop"}

    return {"action": "no_reminder"}


# =============================================================================
# Automatic background loop (NO user updates needed)
# =============================================================================

def _auto_loop(stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        # Always evaluate early false positive
        _check_early_false_positive()
        # Always evaluate almost-done once running
        _maybe_almost_done_alert()

        # Always evaluate finish logic if running
        _check_finish_logic()

        # Always evaluate reminders if finished
        _reminder_engine()

        stop_event.wait(AUTO_CHECK_INTERVAL_SECONDS)


# =============================================================================
# DEMO UI
# =============================================================================

def run_demo():
    print("\n" + "=" * 60)
    print("LAUNDRY DEMO - HelpingHome (Fully Automatic)")
    print("=" * 60)

    print("\nControls:")
    print("  time <minutes>   -> set expected cycle minutes (default 45)")
    print("  open             -> door OPEN")
    print("  close            -> door CLOSED")
    print("  vib <0..1>        -> vibration reading (e.g., vib 1.0)")
    print("  fast <minutes>   -> fast-forward time")
    print("  status           -> print current state")
    print("  q                -> quit")

    stop_event = threading.Event()
    bg = threading.Thread(target=_auto_loop, args=(stop_event,), daemon=True)
    bg.start()

    try:
        while True:
            cmd = input("\n> ").strip().lower()
            if cmd == "q":
                break

            if cmd.startswith("time "):
                try:
                    m = int(cmd.split(" ", 1)[1].strip())
                    set_expected_cycle_minutes(m)
                except ValueError:
                    print("Use: time 45")

            elif cmd == "open":
                update_door_status("OPEN")

            elif cmd == "close":
                update_door_status("CLOSED")

            elif cmd.startswith("vib "):
                try:
                    v = float(cmd.split(" ", 1)[1].strip())
                    update_vibration(v)
                except ValueError:
                    print("Use: vib 1.0")

            elif cmd.startswith("fast "):
                try:
                    mins = float(cmd.split(" ", 1)[1].strip())
                    _advance_time(mins)
                    print(f"⏩ Fast-forwarded {mins} minutes")
                except ValueError:
                    print("Use: fast 30")

            elif cmd == "status":
                _print_status()

            else:
                print("Unknown command.")
    finally:
        stop_event.set()


def _advance_time(minutes: float) -> None:
    """Simulate time passing by shifting internal timestamps backward."""
    seconds = minutes * 60
    global WASHER_STARTED_AT, LAST_VIBRATION_TIME, LAUNDRY_FINISHED_AT, SNOOZE_UNTIL
    global LAST_DOOR_OPENED_AT, LAST_DOOR_CLOSED_AT

    if WASHER_STARTED_AT is not None:
        WASHER_STARTED_AT -= seconds
    if LAST_VIBRATION_TIME is not None:
        LAST_VIBRATION_TIME -= seconds
    if LAUNDRY_FINISHED_AT is not None:
        LAUNDRY_FINISHED_AT -= seconds
    if SNOOZE_UNTIL is not None:
        SNOOZE_UNTIL -= seconds
    if LAST_DOOR_OPENED_AT is not None:
        LAST_DOOR_OPENED_AT -= seconds
    if LAST_DOOR_CLOSED_AT is not None:
        LAST_DOOR_CLOSED_AT -= seconds


def _print_status() -> None:
    elapsed = _elapsed_minutes(WASHER_STARTED_AT) if WASHER_STARTED_AT else None
    quiet = int(_now() - LAST_VIBRATION_TIME) if LAST_VIBRATION_TIME else None
    print("\n--- STATUS ---")
    print(f"Expected minutes: {EXPECTED_CYCLE_MINUTES}")
    print(f"Door: {DOOR_STATUS} (armed={CYCLE_ARMED})")
    print(f"Running: {WASHER_RUNNING}")
    print(f"Elapsed minutes: {None if elapsed is None else round(elapsed, 2)}")
    print(f"Last vibration level: {LAST_VIBRATION_LEVEL}")
    print(f"Quiet seconds: {quiet}")
    print(f"Finished at: {LAUNDRY_FINISHED_AT}")
    print(f"Reminder stage: {REMINDER_STAGE}")
    print(f"Cancelled by door open: {CYCLE_CANCELLED_BY_DOOR_OPEN}")
    print("--------------")


if __name__ == "__main__":
    run_demo()
