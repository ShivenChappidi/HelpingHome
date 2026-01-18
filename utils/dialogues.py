"""
Dialogue variations for HelpingHome voice messages.
Provides multiple soothing variations for each message type to add variety.
"""

import random
from typing import List


# Dialogue variations for different scenarios
DIALOGUES = {
    "proximity_warning": [
        "This item could get loud",
        "Please be careful, this might make some noise",
        "Heads up, this could be a bit noisy",
        "Just letting you know, this may get loud",
        "Something to keep in mind - this could get noisy",
        "Fair warning - this might get a bit loud",
        "You might want to prepare for some noise from this",
        "This device can get pretty loud, just so you know",
    ],
    
    "heat_warning_critical": [
        "It's not safe to touch the stove",
        "The stove is too hot to touch right now",
        "Please be careful, the stove is very hot",
        "The stove is too hot, please wait before touching it",
        "It's unsafe to touch the stove at this temperature",
        "The stove is extremely hot - do not touch",
        "Please stay away from the stove, it's dangerously hot",
        "The stove surface is too hot to touch safely",
    ],
    
    "heat_warning_warming": [
        "The stove is getting too hot, turn it off",
        "The stove is heating up too much, please turn it off",
        "You might want to turn down the stove, it's getting quite hot",
        "The stove temperature is rising, consider turning it off",
        "The stove is getting warmer than it should be",
        "The stove needs to be turned down, it's getting too hot",
        "Please reduce the heat on the stove",
        "The stove is heating up more than necessary",
    ],
    
    "water_heat_warning_critical": [
        "Warning. The water is very hot. Please be careful.",
        "The water temperature is too hot, please be careful",
        "Please be careful, the water is very hot",
        "The water is too hot right now, please wait",
        "It's unsafe to touch the water at this temperature",
        "The water is dangerously hot - please wait",
        "Be very careful, the water is extremely hot",
        "The water temperature is unsafe right now",
    ],
    
    "water_heat_warning_warming": [
        "The water is getting too hot, turn it off",
        "The water is heating up too much, please turn it off",
        "You might want to turn down the water, it's getting quite hot",
        "The water temperature is rising, consider turning it off",
        "The water is getting warmer than it should be",
        "Please reduce the water temperature, it's getting too hot",
        "The water is heating up more than needed",
        "You should turn down the hot water",
    ],
    
    "cold_water_warning": [
        "The water is a little cold",
        "The water temperature is a bit cold",
        "The water feels cold",
        "The water is on the cold side",
        "The water is colder than usual",
        "The water temperature is a bit low",
        "The water seems colder than expected",
        "Just a heads up, the water is on the cool side",
    ],
    
    "volume_warning": [
        "Sounds like the volume is getting too high",
        "The volume seems a bit loud",
        "You might want to lower the volume a bit",
        "The sound level is getting quite high",
        "The volume could be turned down a little",
        "The noise level is getting high",
        "It might be a good time to turn down the volume",
        "The sound is getting a bit too loud",
    ],
    
    "sound_warning": [
        "Warning. Loud noise detected. Please prepare for the sound.",
        "A loud sound has been detected. Get ready.",
        "Heads up - loud noise detected. Please prepare yourself.",
        "There's a loud noise coming. Please be prepared.",
        "A loud sound is happening. You might want to prepare.",
        "Loud noise detected - please prepare for the sound.",
        "A loud noise is occurring. Please get ready.",
    ],
    
    "sound_critical": [
        "Critical alert. Very loud noise detected. Cutting power to appliance.",
        "Very loud noise detected. Turning off the appliance for safety.",
        "Extremely loud noise - cutting power to protect you.",
        "The noise is too loud. Shutting off the appliance now.",
        "Critical: Very loud noise. Disabling the device.",
    ],
    
    "light_warning": [
        "Warning. Harsh lighting detected. Consider dimming the lights or moving to a softer area.",
        "The lighting is quite bright. You might want to dim it or find a softer spot.",
        "The lights are pretty harsh. Consider dimming them or moving somewhere softer.",
        "Harsh lighting detected. Perhaps dim the lights or go to a gentler area.",
        "The lighting is very bright. Consider reducing it or moving to a calmer space.",
        "Harsh lights detected. You may want to dim them or find a softer location.",
    ],
    
    "fire_hazard_reminder": [
        "Fire hazard alert. The stove has been above {temp} degrees for over a minute with no movement detected. Please turn off the stove to avoid a fire.",
        "Important: The stove has been very hot for over a minute with no one nearby. Please turn it off to prevent a fire.",
        "Safety reminder: The stove is extremely hot and has been unattended. Please turn it off now.",
        "Fire safety alert: The stove is dangerously hot with no movement detected. Turn it off immediately.",
        "The stove needs attention - it's been very hot for over a minute with no activity. Please turn it off.",
    ],
    
    "safety_alert": [
        "Safety alert. Stove is hot at {temp} degrees. No motion detected for {minutes} minutes. Please return to the kitchen.",
        "Important: The stove is hot and no one has been in the kitchen for {minutes} minutes. Please come back.",
        "Safety reminder: The stove is hot and unattended for {minutes} minutes. Please return to check on it.",
        "The stove is hot at {temp} degrees and no movement has been detected. Please return to the kitchen.",
        "Alert: The stove needs attention - it's hot and no one has been near it for a while.",
    ],
    
    "stove_hot_warning": [
        "Warning. Stove is hot at {temp} degrees. Please monitor carefully.",
        "The stove is hot right now. Please keep an eye on it.",
        "Just a reminder - the stove is hot. Please watch it carefully.",
        "The stove temperature is high. Please monitor it.",
        "The stove is hot. Make sure to keep an eye on it.",
    ],
    
    "recipe_loaded": [
        "Recipe loaded: {name}. {steps} steps.",
        "Great! I've loaded {name} for you. There are {steps} steps to follow.",
        "Recipe {name} is ready. You have {steps} steps to complete.",
        "{name} recipe is now loaded. There are {steps} steps in this recipe.",
        "I've loaded the {name} recipe. It has {steps} steps.",
    ],
    
    "recipe_step_complete": [
        "Step {step} complete. Next step: {next}.",
        "Well done! Step {step} is done. Now, {next}.",
        "Great job completing step {step}! Next up: {next}.",
        "Step {step} finished. Moving on to: {next}.",
        "You've finished step {step}! The next step is: {next}.",
    ],
    
    "recipe_complete": [
        "Recipe complete. Great job! {name} is ready.",
        "Congratulations! You've finished the {name} recipe. It's ready to enjoy!",
        "Well done! The {name} is complete and ready.",
        "Excellent work! You've completed {name}. It's all done!",
        "Fantastic! The {name} recipe is finished and ready to serve.",
    ],
    
    "recipe_reset": [
        "Recipe reset. Starting {name} from the beginning.",
        "I've reset the recipe. We're starting {name} over from step one.",
        "Recipe reset. Beginning {name} again from the start.",
        "Starting fresh with {name}. Beginning from the first step.",
        "Resetting to the beginning of {name}.",
    ],
    
    "timer_complete": [
        "Timer complete.",
        "Your timer is finished!",
        "The timer has ended.",
        "Time's up!",
        "Your timer is done.",
    ],
    
    "laundry_cycle_loaded": [
        "Cycle type loaded: {name}. Expected time: {minutes} minutes. Detergent amount: {detergent}.",
        "I've loaded {name} cycle for you. It should take about {minutes} minutes. Use {detergent} detergent.",
        "{name} cycle is ready. Expect it to take around {minutes} minutes with {detergent} detergent.",
        "The {name} cycle is loaded. It will run for approximately {minutes} minutes. Use {detergent} detergent.",
        "{name} wash cycle is set. It typically takes {minutes} minutes and requires {detergent} detergent.",
    ],
    
    "laundry_started": [
        "Laundry started. Expected time: {minutes} minutes.",
        "The laundry cycle has begun. It should take about {minutes} minutes.",
        "Washing has started! Expect it to finish in around {minutes} minutes.",
        "The wash cycle is running. It's expected to take {minutes} minutes.",
        "Laundry cycle started. Estimated completion time: {minutes} minutes.",
    ],
    
    "laundry_almost_done": [
        "Laundry is almost done.",
        "Your laundry is nearly finished.",
        "The wash cycle is almost complete.",
        "The laundry should be done soon.",
        "Your clothes are almost ready.",
    ],
    
    "laundry_complete": [
        "Laundry is done when you're ready.",
        "Your laundry cycle is complete!",
        "The washing is finished.",
        "Your clothes are ready.",
        "Laundry cycle complete. You can empty the washer now.",
    ],
    
    "laundry_door_opened": [
        "Door opened. Cycle complete.",
        "The door is open. Cycle finished.",
        "Door has been opened. The cycle is complete.",
        "Cycle complete. The door is open.",
    ],
    
    "laundry_false_positive": [
        "It looks like that start was accidental. I stopped tracking this cycle.",
        "That start seemed accidental. I've stopped monitoring this cycle.",
        "It appears the cycle didn't actually start. I've stopped tracking it.",
        "That looked like a false start. I've cancelled the cycle tracking.",
    ],
    
    "laundry_overrun_motion": [
        "Motion is still detected, but the cycle should be finished by now.",
        "The cycle should be done, but motion is still happening.",
        "Motion continues, though the cycle should have completed.",
        "The wash should be finished, but movement is still being detected.",
    ],
    
    "laundry_reminder_stage2": [
        "Reminder. Clothes may still be in the washer.",
        "Just a reminder - your clothes might still be in the washer.",
        "Reminder: Don't forget about the clothes in the washer.",
        "A quick reminder: Your laundry is still in the washer.",
    ],
    
    "laundry_reminder_stage3": [
        "Please empty the washer and move to the dryer to avoid mold growth. Stopping further reminders.",
        "It's important to move your clothes to the dryer now. I won't remind you again.",
        "Please transfer your clothes to prevent mold. This is my last reminder.",
        "For best results, empty the washer now. This is the final reminder.",
    ],
    
    "pause_button_activated": [
        "De-escalation mode activated. Taking a break. Environment is now calmer. Playing {song}.",
        "Pause mode on. We're taking a moment to calm things down. Playing {song}.",
        "Activating calm mode. Everything is settling down. Enjoying {song}.",
        "Break time activated. Creating a peaceful space. Let's listen to {song}.",
    ],
    
    "routine_step": [
        # These will be dynamically set but can have variations if needed
    ],
}


def get_dialogue(message_type: str, default_text: str = None, **kwargs) -> str:
    """
    Get a random dialogue variation for a given message type.
    Supports format string replacement with keyword arguments.
    
    Args:
        message_type: The type of message (e.g., "proximity_warning")
        default_text: Fallback text if message_type not found
        **kwargs: Format string arguments (e.g., name="Scrambled Eggs", temp=300)
    
    Returns:
        A randomly selected dialogue variation (formatted if kwargs provided)
    """
    if message_type in DIALOGUES and DIALOGUES[message_type]:
        dialogue = random.choice(DIALOGUES[message_type])
        # Format with kwargs if provided
        try:
            if kwargs:
                return dialogue.format(**kwargs)
            return dialogue
        except (KeyError, ValueError):
            # If formatting fails, return unformatted dialogue
            return dialogue
    
    # If no variations found, return default or the message_type as fallback
    if default_text:
        try:
            if kwargs:
                return default_text.format(**kwargs)
            return default_text
        except (KeyError, ValueError):
            return default_text
    
    return message_type


def add_dialogue_variations(message_type: str, variations: List[str]):
    """
    Add or update dialogue variations for a message type.
    
    Args:
        message_type: The type of message
        variations: List of dialogue variations
    """
    DIALOGUES[message_type] = variations

