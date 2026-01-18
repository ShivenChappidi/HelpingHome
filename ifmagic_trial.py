from indistinguishable_from_magic import magic as Magic
import time
import sys
import os

# Add project root to path so we can import utils
_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = _script_dir
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import audio agent (11labs)
try:
    from utils.audio import speak_text
    AUDIO_AVAILABLE = True
except Exception as e:
    AUDIO_AVAILABLE = False
    speak_text = None
    print(f"[DEBUG] Audio import failed: {e}")

# Import dialogue variations
try:
    from utils.dialogues import get_dialogue
    DIALOGUES_AVAILABLE = True
except Exception as e:
    DIALOGUES_AVAILABLE = False
    # Fallback function that just returns the default text
    def get_dialogue(message_type, default_text):
        return default_text
    print(f"[DEBUG] Dialogues import failed: {e}")

# Import event logger
try:
    from utils.event_logger import log_event
    EVENT_LOGGING_AVAILABLE = True
    print("[DEBUG] Event logging module imported successfully")
except Exception as e:
    EVENT_LOGGING_AVAILABLE = False
    log_event = None
    print(f"[DEBUG] Event logging import failed: {e}")
    import traceback
    traceback.print_exc()

# Import requests for API calls
try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception as e:
    REQUESTS_AVAILABLE = False
    print(f"[DEBUG] Requests module not available: {e}")

steps = ["step 1", "step 2", "step 3"]

# Recipe guidance state
RECIPE_GUIDANCE_STATE = {
    "active": False,
    "recipe_id": None,
    "recipe_name": None,
    "steps": [],
    "current_step": 0,
    "recipe_name_announced": False,
    "first_step_announced": False,
    "last_pressure_value": 0,
    "pressure_threshold": 100  # Threshold for detecting pressure sensor press
}

# Routine guidance state (for bathroom)
ROUTINE_GUIDANCE_STATE = {
    "active": False,
    "routine_id": None,
    "routine_name": None,
    "steps": [],
    "current_step": 0,
    "routine_name_announced": False,
    "first_step_announced": False,
    "last_proximity_value": 999,  # Start with high value (far away)
    "proximity_threshold": 100  # Threshold in millimeters for detecting hand near proximity sensor
}

# Laundry routine guidance state (for laundry room - uses pressure sensor)
LAUNDRY_ROUTINE_GUIDANCE_STATE = {
    "active": False,
    "routine_id": None,
    "routine_name": None,
    "steps": [],
    "current_step": 0,
    "routine_name_announced": False,
    "first_step_announced": False,
    "last_pressure_value": 0,
    "pressure_threshold": 100,  # Threshold for detecting pressure sensor press
    "monitoring_mode": False,  # After last step, monitor for cycle completion
    "zero_value_start_time": None,  # When we first detected zero pressure
    "completion_detected": False  # Flag to prevent duplicate notifications
}

API_BASE_URL = "http://localhost:5001/api"

sound_port = 0
force_port = 1
proximity_port = 2
thermal_port = 3
glow_port_prox = 4
glow_port_heat = 5
glow_port_decibel = 6
vibration_port = 7
glow_port_recipe = 8  # Glow port for recipe step indication
glow_port_routine = 9  # Glow port for routine step indication (bathroom)
glow_port_laundry = 10  # Glow port for laundry routine step indication

# State tracking for event logging (prevent duplicate logs for same warning state)
# Only log when transitioning from False -> True (warning appears)
_warning_states = {
    "proximity": False,
    "heat_critical": False,
    "heat_warning": False,
    "cold_water": False,  # For bathroom water temperature
    "decibel": False
}  


prox_warning_fade = (0,6,25,255,1,500,0,64,1)
heat_warning_fade = (0,6,10,255,1,500,0,64,1)
decibel_warning_fade = (0,6,200,255,1,500,0,64,1)
cold_water_warning_fade = (0,6,150,255,1,500,0,64,1)
# Step progress indicator fade tuples (green for progress)
recipe_step_fade = (0,6,85,255,1,500,32,64,1)  # Green hue for recipe steps
routine_step_fade = (0,6,85,255,1,500,32,64,1)  # Green hue for routine steps
laundry_step_fade = (0,6,85,255,1,500,32,64,1)  # Green hue for laundry steps 


class led_output:
    def __init__(self, on, off):
        self.on = on
        self.off = off
        self.pv = 0
    def __call__(self, v):
        if v != self.pv:
            self.pv = v
            [self.off,self.on][v]()


def proximity_warning(ports,warner,room="kitchen"):
    global _warning_states
    howClose = int(ports.modules[proximity_port].data.milimeters)
    
    if howClose < 200:
        warner(1)  # Turn on warning LED via led_output object
        
        # Only log event when transitioning from False -> True (warning first appears)
        if not _warning_states["proximity"]:
            # Audio output via 11labs
            message = get_dialogue("proximity_warning", "This item could get loud")
            if AUDIO_AVAILABLE and speak_text:
                speak_text(message)
            else:
                print(message)
            
            # Log event to activity monitor (ONLY on state transition)
            if EVENT_LOGGING_AVAILABLE and log_event:
                print(f"[DEBUG] Logging proximity warning event: {howClose}mm")
                log_event(
                    event_type="proximity_warning",
                    message=f"Proximity warning: Hand detected {howClose}mm from loud object",
                    room=room,
                    severity="warning",
                    metadata={"distance_mm": howClose, "threshold_mm": 200}
                )
                print("[DEBUG] Proximity warning event logged successfully")
            else:
                print(f"[DEBUG] Event logging not available. EVENT_LOGGING_AVAILABLE={EVENT_LOGGING_AVAILABLE}, log_event={log_event}")
            
            _warning_states["proximity"] = True
    else:
        warner(0)  # Turn off warning LED via led_output object
        _warning_states["proximity"] = False

def routine(ports):
    for step in steps:
        ind = int(steps.index(step))
        #ports.modules[glow_port].out.setFade(ind,ind+1,75+ind*25,255,1,500,32,64,1)
        # Audio output via 11labs
        if AUDIO_AVAILABLE and speak_text:
            speak_text(step)
        else:
            print(step)

def heat_warning(ports,warner,room="kitchen",temp_type="stove",cold_warner=None):
    global _warning_states
    pixels = ports.modules[thermal_port].data.pixel_temperatures;
    center_avg = sum(pixels[i][j] for i in range(2,6) for j in range(2,6))/16
    
    # Check for cold water (only for bathroom/water temp_type)
    if temp_type == "water" and center_avg < 14:
        # Use cold water warning LED if provided, otherwise use regular warner
        if cold_warner is not None:
            cold_warner(1)  # Turn on blue cold water warning LED
        else:
            warner(1)  # Fallback to regular warner if cold_warner not provided
        
        # Only log event when transitioning from False -> True (warning first appears)
        if not _warning_states["cold_water"]:
            # Audio output via 11labs
            message = get_dialogue("cold_water_warning", "The water is a little cold")
            if AUDIO_AVAILABLE and speak_text:
                speak_text(message)
            else:
                print(message)
            
            # Log cold water warning event (ONLY on state transition)
            if EVENT_LOGGING_AVAILABLE and log_event:
                print(f"[DEBUG] Logging cold water warning event: {center_avg:.1f}°C")
                log_event(
                    event_type="cold_water_warning",
                    message=f"Warning: Water temperature is cold ({center_avg:.1f}°C) - below comfortable level",
                    room=room,
                    severity="warning",
                    metadata={"temperature_c": center_avg, "threshold_c": 14, "temp_type": "water"}
                )
                print("[DEBUG] Cold water warning event logged successfully")
            
            _warning_states["cold_water"] = True
            # Reset heat warning states when cold detected
            _warning_states["heat_critical"] = False
            _warning_states["heat_warning"] = False
        return  # Early return to skip heat checks when water is cold
    
    # Reset cold water warning if temperature is above threshold
    if temp_type == "water" and center_avg >= 14:
        if _warning_states["cold_water"]:
            _warning_states["cold_water"] = False
            # Use cold water warning LED if provided, otherwise use regular warner
            if cold_warner is not None:
                cold_warner(0)  # Turn off blue cold water warning LED
            else:
                warner(0)  # Fallback to regular warner if cold_warner not provided
    
    # Check for hot water/stove (existing logic)
    if center_avg > 50:
        warner(1)#ports.modules[glow_port].out.setFade(*heat_warning_fade)
        
        # Only log event when transitioning from False -> True (critical warning first appears)
        if not _warning_states["heat_critical"]:
            # Audio output via 11labs - different message for bathroom vs kitchen
            if temp_type == "water":
                message = get_dialogue("water_heat_warning_critical", "Warning. The water is very hot. Please be careful.")
            else:
                message = get_dialogue("heat_warning_critical", "It's not safe to touch the stove")
            if AUDIO_AVAILABLE and speak_text:
                speak_text(message)
            else:
                print(message)
            
            # Log critical heat warning event (ONLY on state transition)
            if EVENT_LOGGING_AVAILABLE and log_event:
                print(f"[DEBUG] Logging critical heat warning event: {center_avg:.1f}°C")
                log_event(
                    event_type="heat_warning_critical",
                    message=f"Critical: {temp_type.capitalize()} temperature high ({center_avg:.1f}°C) - not safe to touch",
                    room=room,
                    severity="critical",
                    metadata={"temperature_c": center_avg, "threshold_c": 50, "temp_type": temp_type}
                )
                print("[DEBUG] Critical heat warning event logged successfully")
            else:
                print(f"[DEBUG] Event logging not available. EVENT_LOGGING_AVAILABLE={EVENT_LOGGING_AVAILABLE}, log_event={log_event}")
            
            _warning_states["heat_critical"] = True
            _warning_states["heat_warning"] = False  # Reset lower warning state
    elif (temp_type == "water" and center_avg > 39) or (temp_type == "stove" and center_avg > 25):
        warner(1)#ports.modules[glow_port].out.setFade(*heat_warning_fade)
        
        # Only log event when transitioning from False -> True (warning first appears, and not already critical)
        if not _warning_states["heat_warning"] and not _warning_states["heat_critical"]:
            # Audio output via 11labs - different message for bathroom vs kitchen
            if temp_type == "water":
                message = get_dialogue("water_heat_warning_warming", "The water is getting too hot, turn it off")
            else:
                message = get_dialogue("heat_warning_warming", "The stove is getting too hot, turn it off")
            if AUDIO_AVAILABLE and speak_text:
                speak_text(message)
            else:
                print(message)
            
            # Log heat warning event (ONLY on state transition)
            if EVENT_LOGGING_AVAILABLE and log_event:
                print(f"[DEBUG] Logging heat warning event: {center_avg:.1f}°C")
                # Use appropriate threshold for water vs stove
                threshold = 39 if temp_type == "water" else 25
                log_event(
                    event_type="heat_warning",
                    message=f"Warning: {temp_type.capitalize()} temperature rising ({center_avg:.1f}°C)",
                    room=room,
                    severity="warning",
                    metadata={"temperature_c": center_avg, "threshold_c": threshold, "temp_type": temp_type}
                )
                print("[DEBUG] Heat warning event logged successfully")
            else:
                print(f"[DEBUG] Event logging not available. EVENT_LOGGING_AVAILABLE={EVENT_LOGGING_AVAILABLE}, log_event={log_event}")
            
            _warning_states["heat_warning"] = True
    else:
        # Normal temperature range (14-39°C for water, or <25°C for stove)
        # Only turn off warning LED if we're not in cold water state
        if not (temp_type == "water" and center_avg < 14):
            warner(0)#ports.modules[glow_port].out.setBrightness(*heat_warning_fade[:2],255)
        _warning_states["heat_critical"] = False
        _warning_states["heat_warning"] = False
        # Note: cold_water state is already reset above when temp >= 14
   

def decibel_detector(ports,warner,room="kitchen"):
    global _warning_states
    volume = int(ports.modules[sound_port].data.volume)
    
    if volume > 1500:
        warner(1)#ports.modules[glow_port].out.setFade(*decibel_warning_fade)
        
        # Only log event when transitioning from False -> True (warning first appears)
        if not _warning_states["decibel"]:
            # Audio output via 11labs
            message = get_dialogue("volume_warning", "Sounds like the volume is getting too high")
            if AUDIO_AVAILABLE and speak_text:
                speak_text(message)
            else:
                print(message)
            
            # Log decibel warning event (ONLY on state transition)
            if EVENT_LOGGING_AVAILABLE and log_event:
                print(f"[DEBUG] Logging decibel warning event: volume={volume}")
                log_event(
                    event_type="decibel_warning",
                    message=f"High volume detected ({volume}) - loud noise warning",
                    room=room,
                    severity="warning",
                    metadata={"volume": volume, "threshold": 1500}
                )
                print("[DEBUG] Decibel warning event logged successfully")
            else:
                print(f"[DEBUG] Event logging not available. EVENT_LOGGING_AVAILABLE={EVENT_LOGGING_AVAILABLE}, log_event={log_event}")
            
            _warning_states["decibel"] = True
    else:
        warner(0)#ports.modules[glow_port].out.setBrightness(*decibel_warning_fade[:2],255)
        _warning_states["decibel"] = False


def check_active_recipe():
    """Check API for active recipe guidance."""
    global RECIPE_GUIDANCE_STATE
    
    if not REQUESTS_AVAILABLE:
        return
    
    try:
        response = requests.get(f"{API_BASE_URL}/recipe-guidance/get-active", timeout=0.5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data.get("active") and data.get("recipe"):
                recipe = data["recipe"]
                # Update state if recipe changed
                if RECIPE_GUIDANCE_STATE["recipe_id"] != data.get("recipe_id"):
                    RECIPE_GUIDANCE_STATE["active"] = True
                    RECIPE_GUIDANCE_STATE["recipe_id"] = data.get("recipe_id")
                    RECIPE_GUIDANCE_STATE["recipe_name"] = recipe.get("name", data.get("recipe_id"))
                    RECIPE_GUIDANCE_STATE["steps"] = recipe.get("steps", [])
                    RECIPE_GUIDANCE_STATE["current_step"] = 0
                    RECIPE_GUIDANCE_STATE["recipe_name_announced"] = False
                    RECIPE_GUIDANCE_STATE["first_step_announced"] = False
                    print(f"[RECIPE] Active recipe loaded: {RECIPE_GUIDANCE_STATE['recipe_name']}")
                else:
                    # Just update active flag
                    RECIPE_GUIDANCE_STATE["active"] = True
            else:
                # No active recipe
                if RECIPE_GUIDANCE_STATE["active"]:
                    print("[RECIPE] Recipe guidance stopped")
                RECIPE_GUIDANCE_STATE["active"] = False
                RECIPE_GUIDANCE_STATE["recipe_name_announced"] = False
                RECIPE_GUIDANCE_STATE["first_step_announced"] = False
        else:
            # API error - keep current state
            pass
    except Exception as e:
        # API call failed - keep current state (allows offline mode)
        pass


def update_recipe_leds(ports, current_step: int, total_steps: int):
    """
    Update glow port LEDs to show recipe step progress.
    Lights up LEDs sequentially as steps are completed.
    
    Args:
        ports: Hardware ports object
        current_step: Current step index (0-based)
        total_steps: Total number of steps in recipe
    """
    try:
        if hasattr(ports, 'modules') and ports.modules[glow_port_recipe] is not None:
            module = ports.modules[glow_port_recipe]
            if hasattr(module, 'out'):
                # Light up LEDs based on progress
                # Use fade for active steps, brightness for completed steps
                if current_step < total_steps:
                    # Current step - use fade animation (green)
                    module.out.setFade(*recipe_step_fade)
                elif current_step >= total_steps:
                    # All steps complete - pulse or steady green
                    module.out.setFade(*recipe_step_fade)
    except (AttributeError, IndexError) as e:
        pass


def update_routine_leds(ports, current_step: int, total_steps: int, glow_port: int, fade_tuple: tuple):
    """
    Update glow port LEDs to show routine step progress.
    Lights up LEDs sequentially as steps are completed.
    
    Args:
        ports: Hardware ports object
        current_step: Current step index (0-based)
        total_steps: Total number of steps in routine
        glow_port: Glow port number to use
        fade_tuple: Fade tuple to use for the LED color
    """
    try:
        if not hasattr(ports, 'modules'):
            return
        if not ports.modules or len(ports.modules) <= glow_port:
            return
        if ports.modules[glow_port] is None:
            return
            
        module = ports.modules[glow_port]
        if not hasattr(module, 'out'):
            return
            
        # Light up LEDs based on progress - always activate when routine is active
        if hasattr(module.out, 'setFade'):
            module.out.setFade(*fade_tuple)
        elif hasattr(module.out, 'setBrightness'):
            # Fallback to setBrightness if setFade not available
            # Convert fade tuple to brightness: fade_tuple is (start, end, hue, saturation, ...)
            module.out.setBrightness(fade_tuple[0], fade_tuple[1], fade_tuple[2] if len(fade_tuple) > 2 else 2000)
    except (AttributeError, IndexError, TypeError) as e:
        print(f"[ROUTINE LED] Error updating LEDs on port {glow_port}: {e}")


def handle_recipe_guidance(ports):
    """Handle recipe guidance with pressure sensor input."""
    global RECIPE_GUIDANCE_STATE
    
    # Check for active recipe from API (every so often)
    check_active_recipe()
    
    if not RECIPE_GUIDANCE_STATE["active"] or not RECIPE_GUIDANCE_STATE["steps"]:
        # Turn off recipe LEDs when no active recipe
        try:
            if hasattr(ports, 'modules') and ports.modules[glow_port_recipe] is not None:
                ports.modules[glow_port_recipe].out.setBrightness(0, 6, 0)
        except:
            pass
        return
    
    # Announce recipe name if not yet announced
    if not RECIPE_GUIDANCE_STATE["recipe_name_announced"]:
        recipe_name = RECIPE_GUIDANCE_STATE["recipe_name"]
        message = f"Starting recipe: {recipe_name}"
        if AUDIO_AVAILABLE and speak_text:
            speak_text(message)
        else:
            print(f"[RECIPE] {message}")
        RECIPE_GUIDANCE_STATE["recipe_name_announced"] = True
        RECIPE_GUIDANCE_STATE["first_step_announced"] = False
        return  # Wait for next iteration to announce first step
    
    # Announce first step if recipe name was just announced
    if not RECIPE_GUIDANCE_STATE["first_step_announced"]:
        current_step = RECIPE_GUIDANCE_STATE["current_step"]
        if current_step < len(RECIPE_GUIDANCE_STATE["steps"]):
            step_text = RECIPE_GUIDANCE_STATE["steps"][current_step]
            message = f"Step {current_step + 1}: {step_text}"
            if AUDIO_AVAILABLE and speak_text:
                speak_text(message)
            else:
                print(f"[RECIPE] {message}")
            RECIPE_GUIDANCE_STATE["first_step_announced"] = True
            # Update LEDs for first step
            update_recipe_leds(ports, current_step, len(RECIPE_GUIDANCE_STATE["steps"]))
        return  # Wait for pressure sensor to advance to next step
    
    # Continuously update LEDs to show current step progress (even while waiting for input)
    current_step = RECIPE_GUIDANCE_STATE["current_step"]
    update_recipe_leds(ports, current_step, len(RECIPE_GUIDANCE_STATE["steps"]))
    
    # Check pressure sensor for next step
    try:
        # Try different possible property paths for pressure sensor
        pressure_value = 0
        if hasattr(ports, 'modules') and ports.modules[force_port] is not None:
            module = ports.modules[force_port]
            # Try data.strength first (based on user's documentation)
            if hasattr(module, 'data') and hasattr(module.data, 'strength'):
                pressure_value = int(module.data.strength)
            # Fallback: try strength directly
            elif hasattr(module, 'strength'):
                pressure_value = int(module.strength)
            # Fallback: try data.amount or amount
            elif hasattr(module, 'data') and hasattr(module.data, 'amount'):
                pressure_value = int(module.data.amount)
            elif hasattr(module, 'amount'):
                pressure_value = int(module.amount())
        
        # Detect pressure sensor press (pressure > threshold and was previously low)
        last_pressure = RECIPE_GUIDANCE_STATE["last_pressure_value"]
        threshold = RECIPE_GUIDANCE_STATE["pressure_threshold"]
        
        if pressure_value > threshold and last_pressure <= threshold:
            # Pressure sensor pressed - advance to next step
            RECIPE_GUIDANCE_STATE["current_step"] += 1
            current_step = RECIPE_GUIDANCE_STATE["current_step"]
            
            # Update LEDs to show progress
            update_recipe_leds(ports, current_step, len(RECIPE_GUIDANCE_STATE["steps"]))
            
            if current_step < len(RECIPE_GUIDANCE_STATE["steps"]):
                step_text = RECIPE_GUIDANCE_STATE["steps"][current_step]
                message = f"Step {current_step + 1}: {step_text}"
                if AUDIO_AVAILABLE and speak_text:
                    speak_text(message)
                else:
                    print(f"[RECIPE] {message}")
            else:
                # Recipe complete - keep LEDs on to show completion
                recipe_name = RECIPE_GUIDANCE_STATE["recipe_name"]
                message = f"Recipe complete! Great job making {recipe_name}."
                if AUDIO_AVAILABLE and speak_text:
                    speak_text(message)
                else:
                    print(f"[RECIPE] {message}")
                # Keep LEDs on for completion, reset state (will be deactivated by API check)
                update_recipe_leds(ports, current_step, len(RECIPE_GUIDANCE_STATE["steps"]))
                RECIPE_GUIDANCE_STATE["active"] = False
        
        RECIPE_GUIDANCE_STATE["last_pressure_value"] = pressure_value
    except Exception as e:
        # Error reading pressure sensor - continue silently
        pass


def load_default_routines():
    """Load default routines from routines.json file."""
    import json
    import os
    routines_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'routines.json')
    
    if os.path.exists(routines_file):
        try:
            with open(routines_file, 'r', encoding='utf-8') as f:
                routines = json.load(f)
                return routines
        except Exception as e:
            print(f"[ROUTINE] Error loading routines: {e}")
            return {}
    else:
        # Return default routines if file doesn't exist
        return {
            "washing_hands": {
                "name": "Washing Hands",
                "description": "Complete hand washing routine",
                "steps": [
                    "Turn on the water and wet your hands",
                    "Apply soap to your hands",
                    "Scrub your hands together for 20 seconds",
                    "Rinse your hands thoroughly with water",
                    "Dry your hands with a towel"
                ]
            },
            "cleaning_bathroom": {
                "name": "Cleaning the Bathroom",
                "description": "Complete bathroom cleaning routine",
                "steps": [
                    "Gather cleaning supplies: spray, sponge, and paper towels",
                    "Spray the sink and counter with cleaning solution",
                    "Wipe down the sink, counter, and mirror",
                    "Clean the toilet with disinfectant",
                    "Sweep or mop the floor and put supplies away"
                ]
            }
        }


def start_routine(routine_id):
    """Start a routine by ID."""
    global ROUTINE_GUIDANCE_STATE
    
    routines = load_default_routines()
    
    if routine_id not in routines:
        print(f"[ROUTINE] Error: Routine '{routine_id}' not found")
        return False
    
    routine = routines[routine_id]
    ROUTINE_GUIDANCE_STATE["active"] = True
    ROUTINE_GUIDANCE_STATE["routine_id"] = routine_id
    ROUTINE_GUIDANCE_STATE["routine_name"] = routine.get("name", routine_id)
    ROUTINE_GUIDANCE_STATE["steps"] = routine.get("steps", [])
    ROUTINE_GUIDANCE_STATE["current_step"] = 0
    ROUTINE_GUIDANCE_STATE["routine_name_announced"] = False
    ROUTINE_GUIDANCE_STATE["first_step_announced"] = False
    ROUTINE_GUIDANCE_STATE["last_proximity_value"] = 999  # Start far away
    
    print(f"[ROUTINE] Routine started: {ROUTINE_GUIDANCE_STATE['routine_name']}")
    return True


def check_active_routine():
    """Check API for active routine guidance."""
    global ROUTINE_GUIDANCE_STATE
    
    if not REQUESTS_AVAILABLE:
        return
    
    try:
        response = requests.get(f"{API_BASE_URL}/routine-guidance/get-active", timeout=0.5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data.get("active") and data.get("routine"):
                routine = data["routine"]
                # Update state if routine changed
                if ROUTINE_GUIDANCE_STATE["routine_id"] != data.get("routine_id"):
                    ROUTINE_GUIDANCE_STATE["active"] = True
                    ROUTINE_GUIDANCE_STATE["routine_id"] = data.get("routine_id")
                    ROUTINE_GUIDANCE_STATE["routine_name"] = routine.get("name", data.get("routine_id"))
                    ROUTINE_GUIDANCE_STATE["steps"] = routine.get("steps", [])
                    ROUTINE_GUIDANCE_STATE["current_step"] = 0
                    ROUTINE_GUIDANCE_STATE["routine_name_announced"] = False
                    ROUTINE_GUIDANCE_STATE["first_step_announced"] = False
                    print(f"[ROUTINE] Active routine loaded: {ROUTINE_GUIDANCE_STATE['routine_name']}")
                else:
                    # Just update active flag
                    ROUTINE_GUIDANCE_STATE["active"] = True
            else:
                # No active routine
                if ROUTINE_GUIDANCE_STATE["active"]:
                    print("[ROUTINE] Routine guidance stopped")
                ROUTINE_GUIDANCE_STATE["active"] = False
                ROUTINE_GUIDANCE_STATE["routine_name_announced"] = False
                ROUTINE_GUIDANCE_STATE["first_step_announced"] = False
        else:
            # API error - keep current state
            pass
    except Exception as e:
        # API call failed - keep current state (allows offline mode)
        pass


def handle_routine_guidance(ports):
    """Handle routine guidance with proximity sensor input (bathroom)."""
    global ROUTINE_GUIDANCE_STATE
    
    # Check for active routine
    check_active_routine()
    
    if not ROUTINE_GUIDANCE_STATE["active"] or not ROUTINE_GUIDANCE_STATE["steps"]:
        # Turn off routine LEDs when no active routine
        try:
            if hasattr(ports, 'modules') and ports.modules[glow_port_routine] is not None:
                ports.modules[glow_port_routine].out.setBrightness(0, 6, 0)
        except:
            pass
        return
    
    # Update LEDs to show current step progress
    current_step = ROUTINE_GUIDANCE_STATE["current_step"]
    total_steps = len(ROUTINE_GUIDANCE_STATE["steps"])
    update_routine_leds(ports, current_step, total_steps, glow_port_routine, routine_step_fade)
    
    # Announce routine name if not yet announced
    if not ROUTINE_GUIDANCE_STATE["routine_name_announced"]:
        routine_name = ROUTINE_GUIDANCE_STATE["routine_name"]
        message = f"Starting routine: {routine_name}"
        if AUDIO_AVAILABLE and speak_text:
            speak_text(message)
        else:
            print(f"[ROUTINE] {message}")
        ROUTINE_GUIDANCE_STATE["routine_name_announced"] = True
        ROUTINE_GUIDANCE_STATE["first_step_announced"] = False
        return  # Wait for next iteration to announce first step
    
    # Announce first step if routine name was just announced
    if not ROUTINE_GUIDANCE_STATE["first_step_announced"]:
        current_step = ROUTINE_GUIDANCE_STATE["current_step"]
        if current_step < len(ROUTINE_GUIDANCE_STATE["steps"]):
            step_text = ROUTINE_GUIDANCE_STATE["steps"][current_step]
            message = f"Step {current_step + 1}: {step_text}"
            if AUDIO_AVAILABLE and speak_text:
                speak_text(message)
            else:
                print(f"[ROUTINE] {message}")
            ROUTINE_GUIDANCE_STATE["first_step_announced"] = True
            # Update LEDs for first step
            update_routine_leds(ports, current_step, len(ROUTINE_GUIDANCE_STATE["steps"]), glow_port_routine, routine_step_fade)
        return  # Wait for proximity sensor to advance to next step
    
    # Check if we've already completed all steps - don't process proximity sensor if complete
    current_step = ROUTINE_GUIDANCE_STATE["current_step"]
    if current_step >= len(ROUTINE_GUIDANCE_STATE["steps"]):
        # Routine already complete - deactivate and stop checking proximity sensor
        ROUTINE_GUIDANCE_STATE["active"] = False
        return
    
    # Check proximity sensor for next step (port 2)
    try:
        proximity_value = 999  # Default far away
        if hasattr(ports, 'modules') and ports.modules[proximity_port] is not None:
            module = ports.modules[proximity_port]
            # Try different possible property paths for proximity sensor
            if hasattr(module, 'data') and hasattr(module.data, 'milimeters'):
                proximity_value = int(module.data.milimeters)
            elif hasattr(module, 'data') and hasattr(module.data, 'millimeters'):
                proximity_value = int(module.data.millimeters)
            elif hasattr(module, 'distance'):
                proximity_value = int(module.distance)
        
        # Detect proximity sensor trigger (hand within 100mm threshold)
        last_proximity = ROUTINE_GUIDANCE_STATE["last_proximity_value"]
        threshold = ROUTINE_GUIDANCE_STATE["proximity_threshold"]
        
        # Trigger when hand comes within threshold (proximity < threshold) and was previously far away
        if proximity_value < threshold and last_proximity >= threshold:
            # Hand detected near proximity sensor - advance to next step
            ROUTINE_GUIDANCE_STATE["current_step"] += 1
            current_step = ROUTINE_GUIDANCE_STATE["current_step"]
            
            # Update LEDs to show progress
            update_routine_leds(ports, current_step, len(ROUTINE_GUIDANCE_STATE["steps"]), glow_port_routine, routine_step_fade)
            
            if current_step < len(ROUTINE_GUIDANCE_STATE["steps"]):
                step_text = ROUTINE_GUIDANCE_STATE["steps"][current_step]
                message = f"Step {current_step + 1}: {step_text}"
                if AUDIO_AVAILABLE and speak_text:
                    speak_text(message)
                else:
                    print(f"[ROUTINE] {message}")
            else:
                # Routine complete - last step finished, keep LEDs on
                routine_name = ROUTINE_GUIDANCE_STATE["routine_name"]
                message = f"Routine complete! Great job completing {routine_name}."
                if AUDIO_AVAILABLE and speak_text:
                    speak_text(message)
                else:
                    print(f"[ROUTINE] {message}")
                # Keep LEDs on to show completion
                update_routine_leds(ports, current_step, len(ROUTINE_GUIDANCE_STATE["steps"]), glow_port_routine, routine_step_fade)
                # Reset state and stop processing proximity sensor
                ROUTINE_GUIDANCE_STATE["active"] = False
                return  # Exit immediately after completion - don't check proximity sensor again
        
        ROUTINE_GUIDANCE_STATE["last_proximity_value"] = proximity_value
    except Exception as e:
        # Error reading proximity sensor - continue silently
        pass


def check_active_laundry_routine():
    """Check API for active laundry routine guidance."""
    global LAUNDRY_ROUTINE_GUIDANCE_STATE
    
    if not REQUESTS_AVAILABLE:
        return
    
    try:
        response = requests.get(f"{API_BASE_URL}/laundry-routine-guidance/get-active", timeout=0.5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and data.get("active") and data.get("routine"):
                routine = data["routine"]
                # Update state if routine changed
                if LAUNDRY_ROUTINE_GUIDANCE_STATE["routine_id"] != data.get("routine_id"):
                    LAUNDRY_ROUTINE_GUIDANCE_STATE["active"] = True
                    LAUNDRY_ROUTINE_GUIDANCE_STATE["routine_id"] = data.get("routine_id")
                    LAUNDRY_ROUTINE_GUIDANCE_STATE["routine_name"] = routine.get("name", data.get("routine_id"))
                    LAUNDRY_ROUTINE_GUIDANCE_STATE["steps"] = routine.get("steps", [])
                    LAUNDRY_ROUTINE_GUIDANCE_STATE["current_step"] = 0
                    LAUNDRY_ROUTINE_GUIDANCE_STATE["routine_name_announced"] = False
                    LAUNDRY_ROUTINE_GUIDANCE_STATE["first_step_announced"] = False
                    LAUNDRY_ROUTINE_GUIDANCE_STATE["monitoring_mode"] = False
                    LAUNDRY_ROUTINE_GUIDANCE_STATE["zero_value_start_time"] = None
                    LAUNDRY_ROUTINE_GUIDANCE_STATE["completion_detected"] = False
                    print(f"[LAUNDRY] Active routine loaded: {LAUNDRY_ROUTINE_GUIDANCE_STATE['routine_name']}")
                else:
                    # Just update active flag
                    LAUNDRY_ROUTINE_GUIDANCE_STATE["active"] = True
            else:
                # No active routine
                if LAUNDRY_ROUTINE_GUIDANCE_STATE["active"]:
                    print("[LAUNDRY] Laundry routine guidance stopped")
                LAUNDRY_ROUTINE_GUIDANCE_STATE["active"] = False
                LAUNDRY_ROUTINE_GUIDANCE_STATE["routine_name_announced"] = False
                LAUNDRY_ROUTINE_GUIDANCE_STATE["first_step_announced"] = False
                LAUNDRY_ROUTINE_GUIDANCE_STATE["monitoring_mode"] = False
        else:
            # API error - keep current state
            pass
    except Exception as e:
        # API call failed - keep current state (allows offline mode)
        pass


def handle_laundry_routine_guidance(ports):
    """Handle laundry routine guidance with pressure sensor input.
    
    After the last step is completed, switches to monitoring mode:
    - Monitors pressure sensor for 10 seconds of consistent zero values
    - When detected, sends notification to frontend that load is done
    - After completion is detected, pressure sensor readings are completely ignored
    """
    global LAUNDRY_ROUTINE_GUIDANCE_STATE
    
    # Check for active laundry routine
    check_active_laundry_routine()
    
    # If completion was already detected, completely ignore all pressure sensor readings
    if LAUNDRY_ROUTINE_GUIDANCE_STATE["completion_detected"]:
        # Keep LEDs on to show completion
        current_step = LAUNDRY_ROUTINE_GUIDANCE_STATE["current_step"]
        total_steps = len(LAUNDRY_ROUTINE_GUIDANCE_STATE["steps"]) if LAUNDRY_ROUTINE_GUIDANCE_STATE["steps"] else 1
        update_routine_leds(ports, current_step, total_steps, glow_port_laundry, laundry_step_fade)
        return
    
    if not LAUNDRY_ROUTINE_GUIDANCE_STATE["active"] or not LAUNDRY_ROUTINE_GUIDANCE_STATE["steps"]:
        # Turn off laundry LEDs when no active routine
        try:
            if hasattr(ports, 'modules') and ports.modules[glow_port_laundry] is not None:
                ports.modules[glow_port_laundry].out.setBrightness(0, 6, 0)
        except:
            pass
        return
    
    # Update LEDs to show current step progress (even in monitoring mode)
    current_step = LAUNDRY_ROUTINE_GUIDANCE_STATE["current_step"]
    total_steps = len(LAUNDRY_ROUTINE_GUIDANCE_STATE["steps"])
    update_routine_leds(ports, current_step, total_steps, glow_port_laundry, laundry_step_fade)
    
    # If in monitoring mode (after last step), check for cycle completion
    if LAUNDRY_ROUTINE_GUIDANCE_STATE["monitoring_mode"]:
        try:
            # Read pressure sensor
            pressure_value = 0
            if hasattr(ports, 'modules') and ports.modules[force_port] is not None:
                module = ports.modules[force_port]
                if hasattr(module, 'data') and hasattr(module.data, 'strength'):
                    pressure_value = int(module.data.strength)
                elif hasattr(module, 'strength'):
                    pressure_value = int(module.strength)
                elif hasattr(module, 'data') and hasattr(module.data, 'amount'):
                    pressure_value = int(module.data.amount)
                elif hasattr(module, 'amount'):
                    pressure_value = int(module.amount())
            
            # Check if pressure is zero (washing machine stopped vibrating)
            if pressure_value == 0:
                # Pressure is zero - check if we've been at zero for 10 seconds
                if LAUNDRY_ROUTINE_GUIDANCE_STATE["zero_value_start_time"] is None:
                    # First time seeing zero - start timer
                    LAUNDRY_ROUTINE_GUIDANCE_STATE["zero_value_start_time"] = time.time()
                else:
                    # Check if we've been at zero for 10 seconds
                    elapsed_zero_time = time.time() - LAUNDRY_ROUTINE_GUIDANCE_STATE["zero_value_start_time"]
                    if elapsed_zero_time >= 25.0 and not LAUNDRY_ROUTINE_GUIDANCE_STATE["completion_detected"]:
                        # Cycle complete! Send notification
                        LAUNDRY_ROUTINE_GUIDANCE_STATE["completion_detected"] = True
                        message = "Your laundry load is done!"
                        if AUDIO_AVAILABLE and speak_text:
                            speak_text(message)
                        else:
                            print(f"[LAUNDRY] {message}")
                        
                        # Send notification event to API
                        if EVENT_LOGGING_AVAILABLE and log_event:
                            log_event(
                                event_type="laundry_cycle_complete",
                                message="Laundry cycle completed - load is ready",
                                room="laundry",
                                severity="info",
                                metadata={"routine_id": LAUNDRY_ROUTINE_GUIDANCE_STATE["routine_id"]}
                            )
                        
                        # Send notification to frontend via API
                        if REQUESTS_AVAILABLE:
                            try:
                                requests.post(
                                    f"{API_BASE_URL}/events/internal",
                                    json={
                                        "event_type": "laundry_cycle_complete",
                                        "message": "Your laundry load is done!",
                                        "room": "laundry",
                                        "severity": "info",
                                        "metadata": {
                                            "routine_id": LAUNDRY_ROUTINE_GUIDANCE_STATE["routine_id"],
                                            "routine_name": LAUNDRY_ROUTINE_GUIDANCE_STATE["routine_name"]
                                        }
                                    },
                                    timeout=1.0
                                )
                            except:
                                pass  # Fail silently if API unavailable
                        
                        # Deactivate monitoring mode and mark completion
                        LAUNDRY_ROUTINE_GUIDANCE_STATE["monitoring_mode"] = False
                        LAUNDRY_ROUTINE_GUIDANCE_STATE["active"] = False
                        # Set completion_detected flag to prevent any further pressure sensor processing
                        LAUNDRY_ROUTINE_GUIDANCE_STATE["completion_detected"] = True
                        print("[LAUNDRY] Cycle completion detected - pressure sensor will no longer trigger messages")
            else:
                # Pressure is non-zero (washing machine still vibrating) - reset timer
                LAUNDRY_ROUTINE_GUIDANCE_STATE["zero_value_start_time"] = None
        except Exception as e:
            # Error reading pressure sensor - continue silently
            pass
        return  # Exit early when in monitoring mode
    
    # Normal routine guidance mode (before last step)
    # Announce routine name if not yet announced
    if not LAUNDRY_ROUTINE_GUIDANCE_STATE["routine_name_announced"]:
        routine_name = LAUNDRY_ROUTINE_GUIDANCE_STATE["routine_name"]
        message = f"Starting laundry routine: {routine_name}"
        if AUDIO_AVAILABLE and speak_text:
            speak_text(message)
        else:
            print(f"[LAUNDRY] {message}")
        LAUNDRY_ROUTINE_GUIDANCE_STATE["routine_name_announced"] = True
        LAUNDRY_ROUTINE_GUIDANCE_STATE["first_step_announced"] = False
        # Update LEDs for routine start
        update_routine_leds(ports, 0, len(LAUNDRY_ROUTINE_GUIDANCE_STATE["steps"]), glow_port_laundry, laundry_step_fade)
        return  # Wait for next iteration to announce first step
    
    # Announce first step if routine name was just announced
    if not LAUNDRY_ROUTINE_GUIDANCE_STATE["first_step_announced"]:
        current_step = LAUNDRY_ROUTINE_GUIDANCE_STATE["current_step"]
        if current_step < len(LAUNDRY_ROUTINE_GUIDANCE_STATE["steps"]):
            step_text = LAUNDRY_ROUTINE_GUIDANCE_STATE["steps"][current_step]
            message = f"Step {current_step + 1}: {step_text}"
            if AUDIO_AVAILABLE and speak_text:
                speak_text(message)
            else:
                print(f"[LAUNDRY] {message}")
            LAUNDRY_ROUTINE_GUIDANCE_STATE["first_step_announced"] = True
            # Update LEDs for first step
            update_routine_leds(ports, current_step, len(LAUNDRY_ROUTINE_GUIDANCE_STATE["steps"]), glow_port_laundry, laundry_step_fade)
        return  # Wait for pressure sensor to advance to next step
    
    # Check pressure sensor for next step
    try:
        pressure_value = 0
        if hasattr(ports, 'modules') and ports.modules[force_port] is not None:
            module = ports.modules[force_port]
            if hasattr(module, 'data') and hasattr(module.data, 'strength'):
                pressure_value = int(module.data.strength)
            elif hasattr(module, 'strength'):
                pressure_value = int(module.strength)
            elif hasattr(module, 'data') and hasattr(module.data, 'amount'):
                pressure_value = int(module.data.amount)
            elif hasattr(module, 'amount'):
                pressure_value = int(module.amount())
        
        # Detect pressure sensor press (pressure > threshold and was previously low)
        # Note: completion_detected check at function start prevents this from running after completion
        last_pressure = LAUNDRY_ROUTINE_GUIDANCE_STATE["last_pressure_value"]
        threshold = LAUNDRY_ROUTINE_GUIDANCE_STATE["pressure_threshold"]
        
        if pressure_value > threshold and last_pressure <= threshold:
            # Pressure sensor pressed - advance to next step
            LAUNDRY_ROUTINE_GUIDANCE_STATE["current_step"] += 1
            current_step = LAUNDRY_ROUTINE_GUIDANCE_STATE["current_step"]
            
            # Update LEDs to show progress
            update_routine_leds(ports, current_step, len(LAUNDRY_ROUTINE_GUIDANCE_STATE["steps"]), glow_port_laundry, laundry_step_fade)
            
            if current_step < len(LAUNDRY_ROUTINE_GUIDANCE_STATE["steps"]):
                step_text = LAUNDRY_ROUTINE_GUIDANCE_STATE["steps"][current_step]
                message = f"Step {current_step + 1}: {step_text}"
                if AUDIO_AVAILABLE and speak_text:
                    speak_text(message)
                else:
                    print(f"[LAUNDRY] {message}")
            else:
                # Last step completed - switch to monitoring mode, keep LEDs on
                update_routine_leds(ports, current_step, len(LAUNDRY_ROUTINE_GUIDANCE_STATE["steps"]), glow_port_laundry, laundry_step_fade)
                # Get cycle duration from routine metadata if available
                routine_name = LAUNDRY_ROUTINE_GUIDANCE_STATE["routine_name"]
                # Try to get cycle duration from API response (stored in routine data)
                cycle_duration = 45  # Default
                if REQUESTS_AVAILABLE:
                    try:
                        response = requests.get(f"{API_BASE_URL}/laundry-routine-guidance/get-active", timeout=0.5)
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("status") == "success" and data.get("routine"):
                                cycle_duration = data["routine"].get("cycle_duration_minutes", 45)
                    except:
                        pass  # Use default if API call fails
                completion_message = f"All steps complete! The cycle will run for approximately {cycle_duration} minutes. I'll let you know when it's done."
                if AUDIO_AVAILABLE and speak_text:
                    speak_text(completion_message)
                else:
                    print(f"[LAUNDRY] {completion_message}")
                
                # Switch to monitoring mode
                LAUNDRY_ROUTINE_GUIDANCE_STATE["monitoring_mode"] = True
                LAUNDRY_ROUTINE_GUIDANCE_STATE["zero_value_start_time"] = None
                LAUNDRY_ROUTINE_GUIDANCE_STATE["completion_detected"] = False
                print("[LAUNDRY] Switched to monitoring mode - waiting for washing machine to stop vibrating")
        
        LAUNDRY_ROUTINE_GUIDANCE_STATE["last_pressure_value"] = pressure_value
    except Exception as e:
        # Error reading pressure sensor - continue silently
        pass


if __name__ == "__main__":
    # wired connection path for a Mac
    room = input("kitchen, bathroom, or laundry: ")
    with Magic.Hardware("/dev/cu.SLAB_USBtoUART") as h:
        # connect to hardware
        h.connect()
        if room == "kitchen":
            which_warning = 0
            proximity_warning_led = led_output(lambda :h.modules[glow_port_prox].out.setFade(*prox_warning_fade),lambda :h.modules[glow_port_prox].out.setBrightness(*prox_warning_fade[:2],255))
            decibel_warning_led = led_output(lambda :h.modules[glow_port_decibel].out.setFade(*decibel_warning_fade),lambda :h.modules[glow_port_decibel].out.setBrightness(*decibel_warning_fade[:2],255))
            heat_warning_led = led_output(lambda :h.modules[glow_port_heat].out.setFade(*heat_warning_fade),lambda :h.modules[glow_port_heat].out.setBrightness(*heat_warning_fade[:2],255))  
            while True:
                try:
                    # read module data
                    now = time.time()
                    while time.time() - now < .1:
                        try:
                            data = h.read()
                        except KeyboardInterrupt as e:
                            raise e
                        except:
                            print(".",end="",flush=True)
                            time.sleep(0.01)
                    #proximity_warning(h)
                    #h.modules[glow_port].out._send = print
                    which_warning = (which_warning + 1)%3
                    match which_warning:
                        case 0:
                            heat_warning(h,heat_warning_led, room="kitchen")
                        case 1:
                            decibel_detector(h,decibel_warning_led, room="kitchen")
                        case 2:
                            proximity_warning(h,proximity_warning_led, room="kitchen")
                    
                    # Handle recipe guidance (runs every iteration alongside warnings)
                    handle_recipe_guidance(h)
                    
                
                except KeyboardInterrupt:
                    # disconnect from hardware
                    h.disconnect()
                    exit()
        elif room == "bathroom":
            which_warning = 0
            decibel_warning_led = led_output(lambda :h.modules[glow_port_decibel].out.setFade(*decibel_warning_fade),lambda :h.modules[glow_port_decibel].out.setBrightness(*decibel_warning_fade[:2],255))
            heat_warning_led = led_output(lambda :h.modules[glow_port_heat].out.setFade(*heat_warning_fade),lambda :h.modules[glow_port_heat].out.setBrightness(*heat_warning_fade[:2],255))
            cold_water_warning_led = led_output(lambda :h.modules[glow_port_heat].out.setFade(*cold_water_warning_fade),lambda :h.modules[glow_port_heat].out.setBrightness(*cold_water_warning_fade[:2],255))
            
            # Load default routines for bathroom
            routines = load_default_routines()
            print(f"[BATHROOM] Loaded {len(routines)} routines: {', '.join(routines.keys())}")
            
            while True:
                try:
                    # read module data
                    now = time.time()
                    while time.time() - now < .1:
                        try:
                            data = h.read()
                        except KeyboardInterrupt as e:
                            raise e
                        except:
                            print(".",end="",flush=True)
                            time.sleep(0.01)
                    
                    # Rotate through warnings (water temperature and noise detection only)
                    which_warning = (which_warning + 1)%2
                    match which_warning:
                        case 0:
                            # Water temperature warning (using thermal sensor)
                            # Pass cold_water_warning_led for blue LED when cold water is detected
                            heat_warning(h, heat_warning_led, room="bathroom", temp_type="water", cold_warner=cold_water_warning_led)
                        case 1:
                            # Sound/noise level warning
                            decibel_detector(h, decibel_warning_led, room="bathroom")
                    
                    # Handle routine guidance (runs every iteration alongside warnings)
                    handle_routine_guidance(h)
                    
                
                except KeyboardInterrupt:
                    # disconnect from hardware
                    h.disconnect()
                    exit()
        elif room == "laundry":
            which_warning = 0
            proximity_warning_led = led_output(lambda :h.modules[glow_port_prox].out.setFade(*prox_warning_fade),lambda :h.modules[glow_port_prox].out.setBrightness(*prox_warning_fade[:2],255))
            decibel_warning_led = led_output(lambda :h.modules[glow_port_decibel].out.setFade(*decibel_warning_fade),lambda :h.modules[glow_port_decibel].out.setBrightness(*decibel_warning_fade[:2],255))
            
            print(f"[LAUNDRY] Laundry room initialized")
            print(f"[LAUNDRY] Proximity warnings enabled for loud objects (washing machine, dryer)")
            print(f"[LAUNDRY] Decibel warnings enabled for overall noise level")
            
            while True:
                try:
                    # read module data
                    now = time.time()
                    while time.time() - now < .1:
                        try:
                            data = h.read()
                        except KeyboardInterrupt as e:
                            raise e
                        except:
                            print(".",end="",flush=True)
                            time.sleep(0.01)
                    
                    # Rotate through warnings (proximity and decibel)
                    which_warning = (which_warning + 1) % 2
                    match which_warning:
                        case 0:
                            # Proximity warning for loud objects (washing machine, dryer)
                            proximity_warning(h, proximity_warning_led, room="laundry")
                        case 1:
                            # Sound/noise level warning
                            decibel_detector(h, decibel_warning_led, room="laundry")
                    
                    # Handle laundry routine guidance (runs every iteration alongside warnings)
                    handle_laundry_routine_guidance(h)
                    
                
                except KeyboardInterrupt:
                    # disconnect from hardware
                    h.disconnect()
                    exit()