"""
Flask API server for serving kitchen activity monitor events to the frontend.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

# Add project root to path
_script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = _script_dir
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.event_logger import get_recent_events, get_event_count
from utils.recipe_storage import get_all_recipes, add_recipe, get_recipe
from utils.routine_storage import get_all_routines, add_routine, get_routine

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Global state for recipe guidance
RECIPE_GUIDANCE_ACTIVE = False
ACTIVE_RECIPE_ID = None
ACTIVE_RECIPE_DATA = None

# Global state for routine guidance (bathroom)
ROUTINE_GUIDANCE_ACTIVE = False
ACTIVE_ROUTINE_ID = None
ACTIVE_ROUTINE_DATA = None

# Global state for laundry routine guidance
LAUNDRY_ROUTINE_GUIDANCE_ACTIVE = False
ACTIVE_LAUNDRY_ROUTINE_ID = None
ACTIVE_LAUNDRY_ROUTINE_DATA = None

# Global state for voice preference
# Voice IDs for ElevenLabs:
# Australian Woman: "EXAVITQu4vr4xnSDxMaL" (Bella) - female, warm
# American Man: "pNInz6obpgDQGcFmaJgB" (Adam) - male, professional
# British Woman: "ThT5KcBeYPX3keUQqHPh" (Domi) - female, clear
VOICE_PREFERENCES = {
    "australian-woman": "EXAVITQu4vr4xnSDxMaL",  # Bella - warm, soothing
    "american-man": "pNInz6obpgDQGcFmaJgB",      # Adam - professional
    "british-woman": "ThT5KcBeYPX3keUQqHPh"      # Domi - clear, articulate
}
CURRENT_VOICE = "australian-woman"  # Default voice


@app.route('/api/events', methods=['GET'])
def get_events():
    """Get recent events from the activity monitor."""
    room = request.args.get('room', 'kitchen')  # Default to kitchen
    limit = int(request.args.get('limit', 20))  # Default to 20 events
    
    events = get_recent_events(room=room, limit=limit)
    
    return jsonify({
        "events": events,
        "count": len(events),
        "total_events": get_event_count()
    })


@app.route('/api/events/<room>', methods=['GET'])
def get_room_events(room):
    """Get recent events for a specific room (kitchen, bathroom, etc.)."""
    limit = int(request.args.get('limit', 20))
    events = get_recent_events(room=room, limit=limit)
    
    return jsonify({
        "events": events,
        "count": len(events)
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "helpinghome-api"})


@app.route('/api/test-opennote', methods=['GET'])
def test_opennote():
    """Test OpenNote API key and connection."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    api_key = os.getenv('OPENNOTE_API_KEY', '').strip()
    
    if not api_key:
        return jsonify({
            "status": "error",
            "message": "OPENNOTE_API_KEY not found in environment"
        }), 400
    
    try:
        from opennote.client import OpenNoteService
        service = OpenNoteService()
        client = service.client
        
        # Try to list journals (simple API call to test key)
        if hasattr(client, 'journals'):
            journals = client.journals.list()
            return jsonify({
                "status": "success",
                "message": "OpenNote API key is valid",
                "api_key_preview": f"{api_key[:10]}...{api_key[-4:]}",
                "journals_available": True
            })
        else:
            return jsonify({
                "status": "error",
                "message": "Client created but journals API not available"
            }), 500
            
    except ImportError as e:
        return jsonify({
            "status": "error",
            "message": f"Import error: {str(e)}",
            "hint": "Make sure opennote package is installed and API server is restarted"
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"API call failed: {str(e)}",
            "hint": "API key might be invalid or expired. Check your OpenNote account."
        }), 500


@app.route('/api/events/test', methods=['POST'])
def create_test_event():
    """Create a test event for debugging (optional: POST with JSON body)."""
    from utils.event_logger import log_event
    
    # Create a test event
    log_event(
        event_type="test_event",
        message="Test event: Activity monitor is working correctly",
        room="kitchen",
        severity="info",
        metadata={"test": True}
    )
    
    return jsonify({
        "status": "success",
        "message": "Test event created"
    })


@app.route('/api/events/internal', methods=['POST'])
def receive_event():
    """Receive events from external processes (like ifmagic_trial.py)."""
    from utils.event_logger import log_event
    
    try:
        event_data = request.get_json()
        if not event_data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Log the received event
        log_event(
            event_type=event_data.get('event_type', 'unknown'),
            message=event_data.get('message', ''),
            room=event_data.get('room', 'kitchen'),
            severity=event_data.get('severity', 'info'),
            metadata=event_data.get('metadata', {})
        )
        
        return jsonify({
            "status": "success",
            "message": "Event received and logged"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/daily-log/generate', methods=['POST'])
def generate_daily_log():
    """Generate a daily log from events in the last 24 hours and create it in OpenNote."""
    from utils.daily_log_generator import create_daily_log_from_events
    
    try:
        result = create_daily_log_from_events()
        
        if result["status"] == "success":
            return jsonify(result)
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error generating daily log: {str(e)}",
            "note_created": False
        }), 500


@app.route('/api/recipes', methods=['GET'])
def get_recipes():
    """Get all recipes."""
    try:
        recipes = get_all_recipes()
        return jsonify({
            "status": "success",
            "recipes": recipes,
            "count": len(recipes)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error loading recipes: {str(e)}"
        }), 500


@app.route('/api/recipes/<recipe_id>', methods=['GET'])
def get_recipe_by_id(recipe_id):
    """Get a specific recipe by ID."""
    try:
        recipe = get_recipe(recipe_id)
        if recipe:
            return jsonify({
                "status": "success",
                "recipe": recipe
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Recipe '{recipe_id}' not found"
            }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error loading recipe: {str(e)}"
        }), 500


@app.route('/api/recipes', methods=['POST'])
def create_recipe():
    """Add a new recipe."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        recipe_id = data.get('recipe_id', '')
        name = data.get('name', '')
        steps = data.get('steps', [])
        description = data.get('description', '')
        
        if not recipe_id:
            # Generate recipe_id from name if not provided
            recipe_id = name.lower().replace(' ', '_').replace('-', '_')
        
        result = add_recipe(recipe_id, name, steps, description)
        
        if result.get("status") == "success":
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error adding recipe: {str(e)}"
        }), 500


@app.route('/api/recipe-guidance/start', methods=['POST'])
def start_recipe_guidance():
    """Start recipe guidance mode."""
    global RECIPE_GUIDANCE_ACTIVE, ACTIVE_RECIPE_ID, ACTIVE_RECIPE_DATA
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        recipe_id = data.get('recipe_id', '')
        if not recipe_id:
            return jsonify({
                "status": "error",
                "message": "recipe_id is required"
            }), 400
        
        recipe = get_recipe(recipe_id)
        if not recipe:
            return jsonify({
                "status": "error",
                "message": f"Recipe '{recipe_id}' not found"
            }), 404
        
        RECIPE_GUIDANCE_ACTIVE = True
        ACTIVE_RECIPE_ID = recipe_id
        ACTIVE_RECIPE_DATA = recipe
        
        return jsonify({
            "status": "success",
            "message": "Recipe guidance started",
            "recipe_id": recipe_id,
            "recipe_name": recipe.get('name', recipe_id),
            "total_steps": len(recipe.get('steps', []))
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error starting recipe guidance: {str(e)}"
        }), 500


@app.route('/api/recipe-guidance/stop', methods=['POST'])
def stop_recipe_guidance():
    """Stop recipe guidance mode."""
    global RECIPE_GUIDANCE_ACTIVE, ACTIVE_RECIPE_ID, ACTIVE_RECIPE_DATA
    
    RECIPE_GUIDANCE_ACTIVE = False
    ACTIVE_RECIPE_ID = None
    ACTIVE_RECIPE_DATA = None
    
    return jsonify({
        "status": "success",
        "message": "Recipe guidance stopped"
    })


@app.route('/api/recipe-guidance/status', methods=['GET'])
def get_recipe_guidance_status():
    """Get current recipe guidance status."""
    global RECIPE_GUIDANCE_ACTIVE, ACTIVE_RECIPE_ID, ACTIVE_RECIPE_DATA
    
    if RECIPE_GUIDANCE_ACTIVE and ACTIVE_RECIPE_DATA:
        return jsonify({
            "status": "success",
            "active": True,
            "recipe_id": ACTIVE_RECIPE_ID,
            "recipe_name": ACTIVE_RECIPE_DATA.get('name', ACTIVE_RECIPE_ID),
            "total_steps": len(ACTIVE_RECIPE_DATA.get('steps', []))
        })
    else:
        return jsonify({
            "status": "success",
            "active": False
        })


@app.route('/api/recipe-guidance/get-active', methods=['GET'])
def get_active_recipe():
    """Get the currently active recipe (for ifmagic_trial.py to read)."""
    global RECIPE_GUIDANCE_ACTIVE, ACTIVE_RECIPE_ID, ACTIVE_RECIPE_DATA
    
    if RECIPE_GUIDANCE_ACTIVE and ACTIVE_RECIPE_DATA:
        return jsonify({
            "status": "success",
            "active": True,
            "recipe_id": ACTIVE_RECIPE_ID,
            "recipe": ACTIVE_RECIPE_DATA
        })
    else:
        return jsonify({
            "status": "success",
            "active": False,
            "recipe": None
        })


@app.route('/api/routines', methods=['GET'])
def get_routines():
    """Get all routines."""
    try:
        routines = get_all_routines()
        return jsonify({
            "status": "success",
            "routines": routines,
            "count": len(routines)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error loading routines: {str(e)}"
        }), 500


@app.route('/api/routines/<routine_id>', methods=['GET'])
def get_routine_by_id(routine_id):
    """Get a specific routine by ID."""
    try:
        routine = get_routine(routine_id)
        if routine:
            return jsonify({
                "status": "success",
                "routine": routine
            })
        else:
            return jsonify({
                "status": "error",
                "message": f"Routine '{routine_id}' not found"
            }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error loading routine: {str(e)}"
        }), 500


@app.route('/api/routines', methods=['POST'])
def create_routine():
    """Add a new routine."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        routine_id = data.get('routine_id', '')
        name = data.get('name', '')
        steps = data.get('steps', [])
        description = data.get('description', '')
        
        if not routine_id:
            # Generate routine_id from name if not provided
            routine_id = name.lower().replace(' ', '_').replace('-', '_')
        
        result = add_routine(routine_id, name, steps, description)
        
        if result.get("status") == "success":
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error adding routine: {str(e)}"
        }), 500


@app.route('/api/routine-guidance/start', methods=['POST'])
def start_routine_guidance():
    """Start routine guidance mode."""
    global ROUTINE_GUIDANCE_ACTIVE, ACTIVE_ROUTINE_ID, ACTIVE_ROUTINE_DATA
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        routine_id = data.get('routine_id', '')
        if not routine_id:
            return jsonify({
                "status": "error",
                "message": "routine_id is required"
            }), 400
        
        routine = get_routine(routine_id)
        if not routine:
            return jsonify({
                "status": "error",
                "message": f"Routine '{routine_id}' not found"
            }), 404
        
        ROUTINE_GUIDANCE_ACTIVE = True
        ACTIVE_ROUTINE_ID = routine_id
        ACTIVE_ROUTINE_DATA = routine
        
        return jsonify({
            "status": "success",
            "message": "Routine guidance started",
            "routine_id": routine_id,
            "routine_name": routine.get('name', routine_id),
            "total_steps": len(routine.get('steps', []))
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error starting routine guidance: {str(e)}"
        }), 500


@app.route('/api/routine-guidance/stop', methods=['POST'])
def stop_routine_guidance():
    """Stop routine guidance mode."""
    global ROUTINE_GUIDANCE_ACTIVE, ACTIVE_ROUTINE_ID, ACTIVE_ROUTINE_DATA
    
    ROUTINE_GUIDANCE_ACTIVE = False
    ACTIVE_ROUTINE_ID = None
    ACTIVE_ROUTINE_DATA = None
    
    return jsonify({
        "status": "success",
        "message": "Routine guidance stopped"
    })


@app.route('/api/routine-guidance/status', methods=['GET'])
def get_routine_guidance_status():
    """Get current routine guidance status."""
    global ROUTINE_GUIDANCE_ACTIVE, ACTIVE_ROUTINE_ID, ACTIVE_ROUTINE_DATA
    
    if ROUTINE_GUIDANCE_ACTIVE and ACTIVE_ROUTINE_DATA:
        return jsonify({
            "status": "success",
            "active": True,
            "routine_id": ACTIVE_ROUTINE_ID,
            "routine_name": ACTIVE_ROUTINE_DATA.get('name', ACTIVE_ROUTINE_ID),
            "total_steps": len(ACTIVE_ROUTINE_DATA.get('steps', []))
        })
    else:
        return jsonify({
            "status": "success",
            "active": False
        })


@app.route('/api/routine-guidance/get-active', methods=['GET'])
def get_active_routine():
    """Get the currently active routine (for ifmagic_trial.py to read)."""
    global ROUTINE_GUIDANCE_ACTIVE, ACTIVE_ROUTINE_ID, ACTIVE_ROUTINE_DATA
    
    if ROUTINE_GUIDANCE_ACTIVE and ACTIVE_ROUTINE_DATA:
        return jsonify({
            "status": "success",
            "active": True,
            "routine_id": ACTIVE_ROUTINE_ID,
            "routine": ACTIVE_ROUTINE_DATA
        })
    else:
        return jsonify({
            "status": "success",
            "active": False,
            "routine": None
        })


@app.route('/api/laundry-routine-guidance/start', methods=['POST'])
def start_laundry_routine_guidance():
    """Start laundry routine guidance mode."""
    global LAUNDRY_ROUTINE_GUIDANCE_ACTIVE, ACTIVE_LAUNDRY_ROUTINE_ID, ACTIVE_LAUNDRY_ROUTINE_DATA
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON data provided"
            }), 400
        
        routine_id = data.get('routine_id', '')
        if not routine_id:
            return jsonify({
                "status": "error",
                "message": "routine_id is required"
            }), 400
        
        routine = get_routine(routine_id)
        if not routine:
            return jsonify({
                "status": "error",
                "message": f"Routine '{routine_id}' not found"
            }), 404
        
        LAUNDRY_ROUTINE_GUIDANCE_ACTIVE = True
        ACTIVE_LAUNDRY_ROUTINE_ID = routine_id
        ACTIVE_LAUNDRY_ROUTINE_DATA = routine
        
        return jsonify({
            "status": "success",
            "message": "Laundry routine guidance started",
            "routine_id": routine_id,
            "routine_name": routine.get('name', routine_id),
            "total_steps": len(routine.get('steps', []))
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error starting laundry routine guidance: {str(e)}"
        }), 500


@app.route('/api/laundry-routine-guidance/stop', methods=['POST'])
def stop_laundry_routine_guidance():
    """Stop laundry routine guidance mode."""
    global LAUNDRY_ROUTINE_GUIDANCE_ACTIVE, ACTIVE_LAUNDRY_ROUTINE_ID, ACTIVE_LAUNDRY_ROUTINE_DATA
    
    LAUNDRY_ROUTINE_GUIDANCE_ACTIVE = False
    ACTIVE_LAUNDRY_ROUTINE_ID = None
    ACTIVE_LAUNDRY_ROUTINE_DATA = None
    
    return jsonify({
        "status": "success",
        "message": "Laundry routine guidance stopped"
    })


@app.route('/api/laundry-routine-guidance/status', methods=['GET'])
def get_laundry_routine_guidance_status():
    """Get current laundry routine guidance status."""
    global LAUNDRY_ROUTINE_GUIDANCE_ACTIVE, ACTIVE_LAUNDRY_ROUTINE_ID, ACTIVE_LAUNDRY_ROUTINE_DATA
    
    if LAUNDRY_ROUTINE_GUIDANCE_ACTIVE and ACTIVE_LAUNDRY_ROUTINE_DATA:
        return jsonify({
            "status": "success",
            "active": True,
            "routine_id": ACTIVE_LAUNDRY_ROUTINE_ID,
            "routine_name": ACTIVE_LAUNDRY_ROUTINE_DATA.get('name', ACTIVE_LAUNDRY_ROUTINE_ID),
            "total_steps": len(ACTIVE_LAUNDRY_ROUTINE_DATA.get('steps', []))
        })
    else:
        return jsonify({
            "status": "success",
            "active": False
        })


@app.route('/api/laundry-routine-guidance/get-active', methods=['GET'])
def get_active_laundry_routine():
    """Get the currently active laundry routine (for ifmagic_trial.py to read)."""
    global LAUNDRY_ROUTINE_GUIDANCE_ACTIVE, ACTIVE_LAUNDRY_ROUTINE_ID, ACTIVE_LAUNDRY_ROUTINE_DATA
    
    if LAUNDRY_ROUTINE_GUIDANCE_ACTIVE and ACTIVE_LAUNDRY_ROUTINE_DATA:
        return jsonify({
            "status": "success",
            "active": True,
            "routine_id": ACTIVE_LAUNDRY_ROUTINE_ID,
            "routine": ACTIVE_LAUNDRY_ROUTINE_DATA
        })
    else:
        return jsonify({
            "status": "success",
            "active": False,
            "routine": None
        })


@app.route('/api/voice-preference', methods=['GET'])
def get_voice_preference():
    """Get current voice preference."""
    global CURRENT_VOICE
    return jsonify({
        "status": "success",
        "voice": CURRENT_VOICE,
        "voice_id": VOICE_PREFERENCES.get(CURRENT_VOICE, VOICE_PREFERENCES["australian-woman"])
    })


@app.route('/api/voice-preference', methods=['POST'])
def set_voice_preference():
    """Set voice preference."""
    global CURRENT_VOICE
    data = request.get_json()
    
    if not data or 'voice' not in data:
        return jsonify({
            "status": "error",
            "message": "Voice preference is required"
        }), 400
    
    voice = data.get('voice')
    if voice not in VOICE_PREFERENCES:
        return jsonify({
            "status": "error",
            "message": f"Invalid voice preference. Must be one of: {', '.join(VOICE_PREFERENCES.keys())}"
        }), 400
    
    CURRENT_VOICE = voice
    voice_id = VOICE_PREFERENCES[voice]
    
    # Update audio utility with new voice
    try:
        from utils.audio import get_audio_agent
        audio_agent = get_audio_agent(voice_id=voice_id)
        if audio_agent:
            audio_agent.voice_id = voice_id
            print(f"[VOICE] Voice preference updated to: {voice} (voice_id: {voice_id})")
    except Exception as e:
        print(f"[VOICE] Warning: Could not update audio agent voice: {e}")
        import traceback
        traceback.print_exc()
    
    return jsonify({
        "status": "success",
        "voice": CURRENT_VOICE,
        "voice_id": voice_id,
        "message": f"Voice preference set to {voice}"
    })


if __name__ == '__main__':
    import os
    # Use port from environment variable or default to 5001 (5000 often used by AirPlay on macOS)
    port = int(os.getenv('API_PORT', 5001))
    
    print("Starting HelpingHome API server...")
    print("API endpoints:")
    print("  GET /api/events?room=kitchen&limit=20")
    print("  GET /api/events/kitchen?limit=20")
    print("  GET /api/health")
    print("  GET /api/test-opennote (test OpenNote API key)")
    print("  POST /api/daily-log/generate")
    print("  GET /api/recipes")
    print("  GET /api/recipes/<recipe_id>")
    print("  POST /api/recipes (add new recipe)")
    print("  POST /api/recipe-guidance/start (start recipe guidance)")
    print("  POST /api/recipe-guidance/stop (stop recipe guidance)")
    print("  GET /api/recipe-guidance/status (get guidance status)")
    print("  GET /api/recipe-guidance/get-active (get active recipe for hardware)")
    print("  GET /api/routines")
    print("  GET /api/routines/<routine_id>")
    print("  POST /api/routines (add new routine)")
    print("  POST /api/routine-guidance/start (start routine guidance)")
    print("  POST /api/routine-guidance/stop (stop routine guidance)")
    print("  GET /api/routine-guidance/status (get guidance status)")
    print("  GET /api/routine-guidance/get-active (get active routine for hardware)")
    print("  POST /api/laundry-routine-guidance/start (start laundry routine guidance)")
    print("  POST /api/laundry-routine-guidance/stop (stop laundry routine guidance)")
    print("  GET /api/laundry-routine-guidance/status (get laundry guidance status)")
    print("  GET /api/laundry-routine-guidance/get-active (get active laundry routine for hardware)")
    print(f"\nServer running on http://localhost:{port}")
    print(f"(Set API_PORT environment variable to use a different port)")
    app.run(host='0.0.0.0', port=port, debug=True)

