"""
Recipe storage utility for managing recipes in a local JSON file.
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path

# Get project root directory
_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(_script_dir)
RECIPES_FILE = os.path.join(project_root, 'data', 'recipes.json')


def ensure_data_directory():
    """Ensure the data directory exists."""
    data_dir = os.path.dirname(RECIPES_FILE)
    os.makedirs(data_dir, exist_ok=True)


def load_recipes() -> Dict[str, Dict[str, any]]:
    """
    Load recipes from the JSON file.
    
    Returns:
        Dictionary of recipes (recipe_id -> recipe_data)
    """
    ensure_data_directory()
    
    if not os.path.exists(RECIPES_FILE):
        # Return default recipes if file doesn't exist
        default_recipes = {
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
        # Save default recipes to file
        save_recipes(default_recipes)
        return default_recipes
    
    try:
        with open(RECIPES_FILE, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        return recipes
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading recipes: {e}")
        return {}


def save_recipes(recipes: Dict[str, Dict[str, any]]) -> bool:
    """
    Save recipes to the JSON file.
    
    Args:
        recipes: Dictionary of recipes to save
        
    Returns:
        True if successful, False otherwise
    """
    ensure_data_directory()
    
    try:
        with open(RECIPES_FILE, 'w', encoding='utf-8') as f:
            json.dump(recipes, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error saving recipes: {e}")
        return False


def get_all_recipes() -> Dict[str, Dict[str, any]]:
    """
    Get all recipes.
    
    Returns:
        Dictionary of all recipes
    """
    return load_recipes()


def get_recipe(recipe_id: str) -> Optional[Dict[str, any]]:
    """
    Get a specific recipe by ID.
    
    Args:
        recipe_id: Unique identifier for the recipe
        
    Returns:
        Recipe data if found, None otherwise
    """
    recipes = load_recipes()
    return recipes.get(recipe_id)


def add_recipe(recipe_id: str, name: str, steps: List[str], description: str = "") -> Dict[str, any]:
    """
    Add a new recipe to storage.
    
    Args:
        recipe_id: Unique identifier for the recipe
        name: Display name of the recipe
        steps: List of step instructions
        description: Optional description of the recipe
        
    Returns:
        Dictionary with recipe info and status
    """
    recipes = load_recipes()
    
    # Validate inputs
    if not recipe_id or not recipe_id.strip():
        return {
            "status": "error",
            "message": "Recipe ID cannot be empty"
        }
    
    if not name or not name.strip():
        return {
            "status": "error",
            "message": "Recipe name cannot be empty"
        }
    
    if not steps or len(steps) == 0:
        return {
            "status": "error",
            "message": "Recipe must have at least one step"
        }
    
    # Normalize recipe_id (convert to lowercase, replace spaces with underscores)
    recipe_id = recipe_id.strip().lower().replace(' ', '_').replace('-', '_')
    
    recipes[recipe_id] = {
        "name": name.strip(),
        "steps": [step.strip() for step in steps if step.strip()],
        "description": description.strip() if description else ""
    }
    
    if save_recipes(recipes):
        return {
            "status": "success",
            "action": "recipe_added",
            "recipe_id": recipe_id,
            "recipe_name": name,
            "total_steps": len(steps)
        }
    else:
        return {
            "status": "error",
            "message": "Failed to save recipe to file"
        }


def delete_recipe(recipe_id: str) -> Dict[str, any]:
    """
    Delete a recipe by ID.
    
    Args:
        recipe_id: Unique identifier for the recipe
        
    Returns:
        Dictionary with status information
    """
    recipes = load_recipes()
    
    if recipe_id not in recipes:
        return {
            "status": "error",
            "message": f"Recipe '{recipe_id}' not found"
        }
    
    del recipes[recipe_id]
    
    if save_recipes(recipes):
        return {
            "status": "success",
            "action": "recipe_deleted",
            "recipe_id": recipe_id
        }
    else:
        return {
            "status": "error",
            "message": "Failed to delete recipe from file"
        }

