"""
Kitchen Demo for HelpingHome - Autism Assistance Application
Simulates Indistinguishable From Magic hardware interactions
"""

import time
import sys
import os
import csv
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path so imports work when running this file directly
_script_dir = os.path.dirname(os.path.abspath(__file__))  # rooms/kitchen/
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
    import traceback
    traceback.print_exc()


# ============================================================================
# CONFIGURATION VARIABLES - Adjust these to test different scenarios
# ============================================================================

# 1. Sensory Sensitivities (Sound & Light) - HARDCODED THRESHOLDS
SOUND_THRESHOLD_DB = 60  # Decibel threshold for loud noise detection
CURRENT_SOUND_LEVEL = 50  # Current sound level reading (dB)
AMBIENT_LIGHT_LEVEL = 50  # Light level threshold (lux)
CURRENT_LIGHT_LEVEL = 50  # Current light level reading (lux)
CALM_DOWN_COLOR = "blue"  # RGB LED color for calm down scene
RELAY_CUTOFF_ENABLED = True  # Whether to cut power to loud devices

# 2. Executive Functioning (Sequencing & Memory)
RECIPE_STEPS = ["WASH", "CHOP", "MIX", "COOK", "SERVE"]  # Recipe sequence
CURRENT_STEP = 0  # Current step in recipe (0-indexed)
TIMER_DURATION_SECONDS = 300  # 5 minutes default timer
TIMER_ACTIVE = False
TIMER_START_TIME = None

# 3. Safety Awareness (Stove & Heat)
STOVE_TEMP_THRESHOLD_C = 50  # Temperature threshold in Celsius
STOVE_TEMP_CURRENT = 25  # Current stove temperature reading (°C)
MOTION_DETECTED = True  # Whether motion is currently detected
MOTION_TIMEOUT_SECONDS = 300  # 5 minutes of no motion triggers alert
LAST_MOTION_TIME = None
SAFETY_ALERT_ACTIVE = False

# 4. Emotional Regulation (Stress & Frustration)
PAUSE_BUTTON_PRESSED = False  # Panic/Pause button state
DEESCALATION_MODE_ACTIVE = False
SAFE_SONG = "Calming Nature Sounds"  # Pre-selected safe song
LIGHTS_DIMMED = False

# Logging (main events only)
CSV_LOG_DIR = os.path.join(project_root, "data")
CSV_LOG_PREFIX = "kitchen_log"
CSV_COLUMNS = ["timestamp", "event_type", "detail", "value"]


def _log_csv(event_type: str, detail: Optional[str] = None, value: Optional[float] = None) -> None:
    os.makedirs(CSV_LOG_DIR, exist_ok=True)
    day = datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(CSV_LOG_DIR, f"{CSV_LOG_PREFIX}_{day}.csv")
    row = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "event_type": event_type,
        "detail": detail,
        "value": value,
    }
    file_exists = os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


# ============================================================================
# FUNCTION 1: Sensory Sensitivities (Sound & Light)
# ============================================================================

def check_sound_level(db_level: float) -> Dict[str, any]:
    """
    Monitor sound levels and trigger calm down scene if too loud.
    
    Args:
        db_level: Current decibel reading from sound sensor
        
    Returns:
        Dictionary with action taken and status
    """
    global CALM_DOWN_COLOR, RELAY_CUTOFF_ENABLED
    
    if db_level > SOUND_THRESHOLD_DB:
        # Trigger "Calm Down" Scene
        print(f"🔵 SOUND ALERT: {db_level}dB detected (threshold: {SOUND_THRESHOLD_DB}dB)")
        print(f"   → Activating calm down scene: {CALM_DOWN_COLOR.upper()} LED pulsing")
        _log_csv("sound_alert", detail="db_level", value=db_level)
        
        # Play audio warning
        if AUDIO_AVAILABLE and speak_text:
            print(f"[DEBUG] Audio available, calling speak_text...")
            warning_msg = f"Warning. Loud noise detected. {int(db_level)} decibels. Please prepare for the sound."
            speak_text(warning_msg)
        else:
            print(f"[DEBUG] Audio not available. AUDIO_AVAILABLE={AUDIO_AVAILABLE}, speak_text={speak_text}")
        
        if RELAY_CUTOFF_ENABLED and db_level > 90:
            print(f"   → ⚠️  CRITICAL: Cutting power to appliance (noise > 90dB)")
            if AUDIO_AVAILABLE and speak_text:
                speak_text("Critical alert. Very loud noise detected. Cutting power to appliance.")
            _log_csv("sound_critical", detail="db_level", value=db_level)
            return {
                "action": "calm_down_activated",
                "led_color": CALM_DOWN_COLOR,
                "relay_cutoff": True,
                "db_level": db_level
            }
        
        return {
            "action": "calm_down_activated",
            "led_color": CALM_DOWN_COLOR,
            "relay_cutoff": False,
            "db_level": db_level
        }
    
    return {
        "action": "normal",
        "db_level": db_level
    }


def adjust_ambient_light(light_level: int) -> Dict[str, any]:
    """
    Monitor and adjust ambient light to prevent harsh lighting.
    
    Args:
        light_level: Current ambient light level (0-100)
        
    Returns:
        Dictionary with light status
    """
    if light_level > AMBIENT_LIGHT_LEVEL:
        print(f"💡 LIGHT ALERT: Harsh lighting detected ({light_level} lux)")
        print(f"   → Suggesting dimming or moving to softer area")
        _log_csv("light_alert", detail="lux", value=float(light_level))
        
        # Play audio warning
        if AUDIO_AVAILABLE and speak_text:
            warning_msg = f"Warning. Harsh lighting detected. {light_level} lux. Consider dimming the lights or moving to a softer area."
            speak_text(warning_msg)
        
        return {
            "action": "light_too_bright",
            "suggested_level": 50,
            "current_level": light_level
        }
    
    return {
        "action": "normal",
        "light_level": light_level
    }


# ============================================================================
# FUNCTION 2: Executive Functioning (Sequencing & Memory)
# ============================================================================

def step_complete() -> Dict[str, any]:
    """
    Handle recipe step completion via button press.
    Increments step counter and displays next instruction.
    
    Returns:
        Dictionary with current step info
    """
    global CURRENT_STEP, RECIPE_STEPS
    
    if CURRENT_STEP < len(RECIPE_STEPS):
        current_task = RECIPE_STEPS[CURRENT_STEP]
        print(f"✅ STEP {CURRENT_STEP + 1} COMPLETE: {current_task}")
        _log_csv("step_complete", detail=current_task, value=float(CURRENT_STEP + 1))
        
        CURRENT_STEP += 1
        
        if CURRENT_STEP < len(RECIPE_STEPS):
            next_task = RECIPE_STEPS[CURRENT_STEP]
            print(f"   → NEXT: {next_task}")
            # Play audio for next step
            if AUDIO_AVAILABLE and speak_text:
                step_msg = f"Step {CURRENT_STEP} complete. Next step: {next_task}."
                speak_text(step_msg)
            return {
                "action": "step_complete",
                "completed_step": current_task,
                "next_step": next_task,
                "step_number": CURRENT_STEP,
                "total_steps": len(RECIPE_STEPS)
            }
        else:
            print(f"   → 🎉 RECIPE COMPLETE!")
            # Play audio for recipe completion
            if AUDIO_AVAILABLE and speak_text:
                speak_text("Recipe complete. Great job!")
            _log_csv("recipe_complete", detail=current_task, value=float(CURRENT_STEP))
            return {
                "action": "recipe_complete",
                "completed_step": current_task,
                "step_number": CURRENT_STEP,
                "total_steps": len(RECIPE_STEPS)
            }
    
    return {
        "action": "no_more_steps",
        "step_number": CURRENT_STEP
    }


def start_timer(duration_seconds: int) -> Dict[str, any]:
    """
    Start a visual timer countdown.
    Timer value maps to LED strip brightness (visual timer bar).
    
    Args:
        duration_seconds: Timer duration in seconds
        
    Returns:
        Dictionary with timer status
    """
    global TIMER_ACTIVE, TIMER_START_TIME, TIMER_DURATION_SECONDS
    
    TIMER_ACTIVE = True
    TIMER_START_TIME = time.time()
    TIMER_DURATION_SECONDS = duration_seconds
    
    print(f"⏱️  TIMER STARTED: {duration_seconds} seconds ({duration_seconds // 60} minutes)")
    print(f"   → LED strip showing visual countdown")
    _log_csv("timer_started", detail="seconds", value=float(duration_seconds))
    
    return {
        "action": "timer_started",
        "duration": duration_seconds,
        "start_time": TIMER_START_TIME
    }


def check_timer() -> Dict[str, any]:
    """
    Check timer status and update LED strip brightness.
    
    Returns:
        Dictionary with timer status and remaining time
    """
    global TIMER_ACTIVE, TIMER_START_TIME, TIMER_DURATION_SECONDS
    
    if not TIMER_ACTIVE or TIMER_START_TIME is None:
        return {
            "action": "timer_inactive",
            "remaining": 0
        }
    
    elapsed = time.time() - TIMER_START_TIME
    remaining = max(0, TIMER_DURATION_SECONDS - elapsed)
    brightness = int((remaining / TIMER_DURATION_SECONDS) * 100)  # 0-100%
    
    if remaining <= 0:
        TIMER_ACTIVE = False
        print(f"⏰ TIMER COMPLETE!")
        # Play audio for timer completion
        if AUDIO_AVAILABLE and speak_text:
            speak_text("Timer complete.")
        _log_csv("timer_complete")
        return {
            "action": "timer_complete",
            "remaining": 0,
            "brightness": 0
        }
    
    return {
        "action": "timer_running",
        "remaining": int(remaining),
        "brightness": brightness,
        "elapsed": int(elapsed)
    }


def reset_recipe() -> None:
    """Reset recipe to beginning."""
    global CURRENT_STEP
    CURRENT_STEP = 0
    print("🔄 Recipe reset to beginning")
    _log_csv("recipe_reset")


# ============================================================================
# FUNCTION 3: Safety Awareness (Stove & Heat)
# ============================================================================

def check_stove_safety(temp_celsius: float, motion_detected: bool) -> Dict[str, any]:
    """
    Monitor stove temperature and motion to detect safety issues.
    
    Args:
        temp_celsius: Current stove temperature
        motion_detected: Whether motion is currently detected
        
    Returns:
        Dictionary with safety status
    """
    global STOVE_TEMP_CURRENT, MOTION_DETECTED, LAST_MOTION_TIME, SAFETY_ALERT_ACTIVE
    
    STOVE_TEMP_CURRENT = temp_celsius
    MOTION_DETECTED = motion_detected
    
    if motion_detected:
        LAST_MOTION_TIME = time.time()
    
    # Check if stove is hot
    if temp_celsius > STOVE_TEMP_THRESHOLD_C:
        # Stove is hot - check motion status
        if not motion_detected:
            # No motion detected - check how long
            if LAST_MOTION_TIME is None:
                # Never had motion recorded - set it to now minus timeout to trigger alert
                LAST_MOTION_TIME = time.time() - MOTION_TIMEOUT_SECONDS - 1
            
            time_since_motion = time.time() - LAST_MOTION_TIME
            
            if time_since_motion > MOTION_TIMEOUT_SECONDS:
                # No motion for too long - SAFETY ALERT
                if not SAFETY_ALERT_ACTIVE:
                    SAFETY_ALERT_ACTIVE = True
                    print(f"🔥 SAFETY ALERT: Stove is hot ({temp_celsius}°C) and no motion detected for {int(time_since_motion)}s")
                    print(f"   → Playing gentle chime reminder")
                    print(f"   → Consider cutting power if user doesn't return")
                    _log_csv("safety_alert", detail="stove_hot_no_motion", value=float(temp_celsius))
                    
                    # Play audio safety alert
                    if AUDIO_AVAILABLE and speak_text:
                        alert_msg = f"Safety alert. Stove is hot at {int(temp_celsius)} degrees. No motion detected for {int(time_since_motion // 60)} minutes. Please return to the kitchen."
                        speak_text(alert_msg)
                    
                    return {
                        "action": "safety_alert",
                        "temp": temp_celsius,
                        "time_since_motion": int(time_since_motion),
                        "should_cut_power": True
                    }
            else:
                # Stove is hot but motion was recent - just warn about heat
                print(f"⚠️  WARNING: Stove is hot ({temp_celsius}°C) - monitoring for safety")
                if AUDIO_AVAILABLE and speak_text:
                    warning_msg = f"Warning. Stove is hot at {int(temp_celsius)} degrees. Please monitor carefully."
                    speak_text(warning_msg)
                return {
                    "action": "stove_hot_warning",
                    "temp": temp_celsius,
                    "motion_detected": False,
                    "time_since_motion": int(time_since_motion)
                }
        else:
            # Motion detected - stove is hot but user is present
            print(f"⚠️  WARNING: Stove is hot ({temp_celsius}°C) - motion detected, monitoring")
            if AUDIO_AVAILABLE and speak_text:
                warning_msg = f"Warning. Stove is hot at {int(temp_celsius)} degrees. Motion detected. Please monitor carefully."
                speak_text(warning_msg)
            return {
                "action": "stove_hot_monitoring",
                "temp": temp_celsius,
                "motion_detected": True
            }
    
    # Stove is cool - reset alert
    SAFETY_ALERT_ACTIVE = False
    if temp_celsius <= STOVE_TEMP_THRESHOLD_C:
        print(f"✓ Stove temperature: {temp_celsius}°C (normal, threshold: {STOVE_TEMP_THRESHOLD_C}°C)")
    return {
        "action": "normal",
        "temp": temp_celsius,
        "motion_detected": motion_detected
    }


# ============================================================================
# FUNCTION 4: Emotional Regulation (Stress & Frustration)
# ============================================================================

def press_pause_button() -> Dict[str, any]:
    """
    Handle panic/pause button press for de-escalation.
    
    Returns:
        Dictionary with de-escalation actions taken
    """
    global PAUSE_BUTTON_PRESSED, DEESCALATION_MODE_ACTIVE, LIGHTS_DIMMED, TIMER_ACTIVE
    
    PAUSE_BUTTON_PRESSED = True
    DEESCALATION_MODE_ACTIVE = True
    LIGHTS_DIMMED = True
    
    # Save timer state (pause it)
    timer_state = {
        "active": TIMER_ACTIVE,
        "remaining": check_timer().get("remaining", 0) if TIMER_ACTIVE else 0
    }
    
    print(f"🛑 PAUSE BUTTON PRESSED - Activating De-escalation Mode")
    print(f"   → Saving timer state: {timer_state}")
    print(f"   → Dimming lights")
    print(f"   → Playing safe song: '{SAFE_SONG}'")
    print(f"   → Environment is now calmer")
    _log_csv("deescalation_activated", detail=SAFE_SONG)
    
    # Play calming audio message
    if AUDIO_AVAILABLE and speak_text:
        calm_msg = f"De-escalation mode activated. Taking a break. Environment is now calmer. Playing {SAFE_SONG}."
        speak_text(calm_msg)
    
    return {
        "action": "deescalation_activated",
        "lights_dimmed": True,
        "safe_song": SAFE_SONG,
        "timer_saved": timer_state
    }


def exit_deescalation_mode() -> Dict[str, any]:
    """
    Exit de-escalation mode and restore normal state.
    
    Returns:
        Dictionary with restoration status
    """
    global PAUSE_BUTTON_PRESSED, DEESCALATION_MODE_ACTIVE, LIGHTS_DIMMED
    
    PAUSE_BUTTON_PRESSED = False
    DEESCALATION_MODE_ACTIVE = False
    LIGHTS_DIMMED = False
    
    print(f"✅ Exiting de-escalation mode - Restoring normal environment")
    _log_csv("deescalation_exited")
    
    return {
        "action": "deescalation_exited",
        "lights_restored": True
    }


# Configuration setup functions removed - all thresholds are hardcoded above


# ============================================================================
# DEMO MODE - Interactive Testing
# ============================================================================

def run_demo():
    """Run interactive demo to test all kitchen functions."""
    print("\n" + "="*60)
    print("KITCHEN DEMO - HelpingHome Autism Assistance")
    print("="*60)
    print("\nAvailable demos:")
    print("1. Sensory Sensitivities (Sound & Light)")
    print("2. Executive Functioning (Recipe Steps & Timer)")
    print("3. Safety Awareness (Stove & Heat)")
    print("4. Emotional Regulation (Pause Button)")
    print("5. Run All Demos")
    print("0. Exit")
    
    while True:
        try:
            choice = input("\nSelect demo (0-5): ").strip()
            
            if choice == "0":
                print("Exiting demo...")
                break
            elif choice == "1":
                demo_sensory()
            elif choice == "2":
                demo_executive_functioning()
            elif choice == "3":
                demo_safety()
            elif choice == "4":
                demo_emotional_regulation()
            elif choice == "5":
                demo_all()
            else:
                print("Invalid choice. Please select 0-5.")
        except KeyboardInterrupt:
            print("\n\nExiting demo...")
            break


def demo_sensory():
    """Input sensor readings - react if thresholds crossed."""
    global CURRENT_SOUND_LEVEL, CURRENT_LIGHT_LEVEL
    
    print("\n" + "-"*60)
    print("DEMO 1: Sensory Sensitivities")
    print("-"*60)
    print(f"\nThresholds (hardcoded):")
    print(f"  Sound: {SOUND_THRESHOLD_DB}dB")
    print(f"  Light: {AMBIENT_LIGHT_LEVEL} lux")
    print("\nEnter sensor readings:")
    print("  Sound level (dB) - just enter number")
    print("  Light level (lux) - enter 'l' + number")
    print("  'q' to quit\n")
    
    while True:
        try:
            user_input = input("Enter reading: ").strip().lower()
            
            if user_input == 'q':
                break
            elif user_input.startswith('l'):
                try:
                    light_val = int(float(user_input[1:].strip()))
                    CURRENT_LIGHT_LEVEL = light_val
                    # Check if threshold crossed and react
                    if CURRENT_LIGHT_LEVEL > AMBIENT_LIGHT_LEVEL:
                        adjust_ambient_light(CURRENT_LIGHT_LEVEL)
                    else:
                        print(f"✓ Light level: {CURRENT_LIGHT_LEVEL} lux (normal, threshold: {AMBIENT_LIGHT_LEVEL} lux)")
                except ValueError:
                    print("Invalid input. Use 'l' + number (e.g., 'l90')")
            else:
                try:
                    sound_val = float(user_input)
                    CURRENT_SOUND_LEVEL = sound_val
                    # Check if threshold crossed and react
                    if CURRENT_SOUND_LEVEL > SOUND_THRESHOLD_DB:
                        check_sound_level(CURRENT_SOUND_LEVEL)
                    else:
                        print(f"✓ Sound level: {CURRENT_SOUND_LEVEL}dB (normal, threshold: {SOUND_THRESHOLD_DB}dB)")
                except ValueError:
                    print("Invalid input. Enter a number for sound level.")
            
        except KeyboardInterrupt:
            break
    
    print("\nExiting...")


def demo_executive_functioning():
    """Input actions - react to step completion and timer."""
    global CURRENT_STEP, TIMER_ACTIVE
    
    print("\n" + "-"*60)
    print("DEMO 2: Executive Functioning")
    print("-"*60)
    print(f"\nRecipe steps (hardcoded): {', '.join(RECIPE_STEPS)}")
    print(f"Current step: {CURRENT_STEP + 1 if CURRENT_STEP < len(RECIPE_STEPS) else 'Complete'}")
    print("\nInput actions:")
    print("  's' - step complete button pressed")
    print("  't' + number - timer started (seconds)")
    print("  'q' - quit")
    print()
    
    while True:
        try:
            user_input = input("Enter action: ").strip().lower()
            
            if user_input == 'q':
                break
            elif user_input == 's':
                step_complete()
            elif user_input.startswith('t'):
                try:
                    timer_val = int(user_input[1:].strip())
                    start_timer(timer_val)
                    # Check timer status immediately
                    status = check_timer()
                    if status["action"] == "timer_running":
                        print(f"⏱️  Timer: {status['remaining']}s remaining, LED brightness: {status['brightness']}%")
                except ValueError:
                    print("Invalid input. Use 't' + number (e.g., 't300')")
            else:
                print("Unknown command. Use 's', 't', or 'q'")
            
        except KeyboardInterrupt:
            break
    
    print("\nExiting...")


def demo_safety():
    """Input sensor readings - react if thresholds crossed."""
    global STOVE_TEMP_CURRENT, MOTION_DETECTED, LAST_MOTION_TIME, SAFETY_ALERT_ACTIVE
    
    if LAST_MOTION_TIME is None:
        LAST_MOTION_TIME = time.time()
    
    print("\n" + "-"*60)
    print("DEMO 3: Safety Awareness")
    print("-"*60)
    print(f"\nThresholds (hardcoded):")
    print(f"  Stove temp: {STOVE_TEMP_THRESHOLD_C}°C")
    print(f"  Motion timeout: {MOTION_TIMEOUT_SECONDS}s")
    print("\nEnter sensor readings:")
    print("  Temperature (°C) - just enter number")
    print("  Motion - 'm' for motion detected, 'n' for no motion")
    print("  'q' to quit")
    print()
    
    while True:
        try:
            user_input = input("Enter reading: ").strip().lower()
            
            if user_input == 'q':
                break
            elif user_input == 'm':
                MOTION_DETECTED = True
                LAST_MOTION_TIME = time.time()
                print(f"✓ Motion: Detected")
                # Check safety with current temp
                check_stove_safety(STOVE_TEMP_CURRENT, MOTION_DETECTED)
            elif user_input == 'n':
                MOTION_DETECTED = False
                print(f"✓ Motion: Not detected")
                # Check safety with current temp
                check_stove_safety(STOVE_TEMP_CURRENT, MOTION_DETECTED)
            else:
                try:
                    temp_val = float(user_input)
                    STOVE_TEMP_CURRENT = temp_val
                    # Check if threshold crossed and react
                    check_stove_safety(STOVE_TEMP_CURRENT, MOTION_DETECTED)
                except ValueError:
                    print("Invalid input. Enter a number for temperature or 'm'/'n' for motion.")
            
        except KeyboardInterrupt:
            break
    
    print("\nExiting...")


def demo_emotional_regulation():
    """Input actions - react to pause button press."""
    global PAUSE_BUTTON_PRESSED, DEESCALATION_MODE_ACTIVE
    
    print("\n" + "-"*60)
    print("DEMO 4: Emotional Regulation")
    print("-"*60)
    print(f"\nSafe song (hardcoded): {SAFE_SONG}")
    print("\nInput actions:")
    print("  'p' - pause button pressed")
    print("  'e' - exit de-escalation mode")
    print("  'q' - quit")
    print()
    
    while True:
        try:
            user_input = input("Enter action: ").strip().lower()
            
            if user_input == 'q':
                break
            elif user_input == 'p':
                if not DEESCALATION_MODE_ACTIVE:
                    press_pause_button()
                else:
                    print("De-escalation already active")
            elif user_input == 'e':
                if DEESCALATION_MODE_ACTIVE:
                    exit_deescalation_mode()
                else:
                    print("Not in de-escalation mode")
            else:
                print("Unknown command. Use 'p', 'e', or 'q'")
            
        except KeyboardInterrupt:
            break
    
    print("\nExiting...")


def demo_all():
    """Input sensor readings for all systems - react if thresholds crossed."""
    global CURRENT_SOUND_LEVEL, CURRENT_LIGHT_LEVEL, STOVE_TEMP_CURRENT, MOTION_DETECTED, LAST_MOTION_TIME
    
    if LAST_MOTION_TIME is None:
        LAST_MOTION_TIME = time.time()
    
    print("\n" + "="*60)
    print("DEMO: All Systems")
    print("="*60)
    print(f"\nThresholds (hardcoded):")
    print(f"  Sound: {SOUND_THRESHOLD_DB}dB")
    print(f"  Light: {AMBIENT_LIGHT_LEVEL} lux")
    print(f"  Stove temp: {STOVE_TEMP_THRESHOLD_C}°C")
    print(f"  Motion timeout: {MOTION_TIMEOUT_SECONDS}s")
    print(f"\nRecipe steps: {', '.join(RECIPE_STEPS)}")
    print(f"Safe song: {SAFE_SONG}")
    print("\nEnter sensor readings/actions:")
    print("  Sound: number (dB)")
    print("  Light: 'l' + number (lux)")
    print("  Temp: 't' + number (°C)")
    print("  Motion: 'm' (detected) or 'n' (not detected)")
    print("  Step: 's' (complete step)")
    print("  Timer: 'timer' + number (seconds)")
    print("  Pause: 'p' (press pause button)")
    print("  Exit: 'e' (exit de-escalation)")
    print("  Quit: 'q'")
    print()
    
    while True:
        try:
            user_input = input("Enter reading/action: ").strip().lower()
            
            if user_input == 'q':
                break
            elif user_input.startswith('l'):
                try:
                    CURRENT_LIGHT_LEVEL = int(float(user_input[1:].strip()))
                    if CURRENT_LIGHT_LEVEL > AMBIENT_LIGHT_LEVEL:
                        adjust_ambient_light(CURRENT_LIGHT_LEVEL)
                    else:
                        print(f"✓ Light: {CURRENT_LIGHT_LEVEL} lux (normal)")
                except ValueError:
                    print("Invalid light level")
            elif user_input.startswith('t'):
                try:
                    STOVE_TEMP_CURRENT = float(user_input[1:].strip())
                    check_stove_safety(STOVE_TEMP_CURRENT, MOTION_DETECTED)
                except ValueError:
                    print("Invalid temperature")
            elif user_input == 'm':
                MOTION_DETECTED = True
                LAST_MOTION_TIME = time.time()
                print(f"✓ Motion: Detected")
                check_stove_safety(STOVE_TEMP_CURRENT, MOTION_DETECTED)
            elif user_input == 'n':
                MOTION_DETECTED = False
                print(f"✓ Motion: Not detected")
                check_stove_safety(STOVE_TEMP_CURRENT, MOTION_DETECTED)
            elif user_input == 's':
                step_complete()
            elif user_input.startswith('timer'):
                try:
                    timer_val = int(user_input[5:].strip())
                    start_timer(timer_val)
                    status = check_timer()
                    if status["action"] == "timer_running":
                        print(f"⏱️  Timer: {status['remaining']}s remaining")
                except ValueError:
                    print("Invalid timer value")
            elif user_input == 'p':
                press_pause_button()
            elif user_input == 'e':
                exit_deescalation_mode()
            else:
                try:
                    CURRENT_SOUND_LEVEL = float(user_input)
                    if CURRENT_SOUND_LEVEL > SOUND_THRESHOLD_DB:
                        check_sound_level(CURRENT_SOUND_LEVEL)
                    else:
                        print(f"✓ Sound: {CURRENT_SOUND_LEVEL}dB (normal)")
                except ValueError:
                    print("Unknown command")
            
        except KeyboardInterrupt:
            break
    
    print("\nExiting...")


if __name__ == "__main__":
    run_demo()
