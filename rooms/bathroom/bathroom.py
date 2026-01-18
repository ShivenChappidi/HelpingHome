# Bathroom room module for autism assistance application
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
# DEMO MENUS
# ============================================================================

def run_sensory_demo():
    print("\n--- SENSORY DEMO (Thermal & Noise) ---")
    while True:
        print("\nPlease enter sensor readings (or 'q' to quit):")
        noise = get_valid_number("Enter Noise Level (dB):")
        if noise == 'q': break
        
        temp = get_valid_number("Enter Water Temp (°C):")
        if temp == 'q': break
        
        process_sensory(noise, temp)

def run_hygiene_demo():
    print("\n--- HYGIENE DEMO (Hand Washing) ---")
    print("Actions: 'walk', 'wave', 'soap', 'wait', 'leave'")
    print("(Sequence will exit automatically when complete)")
    
    while True:
        action = input("\nUser Action > ").strip().lower()
        if action == 'q': break
        
        if action in ['walk', 'wave', 'soap', 'wait', 'leave']:
            finished = process_hygiene(action)
            if finished:
                print(">>> Sequence Complete. Returning to Main Menu.")
                break
        else:
            print("❌ Invalid action. Try: walk, wave, soap, wait, leave")

def run_safety_demo():
    print("\n--- SAFETY DEMO (Flood/Ghost Tap) ---")
    while True:
        print("\nContext: checking for running water in empty room.")
        noise = get_valid_number("Current Noise Level (dB):")
        if noise == 'q': break
        
        motion_in = input("Is motion detected? (y/n): ").strip().lower()
        if motion_in == 'q': break
        
        has_motion = (motion_in == 'y')
        alert_triggered = process_safety(noise, has_motion)
        
        if alert_triggered:
            print(">>> Alert Active. (Simulate user returning with 'y' motion next to resolve)")

def run_routine_demo():
    print("\n--- ROUTINE DEMO (Toilet Timer) ---")
    print("Simulate: 'sit' (Proximity High) or 'stand' (Proximity Low)")
    
    while True:
        cmd = input("\nUser State (sit/stand) > ").strip().lower()
        if cmd == 'q': break
        
        if cmd == 'sit':
            process_routine(True)
        elif cmd == 'stand':
            finished = process_routine(False)
            if finished:
                print(">>> Routine Complete. Returning to Main Menu.")
                break
        else:
            print("Invalid. Type 'sit' or 'stand'.")

def run_all_modules():
    """
    Run All Demo: Accepts commands for any module and routes them.
    Similar to Kitchen.py style.
    """
    print("\n" + "="*60)
    print("RUN ALL MODULES (Simulated Integration)")
    print("="*60)
    print("Commands:")
    print("  n[val]  -> Noise dB (e.g., n80)")
    print("  t[val]  -> Temp °C  (e.g., t45)")
    print("  walk/wave/soap/wait/leave -> Hygiene")
    print("  sit/stand -> Routine")
    print("  ghost   -> Simulate Ghost Tap (Loud+NoMotion)")
    print("  q       -> Exit")

    while True:
        cmd = input("\n[ALL] Input > ").strip().lower()
        if cmd == 'q': break

        # 1. Sensory Routing
        if cmd.startswith('n'):
            try:
                val = float(cmd[1:])
                # Use current state for temp
                process_sensory(val, 20.0) 
            except ValueError: print("Invalid format. Use n80")
        elif cmd.startswith('t'):
            try:
                val = float(cmd[1:])
                # Use current state for noise
                process_sensory(50.0, val)
            except ValueError: print("Invalid format. Use t45")
            
        # 2. Hygiene Routing
        elif cmd in ['walk', 'wave', 'soap', 'wait', 'leave']:
            process_hygiene(cmd)

        # 3. Routine Routing
        elif cmd == 'sit':
            process_routine(True)
        elif cmd == 'stand':
            process_routine(False)

        # 4. Safety Routing (Shortcut)
        elif cmd == 'ghost':
            process_safety(80, False) # Loud, No Motion
        
        else:
            print("Unknown command. Try: n80, t45, walk, sit, ghost")

def run_main_menu():
    print("\n" + "="*60)
    print("🛀 SMART BATHROOM - DEMO CONTROLLER")
    print("="*60)
    print("1. Sensory Regulation (Hot Water / Loud Noise)")
    print("2. Hygiene Assistant (Hand Washing)")
    print("3. Safety Monitor (Ghost Tap)")
    print("4. Routine Anchor (Toilet Timer)")
    print("5. Run All Modules (Integrated Mode)")
    print("0. Exit")
    
    while True:
        choice = input("\nSelect Option (0-5): ").strip()
        
        if choice == "1":
            run_sensory_demo()
        elif choice == "2":
            run_hygiene_demo()
        elif choice == "3":
            run_safety_demo()
        elif choice == "4":
            run_routine_demo()
        elif choice == "5":
            run_all_modules()
        elif choice == "0":
            print("Exiting System. Goodbye!")
            if AUDIO_AVAILABLE and speak_text:
                speak_text("System shutting down. Goodbye.")
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    run_main_menu()
