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

# Import dialogue system for varied messages
try:
    from utils.dialogues import get_dialogue
    DIALOGUE_AVAILABLE = True
except Exception as e:
    DIALOGUE_AVAILABLE = False
    get_dialogue = None
    print(f"[DEBUG] Dialogue system import failed: {e}")


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
STOVE_TEMP_THRESHOLD_C = 30  # Fire warning threshold in Celsius (triggers vibration after 10s with no motion)
STOVE_TEMP_SECOND_THRESHOLD_C = 300  # Second fire hazard threshold in Celsius
STOVE_TEMP_CURRENT = 25  # Current stove temperature reading (°C)
MOTION_DETECTED = True  # Whether motion is currently detected
MOTION_TIMEOUT_SECONDS = 300  # 5 minutes of no motion triggers alert
LAST_MOTION_TIME = None
SAFETY_ALERT_ACTIVE = False
# Fire warning threshold tracking (40°C)
STOVE_ABOVE_WARNING_THRESHOLD_START = None  # Timestamp when stove first exceeded 40°C threshold
VIBRATION_WARNING_TRIGGER_SECONDS = 10  # Seconds above threshold with no motion before vibration
VIBRATION_ACTIVE = False  # Whether vibration motor is currently active
PROXIMITY_MOTION_RANGE_MM = 2000  # Motion detection range in millimeters (2000mm = 2 meters)
# Second threshold tracking
STOVE_ABOVE_SECOND_THRESHOLD_START = None  # Timestamp when stove first exceeded second threshold
SECOND_THRESHOLD_REMINDER_INTERVAL = 30  # Seconds between reminders when above second threshold
LAST_REMINDER_TIME = None  # Timestamp of last reminder
# Proximity-based motion detection for kitchen
KITCHEN_PROXIMITY_READINGS = []  # Recent proximity readings for motion detection
PROXIMITY_MOTION_THRESHOLD_CM = 5  # Change in proximity (cm) to indicate motion
PROXIMITY_READINGS_TO_TRACK = 10  # Number of recent readings to track
LAST_PROXIMITY_READING = None  # Last proximity reading

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

# 6. Hardware Configuration (ifmagic module port assignments)
HARDWARE_ENABLED = False  # Set to True to enable hardware mode
HARDWARE_CONNECTION_PATH = "/dev/cu.SLAB_USBtoUART"  # Adjust for your system
# Port assignments (adjust based on your physical setup)
PROXIMITY_PORT = 3  # Proximity sensor module port
SOUND_PORT = 2  # Sound sensor module port (may be same as proximity or different)
THERMAL_PORT = 4  # Thermal sensor module port (for stove temperature)
GLOW_PORT = 7  # Glow module port for visual feedback
MOTION_PORT = 3  # Motion sensor module port (optional)
VIBRATION_PORT = 7  # Vibration motor module port


# ============================================================================
# HARDWARE INTEGRATION - Sensor Reading Functions
# ============================================================================

def read_proximity_sensor(ports):
    """
    Read proximity sensor from hardware and return distance in millimeters.
    
    Args:
        ports: Hardware data object from h.read()
        
    Returns:
        Distance in millimeters, or None if sensor unavailable
    """
    try:
        if hasattr(ports, 'modules') and ports.modules[PROXIMITY_PORT] is not None:
            # Try different possible property names
            module = ports.modules[PROXIMITY_PORT]
            if hasattr(module, 'amount'):
                return int(module.amount())
            elif hasattr(module, 'distance'):
                return int(module.distance)
            elif hasattr(module, 'proximity'):
                return int(module.proximity)
    except (AttributeError, IndexError, TypeError) as e:
        pass
    return None


def read_sound_sensor(ports):
    """
    Read sound sensor from hardware and return decibel level.
    
    Args:
        ports: Hardware data object from h.read()
        
    Returns:
        Decibel level, or None if sensor unavailable
    """
    try:
        if hasattr(ports, 'modules') and ports.modules[SOUND_PORT] is not None:
            module = ports.modules[SOUND_PORT]
            if hasattr(module, 'sound'):
                return int(module.sound())
            elif hasattr(module, 'decibel'):
                return int(module.decibel)
            elif hasattr(module, 'volume'):
                return int(module.volume)
    except (AttributeError, IndexError, TypeError) as e:
        pass
    return None


def read_thermal_sensor(ports):
    """
    Read thermal sensor from hardware and return average temperature.
    Uses pixel temperatures from thermal module (as in ifmagic_trial.py).
    
    Args:
        ports: Hardware data object from h.read()
        
    Returns:
        Temperature in Kelvin (or Celsius if module provides it directly), or None
    """
    try:
        if hasattr(ports, 'modules') and ports.modules[THERMAL_PORT] is not None:
            module = ports.modules[THERMAL_PORT]
            # Check if it has pixel_temperatures array (thermal camera module)
            if hasattr(module, 'pixel_temperatures'):
                # Average center pixels (as in ifmagic_trial.py)
                pixels = module.pixel_temperatures
                if isinstance(pixels, (list, tuple)) and len(pixels) >= 4:
                    center_avg = (pixels[3][3] + pixels[3][4] + pixels[4][3] + pixels[4][4]) / 4
                    # Convert from Kelvin to Celsius if needed (typical thermal modules use Kelvin)
                    # If already in Celsius, remove the -273.15
                    temp_celsius = center_avg - 273.15 if center_avg > 200 else center_avg
                    return temp_celsius
            elif hasattr(module, 'temperature'):
                # Direct temperature reading
                temp = float(module.temperature)
                return temp - 273.15 if temp > 200 else temp
    except (AttributeError, IndexError, TypeError) as e:
        pass
    return None


def set_glow_warning(ports, active: bool = True):
    """
    Set glow module to warning state (fade animation) or normal state (solid color).
    
    Args:
        ports: Hardware object (h) for setting outputs
        active: True for warning (fade), False for normal (solid color)
    """
    try:
        if hasattr(ports, 'modules') and ports.modules[GLOW_PORT] is not None:
            if active:
                # Warning: pulsing/fading glow (as in ifmagic_trial.py)
                ports.modules[GLOW_PORT].out.setFade(
                    start=0, end=2000, hue=100, saturation=255,
                    movement=1, speed=1, low=1, high=1, bounce=1
                )
            else:
                # Normal: solid color (low saturation)
                ports.modules[GLOW_PORT].out.setColor(start=0, end=2000, hue=100, saturation=0)
    except (AttributeError, IndexError) as e:
        pass


def set_glow_recipe_step(ports, step_index: int, total_steps: int):
    """
    Set glow module to indicate current recipe step (visual step indicator).
    
    Args:
        ports: Hardware object (h) for setting outputs
        step_index: Current step index (0-based)
        total_steps: Total number of steps
    """
    try:
        if hasattr(ports, 'modules'):
            # Use glow modules in sequence (ports 7, 6, 5, etc.) to show step progress
            # Activate glow on port (7 - step_index) to indicate current step
            glow_port = GLOW_PORT - step_index
            if glow_port >= 0 and ports.modules[glow_port] is not None:
                ports.modules[glow_port].out.setFade(
                    start=0, end=2000, hue=100, saturation=255,
                    movement=1, speed=1, low=1, high=1, bounce=1
                )
    except (AttributeError, IndexError) as e:
        pass


# ============================================================================
# FUNCTION 1: Sensory Sensitivities (Sound & Light)
# ============================================================================

def check_sound_level(db_level: float, hardware_ports=None) -> Dict[str, any]:
    """
    Monitor sound levels and trigger calm down scene if too loud.
    
    Args:
        db_level: Current decibel reading from sound sensor
        hardware_ports: Optional hardware object for glow feedback (if hardware mode enabled)
        
    Returns:
        Dictionary with action taken and status
    """
    global CALM_DOWN_COLOR, RELAY_CUTOFF_ENABLED
    
    if db_level > SOUND_THRESHOLD_DB:
        # Trigger "Calm Down" Scene
        print(f"🔵 SOUND ALERT: {db_level}dB detected (threshold: {SOUND_THRESHOLD_DB}dB)")
        print(f"   → Activating calm down scene: {CALM_DOWN_COLOR.upper()} LED pulsing")
        
        # Activate hardware glow if available
        if hardware_ports is not None:
            set_glow_warning(hardware_ports, active=True)
        
        # Play audio warning
        if AUDIO_AVAILABLE and speak_text:
            print(f"[DEBUG] Audio available, calling speak_text...")
            if DIALOGUE_AVAILABLE and get_dialogue:
                warning_msg = get_dialogue("sound_warning", f"Warning. Loud noise detected. {int(db_level)} decibels. Please prepare for the sound.")
            else:
                warning_msg = f"Warning. Loud noise detected. {int(db_level)} decibels. Please prepare for the sound."
            speak_text(warning_msg)
        else:
            print(f"[DEBUG] Audio not available. AUDIO_AVAILABLE={AUDIO_AVAILABLE}, speak_text={speak_text}")
        
        if RELAY_CUTOFF_ENABLED and db_level > 90:
            print(f"   → ⚠️  CRITICAL: Cutting power to appliance (noise > 90dB)")
            if AUDIO_AVAILABLE and speak_text:
                if DIALOGUE_AVAILABLE and get_dialogue:
                    critical_msg = get_dialogue("sound_critical", "Critical alert. Very loud noise detected. Cutting power to appliance.")
                else:
                    critical_msg = "Critical alert. Very loud noise detected. Cutting power to appliance."
                speak_text(critical_msg)
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
    
        # Turn off warning glow if noise is normal
        if hardware_ports is not None:
            set_glow_warning(hardware_ports, active=False)
        
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
            if DIALOGUE_AVAILABLE and get_dialogue:
                warning_msg = get_dialogue("light_warning", f"Warning. Harsh lighting detected. {light_level} lux. Consider dimming the lights or moving to a softer area.")
            else:
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
        if DIALOGUE_AVAILABLE and get_dialogue:
            recipe_msg = get_dialogue("recipe_loaded", f"Recipe loaded: {CURRENT_RECIPE['name']}. {len(CURRENT_RECIPE['steps'])} steps.",
                                      name=CURRENT_RECIPE['name'], steps=len(CURRENT_RECIPE['steps']))
        else:
            recipe_msg = f"Recipe loaded: {CURRENT_RECIPE['name']}. {len(CURRENT_RECIPE['steps'])} steps."
        speak_text(recipe_msg)
    
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
                if DIALOGUE_AVAILABLE and get_dialogue:
                    step_msg = get_dialogue("recipe_step_complete", f"Step {CURRENT_STEP} complete. Next step: {next_task}.",
                                            step=CURRENT_STEP, next=next_task)
                else:
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
                if DIALOGUE_AVAILABLE and get_dialogue:
                    complete_msg = get_dialogue("recipe_complete", f"Recipe complete. Great job! {CURRENT_RECIPE['name']} is ready.",
                                                name=CURRENT_RECIPE['name'])
                else:
                    complete_msg = f"Recipe complete. Great job! {CURRENT_RECIPE['name']} is ready."
                speak_text(complete_msg)
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
            if DIALOGUE_AVAILABLE and get_dialogue:
                timer_msg = get_dialogue("timer_complete", "Timer complete.")
            else:
                timer_msg = "Timer complete."
            speak_text(timer_msg)
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
        if DIALOGUE_AVAILABLE and get_dialogue:
            reset_msg = get_dialogue("recipe_reset", f"Recipe reset. Starting {CURRENT_RECIPE['name']} from the beginning.",
                                     name=CURRENT_RECIPE['name'])
        else:
            reset_msg = f"Recipe reset. Starting {CURRENT_RECIPE['name']} from the beginning."
        speak_text(reset_msg)
    
    return {
        "action": "recipe_reset",
        "recipe_name": CURRENT_RECIPE['name'],
        "step_number": 0
    }


# ============================================================================
# FUNCTION 3: Safety Awareness (Stove & Heat)
# ============================================================================

def detect_motion_within_range(proximity_mm: float, range_mm: float = 2000) -> bool:
    """
    Detect if motion is within a specified range using proximity sensor.
    
    Args:
        proximity_mm: Current proximity reading in millimeters
        range_mm: Range threshold in millimeters (default 2000mm = 2 meters)
        
    Returns:
        True if motion detected within range, False otherwise
    """
    # If proximity is less than the range, motion is detected within range
    if proximity_mm <= range_mm:
        return True
    return False


def set_vibration_motor(hardware_ports, state: int):
    """
    Control the vibration motor.
    
    Args:
        hardware_ports: Hardware object (h) for setting outputs
        state: 0 for off, 1 for on
    """
    global VIBRATION_ACTIVE
    
    try:
        if hasattr(hardware_ports, 'modules') and hardware_ports.modules[VIBRATION_PORT] is not None:
            module = hardware_ports.modules[VIBRATION_PORT]
            if hasattr(module, 'out'):
                if hasattr(module.out, 'setState'):
                    module.out.setState(state)
                    VIBRATION_ACTIVE = (state == 1)
                    print(f"Vibration motor set to {'ON' if state == 1 else 'OFF'}")
                elif hasattr(module.out, 'set_state'):
                    module.out.set_state(state)
                    VIBRATION_ACTIVE = (state == 1)
                    print(f"Vibration motor set to {'ON' if state == 1 else 'OFF'}")
    except (AttributeError, IndexError) as e:
        print(f"Error setting vibration motor: {e}")


def detect_motion_via_proximity(proximity_cm: float) -> bool:
    """
    Detect motion in kitchen using proximity sensor.
    Changes in proximity readings indicate movement in the kitchen.
    
    Args:
        proximity_cm: Current proximity reading in centimeters
        
    Returns:
        True if motion detected, False otherwise
    """
    global KITCHEN_PROXIMITY_READINGS, LAST_PROXIMITY_READING, PROXIMITY_MOTION_THRESHOLD_CM
    
    # Convert mm to cm if needed (ifmagic proximity returns mm)
    proximity_in_cm = proximity_cm / 10.0 if proximity_cm > 100 else proximity_cm
    
    # If we have a previous reading, check for significant change
    if LAST_PROXIMITY_READING is not None:
        change = abs(proximity_in_cm - LAST_PROXIMITY_READING)
        if change >= PROXIMITY_MOTION_THRESHOLD_CM:
            # Significant change detected - motion detected
            LAST_PROXIMITY_READING = proximity_in_cm
            KITCHEN_PROXIMITY_READINGS.append(proximity_in_cm)
            # Keep only recent readings
            if len(KITCHEN_PROXIMITY_READINGS) > PROXIMITY_READINGS_TO_TRACK:
                KITCHEN_PROXIMITY_READINGS.pop(0)
            return True
    
    # Update tracking
    LAST_PROXIMITY_READING = proximity_in_cm
    KITCHEN_PROXIMITY_READINGS.append(proximity_in_cm)
    # Keep only recent readings
    if len(KITCHEN_PROXIMITY_READINGS) > PROXIMITY_READINGS_TO_TRACK:
        KITCHEN_PROXIMITY_READINGS.pop(0)
    
    # Check if recent readings show variation (indicating movement)
    if len(KITCHEN_PROXIMITY_READINGS) >= 3:
        # Calculate variance in recent readings
        recent_readings = KITCHEN_PROXIMITY_READINGS[-5:]
        if len(recent_readings) >= 2:
            min_reading = min(recent_readings)
            max_reading = max(recent_readings)
            variation = max_reading - min_reading
            if variation >= PROXIMITY_MOTION_THRESHOLD_CM:
                return True
    
    return False


def check_stove_safety(temp_celsius: float, motion_detected: bool, hardware_ports=None, proximity_cm: float = None) -> Dict[str, any]:
    """
    Monitor stove temperature and motion to detect safety issues.
    Includes check for second fire hazard threshold with proximity-based motion detection.
    
    Args:
        temp_celsius: Current stove temperature
        motion_detected: Whether motion is currently detected (from motion sensor if available)
        hardware_ports: Optional hardware object for glow feedback (if hardware mode enabled)
        proximity_cm: Optional proximity reading in cm/mm for motion detection
        
    Returns:
        Dictionary with safety status
    """
    global STOVE_TEMP_CURRENT, MOTION_DETECTED, LAST_MOTION_TIME, SAFETY_ALERT_ACTIVE
    global STOVE_ABOVE_SECOND_THRESHOLD_START, LAST_REMINDER_TIME, STOVE_TEMP_SECOND_THRESHOLD_C
    global STOVE_ABOVE_WARNING_THRESHOLD_START, VIBRATION_ACTIVE, PROXIMITY_MOTION_RANGE_MM
    
    STOVE_TEMP_CURRENT = temp_celsius
    MOTION_DETECTED = motion_detected
    
    if motion_detected:
        LAST_MOTION_TIME = time.time()
    
    # Check for proximity-based motion detection if proximity reading is provided
    proximity_motion_detected = False
    motion_within_range = False
    if proximity_cm is not None:
        # Convert cm to mm for range check (proximity_cm is passed in cm from hardware mode)
        proximity_mm = proximity_cm * 10.0
        
        # Check if motion is within 2000mm range (2 meters)
        motion_within_range = detect_motion_within_range(proximity_mm, PROXIMITY_MOTION_RANGE_MM)
        
        # Also check for motion via proximity changes
        proximity_motion_detected = detect_motion_via_proximity(proximity_cm)
        
        if proximity_motion_detected or motion_within_range:
            LAST_MOTION_TIME = time.time()
            # Reset warning threshold tracking if motion detected
            if STOVE_ABOVE_WARNING_THRESHOLD_START is not None:
                STOVE_ABOVE_WARNING_THRESHOLD_START = None
                # Turn off vibration if motion detected
                if VIBRATION_ACTIVE and hardware_ports is not None:
                    set_vibration_motor(hardware_ports, 0)
            
            # Reset second threshold tracking if motion detected
            if STOVE_ABOVE_SECOND_THRESHOLD_START is not None:
                STOVE_ABOVE_SECOND_THRESHOLD_START = None
                LAST_REMINDER_TIME = None
    
    # Check fire warning threshold (40°C) - trigger vibration after 10 seconds with no motion
    # Vibration will continue until movement is detected (even if temperature drops)
    if temp_celsius > STOVE_TEMP_THRESHOLD_C:
        # Track when stove first exceeded warning threshold
        if STOVE_ABOVE_WARNING_THRESHOLD_START is None:
            STOVE_ABOVE_WARNING_THRESHOLD_START = time.time()
        
        # Check if motion detected within range
        motion_any = motion_detected or motion_within_range
        
        # Check if it's been above threshold for 10 seconds with no motion
        time_above_threshold = time.time() - STOVE_ABOVE_WARNING_THRESHOLD_START
        
        if time_above_threshold >= VIBRATION_WARNING_TRIGGER_SECONDS and not motion_any:
            # No motion within range for 10 seconds - start vibration (or keep it going)
            if not VIBRATION_ACTIVE and hardware_ports is not None:
                print(f"🔥 FIRE WARNING: Stove at {temp_celsius}°C for {int(time_above_threshold)}s with no motion within {PROXIMITY_MOTION_RANGE_MM}mm")
                print(f"   → Starting vibration motor (will continue until motion detected)")
                set_vibration_motor(hardware_ports, 1)
                
                # Play audio warning (only once when vibration starts)
                if AUDIO_AVAILABLE and speak_text:
                    if DIALOGUE_AVAILABLE and get_dialogue:
                        warning_msg = get_dialogue("heat_warning_warming", "The stove is getting too hot, turn it off")
                    else:
                        warning_msg = "The stove is getting too hot, turn it off"
                    speak_text(warning_msg)
            elif VIBRATION_ACTIVE and hardware_ports is not None:
                # Keep vibration going - ensure it's still on
                set_vibration_motor(hardware_ports, 1)
        elif motion_any:
            # Motion detected - stop vibration and reset tracking
            if VIBRATION_ACTIVE and hardware_ports is not None:
                print(f"✓ Motion detected within {PROXIMITY_MOTION_RANGE_MM}mm - stopping vibration")
                set_vibration_motor(hardware_ports, 0)
            STOVE_ABOVE_WARNING_THRESHOLD_START = None
    else:
        # Stove is below threshold - if vibration is active, keep it going until motion detected
        # Reset tracking for new cycle but don't stop vibration if it's already running
        if STOVE_ABOVE_WARNING_THRESHOLD_START is not None:
            STOVE_ABOVE_WARNING_THRESHOLD_START = None
        
        # If vibration is active, keep it going until motion is detected
        if VIBRATION_ACTIVE and hardware_ports is not None:
            # Check if motion detected - only then stop vibration
            motion_any = motion_detected or motion_within_range
            if motion_any:
                print(f"✓ Motion detected within {PROXIMITY_MOTION_RANGE_MM}mm - stopping vibration")
                set_vibration_motor(hardware_ports, 0)
            else:
                # No motion yet - keep vibrating
                set_vibration_motor(hardware_ports, 1)
    
    # Check second fire hazard threshold (300°C) with proximity-based motion detection
    if temp_celsius > STOVE_TEMP_SECOND_THRESHOLD_C:
        # Track when stove first exceeded second threshold
        if STOVE_ABOVE_SECOND_THRESHOLD_START is None:
            STOVE_ABOVE_SECOND_THRESHOLD_START = time.time()
            LAST_REMINDER_TIME = None
        
        # Check if it's been above threshold for 1 minute (60 seconds)
        time_above_threshold = time.time() - STOVE_ABOVE_SECOND_THRESHOLD_START
        
        if time_above_threshold >= 60:  # 1 minute
            # Check if motion detected via proximity sensor
            motion_any = motion_detected or proximity_motion_detected
            
            if not motion_any:
                # No motion detected - give reminders
                current_time = time.time()
                # Send reminder every 30 seconds
                if LAST_REMINDER_TIME is None or (current_time - LAST_REMINDER_TIME) >= SECOND_THRESHOLD_REMINDER_INTERVAL:
                    LAST_REMINDER_TIME = current_time
                    
                    if hardware_ports is not None:
                        set_glow_warning(hardware_ports, active=True)
                    
                    # Play audio reminder
                    if AUDIO_AVAILABLE and speak_text:
                        if DIALOGUE_AVAILABLE and get_dialogue:
                            reminder_msg = get_dialogue("fire_hazard_reminder", 
                                                       f"Fire hazard alert. The stove has been above {int(STOVE_TEMP_SECOND_THRESHOLD_C)} degrees for over a minute with no movement detected. Please turn off the stove to avoid a fire.",
                                                       temp=int(STOVE_TEMP_SECOND_THRESHOLD_C))
                        else:
                            reminder_msg = f"Fire hazard alert. The stove has been above {int(STOVE_TEMP_SECOND_THRESHOLD_C)} degrees for over a minute with no movement detected. Please turn off the stove to avoid a fire."
                        speak_text(reminder_msg)
                    
                    print(f"🔥 FIRE HAZARD REMINDER: Stove at {temp_celsius}°C for {int(time_above_threshold)}s with no motion")
                    print(f"   → Reminder: Turn off the stove to avoid a fire")
                    
                    return {
                        "action": "fire_hazard_reminder",
                        "temp": temp_celsius,
                        "time_above_threshold": int(time_above_threshold),
                        "motion_detected": False,
                        "proximity_motion_detected": proximity_motion_detected,
                        "reminder_sent": True
                    }
            else:
                # Motion detected - reset tracking
                STOVE_ABOVE_SECOND_THRESHOLD_START = None
                LAST_REMINDER_TIME = None
    
    # Reset second threshold tracking if temperature drops below threshold
    if temp_celsius <= STOVE_TEMP_SECOND_THRESHOLD_C:
        if STOVE_ABOVE_SECOND_THRESHOLD_START is not None:
            STOVE_ABOVE_SECOND_THRESHOLD_START = None
            LAST_REMINDER_TIME = None
    
    # Thermal warnings based on temperature (from ifmagic_trial.py logic)
    if temp_celsius > STOVE_TEMP_SECOND_THRESHOLD_C:  # Very hot - critical warning (using constant)
        if hardware_ports is not None:
            set_glow_warning(hardware_ports, active=True)
        if AUDIO_AVAILABLE and speak_text:
            if DIALOGUE_AVAILABLE and get_dialogue:
                hot_msg = get_dialogue("heat_warning_warming", "The stove is getting too hot, turn it off")
            else:
                hot_msg = "The stove is getting too hot, turn it off"
            speak_text(hot_msg)
        print(f"🔥 CRITICAL: Stove temperature very high ({temp_celsius}°C) - turn it off")
    elif temp_celsius > STOVE_TEMP_THRESHOLD_C:  # Hot - safety warning (using constant)
        if hardware_ports is not None:
            # Moderate warning - less saturation
            try:
                if hasattr(hardware_ports, 'modules') and hardware_ports.modules[GLOW_PORT] is not None:
                    hardware_ports.modules[GLOW_PORT].out.setFade(
                        start=0, end=2000, hue=100, saturation=175,  # Lower saturation
                        movement=1, speed=1, low=1, high=1, bounce=1
                    )
            except (AttributeError, IndexError):
                pass
        if AUDIO_AVAILABLE and speak_text:
            if DIALOGUE_AVAILABLE and get_dialogue:
                touch_msg = get_dialogue("heat_warning_critical", "It's not safe to touch the stove")
            else:
                touch_msg = "It's not safe to touch the stove"
            speak_text(touch_msg)
        print(f"⚠️  WARNING: Stove is hot ({temp_celsius}°C) - not safe to touch")
    
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
                        if DIALOGUE_AVAILABLE and get_dialogue:
                            alert_msg = get_dialogue("safety_alert", 
                                                    f"Safety alert. Stove is hot at {int(temp_celsius)} degrees. No motion detected for {int(time_since_motion // 60)} minutes. Please return to the kitchen.",
                                                    temp=int(temp_celsius), minutes=int(time_since_motion // 60))
                        else:
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
                    if DIALOGUE_AVAILABLE and get_dialogue:
                        warning_msg = get_dialogue("stove_hot_warning", f"Warning. Stove is hot at {int(temp_celsius)} degrees. Please monitor carefully.",
                                                   temp=int(temp_celsius))
                    else:
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
                if DIALOGUE_AVAILABLE and get_dialogue:
                    warning_msg = get_dialogue("stove_hot_warning", f"Warning. Stove is hot at {int(temp_celsius)} degrees. Motion detected. Please monitor carefully.",
                                               temp=int(temp_celsius))
                else:
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
        if DIALOGUE_AVAILABLE and get_dialogue:
            calm_msg = get_dialogue("pause_button_activated", 
                                   f"De-escalation mode activated. Taking a break. Environment is now calmer. Playing {SAFE_SONG}.",
                                   song=SAFE_SONG)
        else:
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

def check_proximity_to_loud_object(proximity_cm: float, object_name: str, hardware_ports=None) -> Dict[str, any]:
    """
    Detect when a hand is in close proximity to a loud object (blender, garbage disposal, etc.)
    and play a warning message before the object is turned on.
    
    Args:
        proximity_cm: Distance reading from proximity sensor in centimeters (or millimeters, will be converted)
        object_name: Name of the loud object being approached (e.g., "blender", "garbage disposal")
        hardware_ports: Optional hardware object for glow feedback (if hardware mode enabled)
        
    Returns:
        Dictionary with proximity status and action taken
    """
    global CURRENT_PROXIMITY_CM, CURRENT_NEAR_OBJECT, PROXIMITY_THRESHOLD_CM
    
    # Convert mm to cm if needed (ifmagic proximity returns mm)
    proximity_in_cm = proximity_cm / 10.0 if proximity_cm > 100 else proximity_cm
    CURRENT_PROXIMITY_CM = proximity_in_cm
    
    # Check if hand is within warning threshold (100mm = 10cm from ifmagic_trial.py)
    threshold_cm = 10.0  # 100mm threshold from ifmagic_trial.py
    if proximity_in_cm <= threshold_cm:
        CURRENT_NEAR_OBJECT = object_name.lower()
        
        print(f"⚠️  PROXIMITY ALERT: Hand detected {proximity_in_cm:.1f}cm from {object_name}")
        print(f"   → Warning: {object_name.upper()} can create loud noise")
        print(f"   → Activating pre-warning system")
        
        # Activate hardware glow if available
        if hardware_ports is not None:
            set_glow_warning(hardware_ports, active=True)
        
        # Play audio warning
        if AUDIO_AVAILABLE and speak_text:
            if DIALOGUE_AVAILABLE and get_dialogue:
                warning_msg = get_dialogue("proximity_warning", "This item could get loud")
            else:
                warning_msg = "This item could get loud"
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
        # Hand moved away or not close enough - turn off glow
        if hardware_ports is not None:
            set_glow_warning(hardware_ports, active=False)
        
        if CURRENT_NEAR_OBJECT == object_name.lower():
            CURRENT_NEAR_OBJECT = None
            print(f"✅ Hand moved away from {object_name} ({proximity_in_cm:.1f}cm)")
        
        return {
            "action": "proximity_safe",
            "object_name": object_name,
            "proximity_cm": proximity_in_cm,
            "threshold_cm": threshold_cm
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
    global STOVE_ABOVE_SECOND_THRESHOLD_START, STOVE_TEMP_SECOND_THRESHOLD_C, LAST_PROXIMITY_READING
    
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
    print(f"  Stove temp: {STOVE_TEMP_CURRENT}°C")
    print(f"    First threshold: {STOVE_TEMP_THRESHOLD_C}°C")
    print(f"    Second threshold: {STOVE_TEMP_SECOND_THRESHOLD_C}°C")
    if STOVE_ABOVE_SECOND_THRESHOLD_START is not None:
        time_above = int(time.time() - STOVE_ABOVE_SECOND_THRESHOLD_START)
        print(f"    Above second threshold: {time_above}s")
    print(f"  Motion: {'Detected' if MOTION_DETECTED else 'Not detected'}")
    if LAST_PROXIMITY_READING is not None:
        print(f"  Proximity (motion detection): {LAST_PROXIMITY_READING:.1f}cm")
    
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


def run_demo_with_hardware():
    """
    Run kitchen system with ifmagic hardware integration.
    Continuously polls hardware sensors and triggers appropriate responses.
    Replaces keyboard input with hardware sensor readings.
    """
    global LAST_MOTION_TIME, CURRENT_RECIPE, CURRENT_STEP
    
    # Initialize motion time
    if LAST_MOTION_TIME is None:
        LAST_MOTION_TIME = time.time()
    
    print("\n" + "="*60)
    print("KITCHEN SYSTEM - HARDWARE MODE")
    print("="*60)
    print(f"\nConnecting to hardware at {HARDWARE_CONNECTION_PATH}...")
    print("Hardware sensor ports:")
    print(f"  Proximity: Port {PROXIMITY_PORT}")
    print(f"  Sound: Port {SOUND_PORT}")
    print(f"  Thermal: Port {THERMAL_PORT}")
    print(f"  Glow: Port {GLOW_PORT}")
    print("\nSystem is running with hardware sensors...")
    print("(Press Ctrl+C to exit)\n")
    
    try:
        with Magic.Hardware(HARDWARE_CONNECTION_PATH) as h:
            h.connect()
            print("✓ Hardware connected successfully\n")
            
            # Track previous states to avoid repeated warnings
            last_proximity_warning = False
            last_sound_warning = False
            last_temp_warning_level = None  # 'critical', 'warning', or None
            
            while True:
                try:
                    # Read hardware data
                    ports = h.read()
                    
                    # 1. Check proximity sensor (for loud objects and motion detection)
                    proximity_mm = read_proximity_sensor(ports)
                    proximity_cm = None
                    if proximity_mm is not None:
                        # Convert mm to cm for stove safety check (read_proximity_sensor returns mm)
                        proximity_cm = proximity_mm / 10.0
                        # Use default object name "blender" or detect based on context
                        object_name = CURRENT_NEAR_OBJECT if CURRENT_NEAR_OBJECT else "blender"
                        result = check_proximity_to_loud_object(proximity_mm, object_name, hardware_ports=h)
                        last_proximity_warning = (result.get("action") == "proximity_warning_activated")
                    
                    # 2. Check sound sensor (decibel detection)
                    sound_db = read_sound_sensor(ports)
                    if sound_db is not None:
                        result = check_sound_level(sound_db, hardware_ports=h)
                        last_sound_warning = (result.get("action") == "calm_down_activated")
                    
                    # 3. Check thermal sensor (stove temperature) with proximity-based motion detection
                    temp_celsius = read_thermal_sensor(ports)
                    if temp_celsius is not None:
                        # Determine motion status (could read from motion sensor if available)
                        # For now, use current global state or assume motion based on recent activity
                        motion_status = MOTION_DETECTED if time.time() - (LAST_MOTION_TIME or 0) < 10 else False
                        # Pass proximity reading for motion detection (in cm, will be converted to mm in check_stove_safety)
                        result = check_stove_safety(temp_celsius, motion_status, hardware_ports=h, proximity_cm=proximity_cm)
                        
                        # Track warning level for glow management
                        if result.get("action") in ["safety_alert", "stove_hot_warning"]:
                            last_temp_warning_level = 'critical'
                        elif temp_celsius > 50:
                            last_temp_warning_level = 'warning'
                        else:
                            last_temp_warning_level = None
                    
                    # 4. Update recipe step glow visualization (if recipe is active)
                    if CURRENT_RECIPE is not None and CURRENT_STEP < len(CURRENT_RECIPE.get('steps', [])):
                        set_glow_recipe_step(h, CURRENT_STEP, len(CURRENT_RECIPE['steps']))
                    
                    # 5. Check timer status periodically
                    if TIMER_ACTIVE:
                        timer_status = check_timer()
                        if timer_status["action"] == "timer_complete":
                            pass  # Timer completed - already handled in check_timer()
                    
                    # Small delay to prevent overwhelming the system
                    time.sleep(0.1)  # Check sensors 10 times per second
                    
                except KeyboardInterrupt:
                    print("\n\nExiting hardware mode...")
                    # Turn off all glows before exiting
                    try:
                        set_glow_warning(h, active=False)
                    except:
                        pass
                    h.disconnect()
                    break
                    
                except Exception as e:
                    print(f"Error reading hardware: {e}")
                    import traceback
                    traceback.print_exc()
                    time.sleep(1)  # Wait before retrying
                    
    except Exception as e:
        print(f"Error connecting to hardware: {e}")
        print("\nTroubleshooting:")
        print("1. Check connection path is correct for your system")
        print("2. Ensure hardware is connected and powered on")
        print("3. Verify modules are properly connected to the specified ports")
        print("4. Check port assignments in HARDWARE configuration section")
        import traceback
        traceback.print_exc()


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
    # Choose between hardware mode and keyboard input mode
    # Set HARDWARE_ENABLED = True to use hardware sensors, False for keyboard input
    if HARDWARE_ENABLED:
        run_demo_with_hardware()
    else:
        run_demo()