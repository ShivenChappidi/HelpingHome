"""
Routine storage utility for managing bathroom routines in a local JSON file.
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path

# Get project root directory
_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(_script_dir)
ROUTINES_FILE = os.path.join(project_root, 'data', 'routines.json')


def ensure_data_directory():
    """Ensure the data directory exists."""
    data_dir = os.path.dirname(ROUTINES_FILE)
    os.makedirs(data_dir, exist_ok=True)


def load_routines() -> Dict[str, Dict[str, any]]:
    """
    Load routines from the JSON file.
    
    Returns:
        Dictionary of routines (routine_id -> routine_data)
    """
    ensure_data_directory()
    
    if not os.path.exists(ROUTINES_FILE):
        # Return default routines if file doesn't exist
        default_routines = {
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
        # Save default routines to file
        save_routines(default_routines)
        return default_routines
    
    try:
        with open(ROUTINES_FILE, 'r', encoding='utf-8') as f:
            routines = json.load(f)
        return routines
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading routines: {e}")
        return {}


def save_routines(routines: Dict[str, Dict[str, any]]) -> bool:
    """
    Save routines to the JSON file.
    
    Args:
        routines: Dictionary of routines to save
        
    Returns:
        True if successful, False otherwise
    """
    ensure_data_directory()
    
    try:
        with open(ROUTINES_FILE, 'w', encoding='utf-8') as f:
            json.dump(routines, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error saving routines: {e}")
        return False


def get_all_routines() -> Dict[str, Dict[str, any]]:
    """
    Get all routines.
    
    Returns:
        Dictionary of all routines
    """
    return load_routines()


def get_routine(routine_id: str) -> Optional[Dict[str, any]]:
    """
    Get a specific routine by ID.
    
    Args:
        routine_id: Unique identifier for the routine
        
    Returns:
        Routine data if found, None otherwise
    """
    routines = load_routines()
    return routines.get(routine_id)


def add_routine(routine_id: str, name: str, steps: List[str], description: str = "") -> Dict[str, any]:
    """
    Add a new routine to storage.
    
    Args:
        routine_id: Unique identifier for the routine
        name: Display name of the routine
        steps: List of step instructions
        description: Optional description of the routine
        
    Returns:
        Dictionary with routine info and status
    """
    routines = load_routines()
    
    # Validate inputs
    if not routine_id or not routine_id.strip():
        return {
            "status": "error",
            "message": "Routine ID cannot be empty"
        }
    
    if not name or not name.strip():
        return {
            "status": "error",
            "message": "Routine name cannot be empty"
        }
    
    if not steps or len(steps) == 0:
        return {
            "status": "error",
            "message": "Routine must have at least one step"
        }
    
    # Normalize routine_id (convert to lowercase, replace spaces with underscores)
    routine_id = routine_id.strip().lower().replace(' ', '_').replace('-', '_')
    
    routines[routine_id] = {
        "name": name.strip(),
        "steps": [step.strip() for step in steps if step.strip()],
        "description": description.strip() if description else ""
    }
    
    if save_routines(routines):
        return {
            "status": "success",
            "action": "routine_added",
            "routine_id": routine_id,
            "routine_name": name,
            "total_steps": len(steps)
        }
    else:
        return {
            "status": "error",
            "message": "Failed to save routine to file"
        }


def delete_routine(routine_id: str) -> Dict[str, any]:
    """
    Delete a routine by ID.
    
    Args:
        routine_id: Unique identifier for the routine
        
    Returns:
        Dictionary with status information
    """
    routines = load_routines()
    
    if routine_id not in routines:
        return {
            "status": "error",
            "message": f"Routine '{routine_id}' not found"
        }
    
    del routines[routine_id]
    
    if save_routines(routines):
        return {
            "status": "success",
            "action": "routine_deleted",
            "routine_id": routine_id
        }
    else:
        return {
            "status": "error",
            "message": "Failed to delete routine from file"
        }

