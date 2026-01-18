"""
Kitchen Demo for HelpingHome - Autism Assistance Application
Simulates Indistinguishable From Magic hardware interactions
"""

import time
import sys
import os
from typing import Dict, List, Optional
from indistinguishable_from_magic import magic as Magic

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
# Recipe data structure (JSON-friendly for frontend integration)
# Format: {recipe_id: {"name": str, "steps": [str], "description": str}}
# This structure can be easily serialized to/from JSON for API integration
RECIPES = {
    "scrambled_eggs": {
        "name": "Scrambled Eggs",
        "description": "Simple scrambled eggs recipe",
        "steps": [
            "Gather ingredients: 2 eggs, butter, salt, pepper",
            "Crack eggs into a bowl",
            "Add salt and pepper, whisk gently",
            "Heat pan with butter over medium heat",
            "Pour eggs into pan",
            "Stir gently until cooked",
            "Serve on plate"
        ]
    },
    "pasta_basic": {
        "name": "Basic Pasta",
        "description": "Simple pasta with sauce",
        "steps": [
            "Fill pot with water and bring to boil",
            "Add pasta to boiling water",
            "Cook pasta for 8-10 minutes",
            "Drain pasta in colander",
            "Heat sauce in separate pan",
            "Mix pasta with sauce",
            "Serve in bowl"
        ]
    },
    "grilled_cheese": {
        "name": "Grilled Cheese Sandwich",
        "description": "Classic grilled cheese",
        "steps": [
            "Gather bread and cheese",
            "Butter one side of each bread slice",
            "Place cheese between bread slices",
            "Heat pan over medium heat",
            "Cook sandwich 2-3 minutes per side",
            "Check if golden brown",
            "Remove from pan and serve"
        ]
    },
    "smoothie": {
        "name": "Fruit Smoothie",
        "description": "Healthy fruit smoothie",
        "steps": [
            "Gather fruits: banana, berries, yogurt",
            "Wash fruits if needed",
            "Cut banana into chunks",
            "Add fruits to blender",
            "Add yogurt and ice",
            "Blend until smooth",
            "Pour into glass and serve"
        ]
    },
    "salad": {
        "name": "Simple Salad",
        "description": "Fresh green salad",
        "steps": [
            "Wash lettuce and vegetables",
            "Dry lettuce with paper towel",
            "Chop lettuce into bite-sized pieces",
            "Slice tomatoes and cucumbers",
            "Add vegetables to bowl",
            "Add dressing and toss",
            "Serve in salad bowl"
        ]
    }
}

CURRENT_RECIPE_ID = None  # ID of currently active recipe
CURRENT_RECIPE = None  # Full recipe dictionary
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

# 5. Proximity Detection for Loud Objects
PROXIMITY_THRESHOLD_CM = 15  # Distance threshold in centimeters (hand detected within this range)
LOUD_OBJECTS = ["blender", "garbage disposal", "food processor", "mixer"]  # List of loud objects
CURRENT_PROXIMITY_CM = 50  # Current proximity reading (cm) - default far away
CURRENT_NEAR_OBJECT = None  # Which loud object is currently being approached


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

def add_recipe(recipe_id: str, name: str, steps: List[str], description: str = "") -> Dict[str, any]:
    """
    Add a new recipe (for frontend integration).
    
    Args:
        recipe_id: Unique identifier for the recipe
        name: Display name of the recipe
        steps: List of step instructions
        description: Optional description of the recipe
        
    Returns:
        Dictionary with recipe info and status
    """
    RECIPES[recipe_id] = {
        "name": name,
        "steps": steps,
        "description": description
    }
    
    return {
        "action": "recipe_added",
        "recipe_id": recipe_id,
        "recipe_name": name,
        "total_steps": len(steps)
    }


def get_all_recipes() -> Dict[str, Dict[str, any]]:
    """
    Get all available recipes (for frontend integration).
    
    Returns:
        Dictionary of all recipes
    """
    return RECIPES.copy()


def load_recipe(recipe_id: str) -> Dict[str, any]:
    """
    Load a recipe by ID.
    
    Args:
        recipe_id: ID of the recipe to load
        
    Returns:
        Dictionary with recipe info and status
    """
    global CURRENT_RECIPE_ID, CURRENT_RECIPE, CURRENT_STEP
    
    if recipe_id not in RECIPES:
        return {
            "action": "recipe_not_found",
            "recipe_id": recipe_id,
            "error": f"Recipe '{recipe_id}' not found"
        }
    
    CURRENT_RECIPE_ID = recipe_id
    CURRENT_RECIPE = RECIPES[recipe_id]
    CURRENT_STEP = 0
    
    print(f"📋 Recipe loaded: {CURRENT_RECIPE['name']}")
    print(f"   Description: {CURRENT_RECIPE.get('description', 'No description')}")
    print(f"   Steps: {len(CURRENT_RECIPE['steps'])}")
    
    # Play audio announcement
    if AUDIO_AVAILABLE and speak_text:
        speak_text(f"Recipe loaded: {CURRENT_RECIPE['name']}. {len(CURRENT_RECIPE['steps'])} steps.")
    
    return {
        "action": "recipe_loaded",
        "recipe_id": recipe_id,
        "recipe_name": CURRENT_RECIPE['name'],
        "total_steps": len(CURRENT_RECIPE['steps']),
        "steps": CURRENT_RECIPE['steps']
    }


def step_complete() -> Dict[str, any]:
    """
    Handle recipe step completion via button press.
    Increments step counter and displays next instruction.
    
    Returns:
        Dictionary with current step info
    """
    global CURRENT_STEP, CURRENT_RECIPE
    
    if CURRENT_RECIPE is None:
        return {
            "action": "no_recipe_loaded",
            "error": "No recipe is currently loaded. Please select a recipe first."
        }
    
    recipe_steps = CURRENT_RECIPE['steps']
    
    if CURRENT_STEP < len(recipe_steps):
        current_task = recipe_steps[CURRENT_STEP]
        print(f"✅ STEP {CURRENT_STEP + 1} COMPLETE: {current_task}")
        
        CURRENT_STEP += 1
        
        if CURRENT_STEP < len(recipe_steps):
            next_task = recipe_steps[CURRENT_STEP]
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
                "total_steps": len(recipe_steps),
                "recipe_name": CURRENT_RECIPE['name']
            }
        else:
            print(f"   → 🎉 RECIPE COMPLETE!")
            # Play audio for recipe completion
            if AUDIO_AVAILABLE and speak_text:
                speak_text(f"Recipe complete. Great job! {CURRENT_RECIPE['name']} is ready.")
            return {
                "action": "recipe_complete",
                "completed_step": current_task,
                "step_number": CURRENT_STEP,
                "total_steps": len(recipe_steps),
                "recipe_name": CURRENT_RECIPE['name']
            }
    
    return {
        "action": "no_more_steps",
        "step_number": CURRENT_STEP,
        "recipe_name": CURRENT_RECIPE['name'] if CURRENT_RECIPE else None
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


def reset_recipe() -> Dict[str, any]:
    """Reset recipe to beginning."""
    global CURRENT_STEP, CURRENT_RECIPE
    
    if CURRENT_RECIPE is None:
        return {
            "action": "no_recipe_loaded",
            "error": "No recipe is currently loaded."
        }
    
    CURRENT_STEP = 0
    print(f"🔄 Recipe reset to beginning: {CURRENT_RECIPE['name']}")
    
    if AUDIO_AVAILABLE and speak_text:
        speak_text(f"Recipe reset. Starting {CURRENT_RECIPE['name']} from the beginning.")
    
    return {
        "action": "recipe_reset",
        "recipe_name": CURRENT_RECIPE['name'],
        "step_number": 0
    }


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
    
    return {
        "action": "deescalation_exited",
        "lights_restored": True
    }


# ============================================================================
# FUNCTION 5: Proximity Detection for Loud Objects
# ============================================================================

def check_proximity_to_loud_object(proximity_cm: float, object_name: str) -> Dict[str, any]:
    """
    Detect when a hand is in close proximity to a loud object (blender, garbage disposal, etc.)
    and play a warning message before the object is turned on.
    
    Args:
        proximity_cm: Distance reading from proximity sensor in centimeters
        object_name: Name of the loud object being approached (e.g., "blender", "garbage disposal")
        
    Returns:
        Dictionary with proximity status and action taken
    """
    global CURRENT_PROXIMITY_CM, CURRENT_NEAR_OBJECT, PROXIMITY_THRESHOLD_CM
    
    CURRENT_PROXIMITY_CM = proximity_cm
    
    # Check if hand is within warning threshold
    if proximity_cm <= PROXIMITY_THRESHOLD_CM:
        CURRENT_NEAR_OBJECT = object_name.lower()
        
        print(f"⚠️  PROXIMITY ALERT: Hand detected {proximity_cm}cm from {object_name}")
        print(f"   → Warning: {object_name.upper()} can create loud noise")
        print(f"   → Activating pre-warning system")
        
        # Play audio warning
        if AUDIO_AVAILABLE and speak_text:
            warning_msg = f"Warning. Your hand is near the {object_name}. This device can create loud noise. Please prepare for the sound or move your hand away."
            speak_text(warning_msg)
        
        # Activate visual warning (RGB LED pulsing)
        print(f"   → RGB LED: Pulsing {CALM_DOWN_COLOR.upper()} light")
        
        return {
            "action": "proximity_warning_activated",
            "object_name": object_name,
            "proximity_cm": proximity_cm,
            "threshold_cm": PROXIMITY_THRESHOLD_CM,
            "warning_played": True,
            "led_activated": True
        }
    else:
        # Hand moved away or not close enough
        if CURRENT_NEAR_OBJECT == object_name.lower():
            CURRENT_NEAR_OBJECT = None
            print(f"✅ Hand moved away from {object_name} ({proximity_cm}cm)")
        
        return {
            "action": "proximity_safe",
            "object_name": object_name,
            "proximity_cm": proximity_cm,
            "threshold_cm": PROXIMITY_THRESHOLD_CM
        }


# Configuration setup functions removed - all thresholds are hardcoded above


# ============================================================================
# DEMO MODE - Interactive Testing
# ============================================================================

def print_input_key():
    """Print the input key showing which letters correspond to which inputs."""
    print("\n" + "="*60)
    print("INPUT KEY - Letter Prefixes for Kitchen System")
    print("="*60)
    print("\nSensory Sensitivities:")
    print("  d<number>      - Decibel level (e.g., 'd80' = 80 decibels)")
    print("  l<number>      - Light level in lux (e.g., 'l90' = 90 lux)")
    print("\nExecutive Functioning:")
    print("  r<recipe_id>   - Load recipe (e.g., 'rscrambled_eggs')")
    print("  s              - Step complete")
    print("  timer<number>  - Start timer in seconds (e.g., 'timer300' = 5 minutes)")
    print("\nSafety Awareness:")
    print("  t<number>      - Stove temperature in Celsius (e.g., 't75' = 75°C)")
    print("  m              - Motion detected")
    print("  n              - No motion detected")
    print("\nEmotional Regulation:")
    print("  p              - Pause button pressed (activate de-escalation)")
    print("  e              - Exit de-escalation mode")
    print("\nProximity Detection:")
    print("  x<object> <distance> - Proximity to loud object (e.g., 'x blender 10')")
    print("                        Objects: blender, garbage disposal, food processor, mixer")
    print("\nSystem Control:")
    print("  key            - Show this input key")
    print("  status         - Show current system status")
    print("  q              - Quit demo")
    print("="*60)


def show_system_status():
    """Display current status of all system sections."""
    global CURRENT_SOUND_LEVEL, CURRENT_LIGHT_LEVEL, STOVE_TEMP_CURRENT, MOTION_DETECTED
    global CURRENT_RECIPE, CURRENT_STEP, TIMER_ACTIVE, DEESCALATION_MODE_ACTIVE
    global CURRENT_PROXIMITY_CM, CURRENT_NEAR_OBJECT
    
    print("\n" + "-"*60)
    print("SYSTEM STATUS")
    print("-"*60)
    
    print("\nSensory Sensitivities:")
    print(f"  Sound: {CURRENT_SOUND_LEVEL}dB (threshold: {SOUND_THRESHOLD_DB}dB)")
    print(f"  Light: {CURRENT_LIGHT_LEVEL} lux (threshold: {AMBIENT_LIGHT_LEVEL} lux)")
    
    print("\nExecutive Functioning:")
    if CURRENT_RECIPE:
        recipe_status = f"Step {CURRENT_STEP + 1}/{len(CURRENT_RECIPE['steps'])}" if CURRENT_STEP < len(CURRENT_RECIPE['steps']) else "Complete"
        print(f"  Recipe: {CURRENT_RECIPE['name']} ({recipe_status})")
    else:
        print("  Recipe: None loaded")
    timer_status = check_timer()
    if timer_status["action"] == "timer_running":
        print(f"  Timer: {timer_status['remaining']}s remaining ({timer_status['brightness']}% brightness)")
    else:
        print("  Timer: Not active")
    
    print("\nSafety Awareness:")
    print(f"  Stove temp: {STOVE_TEMP_CURRENT}°C (threshold: {STOVE_TEMP_THRESHOLD_C}°C)")
    print(f"  Motion: {'Detected' if MOTION_DETECTED else 'Not detected'}")
    
    print("\nEmotional Regulation:")
    print(f"  De-escalation mode: {'Active' if DEESCALATION_MODE_ACTIVE else 'Inactive'}")
    
    print("\nProximity Detection:")
    if CURRENT_NEAR_OBJECT:
        print(f"  Near object: {CURRENT_NEAR_OBJECT} ({CURRENT_PROXIMITY_CM}cm)")
    else:
        print(f"  Current proximity: {CURRENT_PROXIMITY_CM}cm (threshold: {PROXIMITY_THRESHOLD_CM}cm)")
    
    print("-"*60)


def parse_unified_input(user_input: str):
    """
    Parse unified input with letter prefixes and route to appropriate functions.
    All sections run simultaneously - inputs can be sent at any time.
    """
    global CURRENT_SOUND_LEVEL, CURRENT_LIGHT_LEVEL, STOVE_TEMP_CURRENT, MOTION_DETECTED
    global LAST_MOTION_TIME, CURRENT_RECIPE, CURRENT_STEP, TIMER_ACTIVE
    global CURRENT_PROXIMITY_CM
    
    user_input = user_input.strip()
    if not user_input:
        return
    
    # Initialize motion time if needed
    if LAST_MOTION_TIME is None:
        LAST_MOTION_TIME = time.time()
    
    # System control commands
    if user_input == 'q':
        return 'quit'
    elif user_input == 'key':
        print_input_key()
        return
    elif user_input == 'status':
        show_system_status()
        return
    
    # Sensory Sensitivities
    if user_input.startswith('d'):
        try:
            db_val = float(user_input[1:].strip())
            CURRENT_SOUND_LEVEL = db_val
            check_sound_level(CURRENT_SOUND_LEVEL)
        except ValueError:
            print("Invalid input. Use 'd' + number (e.g., 'd80')")
    elif user_input.startswith('l'):
        try:
            light_val = int(float(user_input[1:].strip()))
            CURRENT_LIGHT_LEVEL = light_val
            adjust_ambient_light(CURRENT_LIGHT_LEVEL)
        except ValueError:
            print("Invalid input. Use 'l' + number (e.g., 'l90')")
    
    # Executive Functioning
    elif user_input.startswith('r'):
        recipe_id = user_input[1:].strip()
        if recipe_id in RECIPES:
            load_recipe(recipe_id)
        else:
            print(f"Recipe '{recipe_id}' not found. Available recipes: {', '.join(RECIPES.keys())}")
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
            print("Invalid input. Use 'timer' + number (e.g., 'timer300')")
    
    # Safety Awareness
    elif user_input.startswith('t') and not user_input.startswith('timer'):
        try:
            temp_val = float(user_input[1:].strip())
            STOVE_TEMP_CURRENT = temp_val
            check_stove_safety(STOVE_TEMP_CURRENT, MOTION_DETECTED)
        except ValueError:
            print("Invalid input. Use 't' + number (e.g., 't75')")
    elif user_input == 'm':
        MOTION_DETECTED = True
        LAST_MOTION_TIME = time.time()
        print(f"✓ Motion: Detected")
        check_stove_safety(STOVE_TEMP_CURRENT, MOTION_DETECTED)
    elif user_input == 'n':
        MOTION_DETECTED = False
        print(f"✓ Motion: Not detected")
        check_stove_safety(STOVE_TEMP_CURRENT, MOTION_DETECTED)
    
    # Emotional Regulation
    elif user_input == 'p':
        press_pause_button()
    elif user_input == 'e':
        exit_deescalation_mode()
    
    # Proximity Detection
    elif user_input.startswith('x'):
        try:
            parts = user_input[1:].strip().split()
            if len(parts) < 2:
                print("Invalid format. Use 'x <object_name> <distance>' (e.g., 'x blender 10')")
            else:
                distance = float(parts[-1])
                object_name = ' '.join(parts[:-1])
                check_proximity_to_loud_object(distance, object_name)
        except (ValueError, IndexError):
            print("Invalid format. Use 'x <object_name> <distance>' (e.g., 'x blender 10')")
    
    else:
        print(f"Unknown command: '{user_input}'. Type 'key' to see input options.")


def run_demo():
    """
    Run unified demo with all systems running simultaneously.
    Inputs use letter prefixes to distinguish input types.
    """
    global LAST_MOTION_TIME
    
    # Initialize motion time
    if LAST_MOTION_TIME is None:
        LAST_MOTION_TIME = time.time()
    
    print("\n" + "="*60)
    print("KITCHEN SYSTEM DEMO - All Sections Running Simultaneously")
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
            # Check timer status periodically if active (simulate continuous monitoring)
            if TIMER_ACTIVE:
                timer_status = check_timer()
                if timer_status["action"] == "timer_complete":
                    # Timer completed during idle time
                    pass
            
            # Get user input
            user_input = input("> ").strip().lower()
            
            result = parse_unified_input(user_input)
            if result == 'quit':
                print("\nExiting demo...")
                break
            
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
    global CURRENT_STEP, CURRENT_RECIPE, TIMER_ACTIVE, TIMER_START_TIME, TIMER_DURATION_SECONDS
    
    print("\n" + "-"*60)
    print("DEMO 2: Executive Functioning")
    print("-"*60)
    
    # Prompt for recipe selection if none is loaded
    if CURRENT_RECIPE is None:
        print("\n📋 Select a recipe:")
        recipe_list = list(RECIPES.items())
        for i, (recipe_id, recipe) in enumerate(recipe_list, 1):
            print(f"  {i}. {recipe['name']} - {recipe.get('description', '')}")
        
        while True:
            try:
                choice = input("\nEnter recipe number (1-{}): ".format(len(recipe_list))).strip()
                recipe_idx = int(choice) - 1
                if 0 <= recipe_idx < len(recipe_list):
                    recipe_id, _ = recipe_list[recipe_idx]
                    load_recipe(recipe_id)
                    break
                else:
                    print(f"Invalid choice. Enter 1-{len(recipe_list)}")
            except ValueError:
                print("Invalid input. Enter a number.")
            except KeyboardInterrupt:
                print("\nExiting...")
                return
    
    # Show current recipe status
    if CURRENT_RECIPE:
        print(f"\n📋 Current recipe: {CURRENT_RECIPE['name']}")
        print(f"   Steps: {len(CURRENT_RECIPE['steps'])}")
        current_status = f"Step {CURRENT_STEP + 1}/{len(CURRENT_RECIPE['steps'])}" if CURRENT_STEP < len(CURRENT_RECIPE['steps']) else "Complete"
        print(f"   Status: {current_status}")
        if CURRENT_STEP < len(CURRENT_RECIPE['steps']):
            print(f"   Current step: {CURRENT_RECIPE['steps'][CURRENT_STEP]}")
    
    print("\nInput actions:")
    print("  's' - step complete button pressed")
    print("  't' + number - timer started (seconds)")
    print("  'check' - check timer status")
    print("  'reset' - reset recipe to beginning")
    print("  'new' - select a new recipe")
    print("  'q' - quit")
    print()
    
    while True:
        try:
            user_input = input("Enter action: ").strip().lower()
            
            if user_input == 'q':
                break
            elif user_input == 's':
                result = step_complete()
                if result.get("action") == "no_recipe_loaded":
                    print(f"⚠️  {result['error']}")
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
            elif user_input == 'check':
                status = check_timer()
                if status["action"] == "timer_running":
                    print(f"⏱️  Timer: {status['remaining']:.1f}s remaining ({status['brightness']}% brightness)")
                elif status["action"] == "timer_complete":
                    print("⏰ Timer complete!")
                else:
                    print("No active timer")
            elif user_input == 'reset':
                result = reset_recipe()
                if result.get("action") == "no_recipe_loaded":
                    print(f"⚠️  {result['error']}")
            elif user_input == 'new':
                print("\n📋 Select a new recipe:")
                recipe_list = list(RECIPES.items())
                for i, (recipe_id, recipe) in enumerate(recipe_list, 1):
                    print(f"  {i}. {recipe['name']} - {recipe.get('description', '')}")
                
                while True:
                    try:
                        choice = input("\nEnter recipe number (1-{}): ".format(len(recipe_list))).strip()
                        recipe_idx = int(choice) - 1
                        if 0 <= recipe_idx < len(recipe_list):
                            recipe_id, _ = recipe_list[recipe_idx]
                            load_recipe(recipe_id)
                            print(f"\n📋 Switched to: {CURRENT_RECIPE['name']}")
                            break
                        else:
                            print(f"Invalid choice. Enter 1-{len(recipe_list)}")
                    except ValueError:
                        print("Invalid input. Enter a number.")
                    except KeyboardInterrupt:
                        break
            else:
                print("Unknown command. Use 's', 't', 'check', 'reset', 'new', or 'q'")
            
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
    # Show current recipe if loaded
    if CURRENT_RECIPE:
        print(f"\nCurrent recipe: {CURRENT_RECIPE['name']} ({len(CURRENT_RECIPE['steps'])} steps)")
    else:
        print(f"\nNo recipe loaded. Select one in Demo 2 first.")
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
    print("  Proximity: 'prox object_name distance_cm' (e.g., 'prox blender 10')")
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
            elif user_input.startswith('prox'):
                try:
                    parts = user_input.split()[1:]  # Skip 'prox'
                    if len(parts) < 2:
                        print("Invalid format. Use: 'prox object_name distance_cm'")
                    else:
                        distance = float(parts[-1])
                        object_name = ' '.join(parts[:-1])
                        check_proximity_to_loud_object(distance, object_name)
                except (ValueError, IndexError):
                    print("Invalid proximity format. Use: 'prox object_name distance_cm'")
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


def demo_proximity():
    """Input proximity readings - react if hand is near loud object."""
    global CURRENT_PROXIMITY_CM, CURRENT_NEAR_OBJECT
    
    print("\n" + "-"*60)
    print("DEMO 5: Proximity Detection for Loud Objects")
    print("-"*60)
    print(f"\nThreshold (hardcoded): {PROXIMITY_THRESHOLD_CM}cm")
    print(f"Loud objects: {', '.join(LOUD_OBJECTS)}")
    print("\nEnter proximity readings:")
    print("  Format: 'object_name distance_cm' (e.g., 'blender 10' or 'garbage disposal 5')")
    print("  Or: 'q' to quit")
    print()
    
    while True:
        try:
            user_input = input("Enter object and distance: ").strip().lower()
            
            if user_input == 'q':
                break
            
            # Parse input: "object_name distance"
            parts = user_input.split()
            if len(parts) < 2:
                print("Invalid format. Use: 'object_name distance_cm'")
                continue
            
            try:
                distance = float(parts[-1])  # Last part is distance
                object_name = ' '.join(parts[:-1])  # Everything else is object name
                
                # Check if object is in our list (case-insensitive)
                object_found = None
                for obj in LOUD_OBJECTS:
                    if obj.lower() in object_name or object_name in obj.lower():
                        object_found = obj
                        break
                
                if object_found:
                    check_proximity_to_loud_object(distance, object_found)
                else:
                    print(f"⚠️  Warning: '{object_name}' not in known loud objects list.")
                    print(f"   Known objects: {', '.join(LOUD_OBJECTS)}")
                    # Still check proximity but warn it's not in the list
                    check_proximity_to_loud_object(distance, object_name)
                    
            except ValueError:
                print("Invalid distance. Enter a number for distance in centimeters.")
            
        except KeyboardInterrupt:
            break
    
    print("\nExiting...")


if __name__ == "__main__":
    run_demo()