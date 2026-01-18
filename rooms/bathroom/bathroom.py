"""
Bathroom Module for HelpingHome - Autism Assistance Application
Focus: Sensory Regulation, Hygiene Sequencing, Safety, and Interoception.
"""

import time
import sys
import os
import random
from typing import Dict, Optional, Any

# Add project root to path so imports work when running this file directly
_script_dir = os.path.dirname(os.path.abspath(__file__))
_rooms_dir = os.path.dirname(_script_dir)
project_root = os.path.dirname(_rooms_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import Audio Utility
try:
    from utils.audio import speak_text
    AUDIO_AVAILABLE = True
except Exception as e:
    AUDIO_AVAILABLE = False
    speak_text = None
    print(f"[SYSTEM] Audio module warning: {e}")

# ============================================================================
# CONFIGURATION & THRESHOLDS
# ============================================================================

# 1. Sensory (Noise & Thermal)
NOISE_LIMIT_DB = 75           # dB level that triggers calming audio
TEMP_SCALD_C = 40.0           # °C - Water too hot
TEMP_COLD_C = 30.0            # °C - Water too cold

# 2. Hygiene (Hand Washing)
WASH_DURATION_SEC = 20        # Scrubbing time goal

# 3. Safety (Ghost Tap)
GHOST_TAP_TIMEOUT = 10        # Seconds of water running alone triggers alert

# 4. Routine (Toilet)
TOILET_LIMIT_SEC = 15         # Seconds before gentle reminder (Short for Demo)
PROXIMITY_SIT_VAL = 100       # Sensor value threshold for sitting

# State Variables
state = {
    "wash_step": 0,           # 0=Idle, 1=Water, 2=Soap, 3=Scrub, 4=Done
    "wash_timer_start": None,
    "last_motion_time": time.time(),
    "safety_alert_sent": False,
    "is_sitting": False,
    "sit_start_time": None,
    "calming_mode": False
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def announce(text: str, led_color: Optional[str] = None):
    """
    Central function to handle Audio + Terminal + LED feedback.
    """
    timestamp = time.strftime("%H:%M:%S")
    
    # 1. Terminal Print (Assistant Voice)
    print(f"[{timestamp}] 🗣️  ASSISTANT: \"{text}\"")
    
    # 2. LED Feedback
    if led_color:
        print(f"[{timestamp}] 💡 LED OUTPUT: Set to {led_color.upper()}")

    # 3. Audio Output (ElevenLabs)
    if AUDIO_AVAILABLE and speak_text:
        speak_text(text)

def log_caregiver(message: str):
    """Simulates logging an event to the Caregiver Dashboard/OpenNote."""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] 📝 LOG TO CAREGIVER: {message}")

def get_valid_number(prompt: str) -> float:
    """Robust input handler. Re-asks user if they type text instead of numbers."""
    while True:
        try:
            user_input = input(f"\n{prompt} ").strip().lower()
            if user_input == 'q':
                return 'q'
            return float(user_input)
        except ValueError:
            error_msg = "I didn't catch that number. Please enter a valid digit."
            print(f"❌ ERROR: Invalid input. Expecting a number.")
            if AUDIO_AVAILABLE and speak_text:
                speak_text(error_msg)

# ============================================================================
# CORE LOGIC MODULES
# ============================================================================

def process_sensory(noise_db: float, water_temp: float):
    """
    Handles Thermal and Noise sensors.
    Output: LED changes and Audio Warnings.
    """
    global state
    
    print(f"--- SENSOR CHECK: Noise={noise_db}dB | Temp={water_temp}°C ---")

    # 1. Thermal Logic
    if water_temp > TEMP_SCALD_C:
        announce("Warning. The water is very hot. Please be careful.", led_color="RED")
    elif water_temp < TEMP_COLD_C:
        announce("The water is quite cold.", led_color="BLUE")
    else:
        # Ideal temperature logic
        if not state["calming_mode"] and not state["is_sitting"]: 
             # Only show green if we aren't busy elsewhere
            print("💡 LED OUTPUT: Set to GREEN (Temp OK)")

    # 2. Auditory Logic
    if noise_db > NOISE_LIMIT_DB:
        if not state["calming_mode"]:
            state["calming_mode"] = True
            announce("It is getting loud. Playing calming sounds.", led_color="SOFT_ORANGE")
            print("🎵 [AUDIO SYSTEM] Playing: 'Nature_Sounds.mp3'")
    else:
        if state["calming_mode"]:
            state["calming_mode"] = False
            print("✓ Noise levels returned to normal. Fading music.")


def process_hygiene(action: str) -> bool:
    """
    Handles Hand Washing sequence.
    Returns: True if sequence finished/reset, False if still in progress.
    """
    global state
    
    # Logic Map
    if action == "walk" and state["wash_step"] == 0:
        state["wash_step"] = 1
        announce("Hi. Let's wash hands. Turn on the water.", led_color="WHITE")
        
    elif action == "wave" and state["wash_step"] == 1:
        state["wash_step"] = 2
        announce("Great. Now get some soap.", led_color="CYAN")
        
    elif action == "soap" and state["wash_step"] == 2:
        state["wash_step"] = 3
        state["wash_timer_start"] = time.time()
        announce("Scrub your hands while I count down.", led_color="PULSING_BLUE")
        print("⏳ [SYSTEM] 20-Second Timer Started...")
        
    elif action == "wait" and state["wash_step"] == 3:
        # Simulate timer finishing
        announce("Good job scrubbing. Rinse and dry your hands.", led_color="GREEN")
        state["wash_step"] = 4
        
    elif action == "leave":
        if state["wash_step"] == 4:
            announce("All done. Hands are clean!", led_color="OFF")
            state["wash_step"] = 0
            return True # Routine Complete
        elif state["wash_step"] > 0:
            announce("Please come back, we aren't finished yet.", led_color="YELLOW")
        else:
            print("✓ User left the area.")
            return True # Reset/Left

    return False


def process_safety(noise_db: float, motion_detected: bool) -> bool:
    """
    Handles Ghost Tap. 
    Returns: True if alert triggered, False otherwise.
    """
    global state
    
    if motion_detected:
        state["last_motion_time"] = time.time()
        if state["safety_alert_sent"]:
            state["safety_alert_sent"] = False
            log_caregiver("Safety Alert Resolved: User returned to bathroom.")
            announce("Welcome back.", led_color="GREEN")
        return False

    # Ghost Tap Check
    is_loud = noise_db > 55
    time_since_motion = time.time() - state["last_motion_time"]
    
    # Simulate time passing for demo logic
    if not motion_detected:
        # artificially add time to simulate a delay for the demo
        time_since_motion += GHOST_TAP_TIMEOUT + 1 

    if is_loud and time_since_motion > GHOST_TAP_TIMEOUT:
        if not state["safety_alert_sent"]:
            state["safety_alert_sent"] = True
            announce("Alert. The sink is running but nobody is here.", led_color="FLASHING_RED")
            log_caregiver("ALERT: Ghost Tap Detected (Running water + No Motion).")
            return True # Alert Triggered
            
    return False

def process_routine(is_sitting: bool) -> bool:
    """
    Handles Toilet Timing (Interoception).
    Returns: True if routine ended (stood up), False if ongoing.
    """
    global state
    
    if is_sitting and not state["is_sitting"]:
        # SIT DOWN EVENT
        state["is_sitting"] = True
        state["sit_start_time"] = time.time()
        announce("Timer started.", led_color="SOFT_BLUE")
        log_caregiver("User is using the toilet.")
        
    elif not is_sitting and state["is_sitting"]:
        # STAND UP EVENT
        state["is_sitting"] = False
        announce("Remember to wash your hands.", led_color="GREEN")
        log_caregiver("User finished using the toilet.")
        return True # Routine Complete

    # DURATION CHECK
    if state["is_sitting"]:
        elapsed = time.time() - state["sit_start_time"] + TOILET_LIMIT_SEC + 1
        
        if elapsed > TOILET_LIMIT_SEC:
            announce("Just checking in. Are you ready to finish up?", led_color="SOFT_PURPLE")
            log_caregiver("Routine Duration Limit Reached (Check-in sent).")
    
    return False

# ============================================================================
# DEMO MODE - Unified Input System
# ============================================================================

# Track current sensory values for unified processing
current_noise_db = 50.0
current_water_temp = 35.0
current_motion = True

def print_input_key():
    """Print the input key showing which letters correspond to which inputs."""
    print("\n" + "="*60)
    print("INPUT KEY - Letter Prefixes for Bathroom System")
    print("="*60)
    print("\nSensory Regulation:")
    print("  n<number>      - Noise level in decibels (e.g., 'n80' = 80 dB)")
    print("  w<number>      - Water temperature in Celsius (e.g., 'w45' = 45°C)")
    print("\nHygiene (Hand Washing):")
    print("  walk           - Walk to sink (start sequence)")
    print("  wave           - Wave hand at sensor (water detected)")
    print("  soap           - Apply soap")
    print("  wait           - Wait for scrubbing timer")
    print("  leave          - Leave sink area (complete)")
    print("\nSafety (Ghost Tap Detection):")
    print("  m              - Motion detected")
    print("  nm             - No motion detected")
    print("  ghost          - Simulate ghost tap (loud + no motion)")
    print("\nRoutine (Toilet Timer):")
    print("  sit            - User sits down (start timer)")
    print("  stand          - User stands up (end timer)")
    print("\nSystem Control:")
    print("  key            - Show this input key")
    print("  status         - Show current system status")
    print("  q              - Quit demo")
    print("="*60)


def show_system_status():
    """Display current status of all system sections."""
    global state, current_noise_db, current_water_temp, current_motion
    
    print("\n" + "-"*60)
    print("BATHROOM SYSTEM STATUS")
    print("-"*60)
    
    print("\nSensory Regulation:")
    print(f"  Noise: {current_noise_db}dB (threshold: {NOISE_LIMIT_DB}dB)")
    print(f"  Water temp: {current_water_temp}°C (scald: {TEMP_SCALD_C}°C, cold: {TEMP_COLD_C}°C)")
    print(f"  Calming mode: {'Active' if state['calming_mode'] else 'Inactive'}")
    
    print("\nHygiene (Hand Washing):")
    steps = ["Idle", "Turn on water", "Get soap", "Scrub", "Done"]
    step_name = steps[state['wash_step']] if state['wash_step'] < len(steps) else "Unknown"
    print(f"  Current step: {state['wash_step']} - {step_name}")
    
    print("\nSafety (Ghost Tap):")
    print(f"  Motion: {'Detected' if current_motion else 'Not detected'}")
    print(f"  Safety alert sent: {state['safety_alert_sent']}")
    
    print("\nRoutine (Toilet Timer):")
    print(f"  Sitting: {'Yes' if state['is_sitting'] else 'No'}")
    if state['is_sitting'] and state['sit_start_time']:
        elapsed = int(time.time() - state['sit_start_time'])
        print(f"  Time sitting: {elapsed} seconds")
    
    print("-"*60)


def parse_unified_input(user_input: str):
    """
    Parse unified input with letter prefixes and route to appropriate functions.
    All sections run simultaneously - inputs can be sent at any time.
    """
    global current_noise_db, current_water_temp, current_motion
    
    user_input = user_input.strip()
    if not user_input:
        return
    
    # System control commands
    if user_input == 'q':
        return 'quit'
    elif user_input == 'key':
        print_input_key()
        return
    elif user_input == 'status':
        show_system_status()
        return
    
    # Sensory Regulation
    if user_input.startswith('n'):
        try:
            noise_val = float(user_input[1:].strip())
            current_noise_db = noise_val
            process_sensory(current_noise_db, current_water_temp)
        except ValueError:
            print("Invalid input. Use 'n' + number (e.g., 'n80')")
    elif user_input.startswith('w'):
        try:
            temp_val = float(user_input[1:].strip())
            current_water_temp = temp_val
            process_sensory(current_noise_db, current_water_temp)
        except ValueError:
            print("Invalid input. Use 'w' + number (e.g., 'w45')")
    
    # Hygiene (Hand Washing)
    elif user_input in ['walk', 'wave', 'soap', 'wait', 'leave']:
        process_hygiene(user_input)
    
    # Safety (Ghost Tap)
    elif user_input == 'm':
        current_motion = True
        state["last_motion_time"] = time.time()
        process_safety(current_noise_db, current_motion)
    elif user_input == 'nm':
        current_motion = False
        process_safety(current_noise_db, current_motion)
    elif user_input == 'ghost':
        # Simulate ghost tap: loud + no motion
        process_safety(80, False)
    
    # Routine (Toilet Timer)
    elif user_input == 'sit':
        process_routine(True)
    elif user_input == 'stand':
        process_routine(False)
    
    else:
        print(f"Unknown command: '{user_input}'. Type 'key' to see input options.")


def run_demo():
    """
    Run unified demo with all systems running simultaneously.
    Inputs use letter prefixes to distinguish input types.
    """
    print("\n" + "="*60)
    print("BATHROOM SYSTEM DEMO - All Sections Running Simultaneously")
    print("="*60)
    print("\nAll sections are now active and monitoring simultaneously.")
    print("Send any input at any time using letter prefixes.")
    
    # Print input key
    print_input_key()
    
    print("\nSystem is running. Enter inputs below (type 'key' to see input options):")
    print()
    
    # Main input loop - all systems are active
    while True:
        try:
            user_input = input("> ").strip().lower()
            
            result = parse_unified_input(user_input)
            if result == 'quit':
                print("\nExiting demo...")
                if AUDIO_AVAILABLE and speak_text:
                    speak_text("System shutting down. Goodbye.")
                break
            
        except KeyboardInterrupt:
            print("\n\nExiting demo...")
            break


if __name__ == "__main__":
    run_demo()