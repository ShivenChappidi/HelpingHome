"""
Event logging system for tracking kitchen activity monitor events.
Stores events in memory and provides API for querying recent events.
Can also send events to API server via HTTP if API_URL is set.
"""

import time
import os
from typing import List, Dict, Optional
from collections import deque
from threading import Lock

# Global event storage (in-memory, can be replaced with database later)
_events: deque = deque(maxlen=100)  # Keep last 100 events
_event_lock = Lock()

# API server URL (set via environment variable or default)
API_URL = os.getenv('EVENT_API_URL', 'http://localhost:5001/api/events/internal')


def log_event(event_type: str, message: str, room: str = "kitchen", severity: str = "info", metadata: Optional[Dict] = None):
    """
    Log an event to the activity monitor.
    
    Args:
        event_type: Type of event (e.g., "proximity_warning", "heat_warning", "decibel_warning")
        message: Human-readable message describing the event
        room: Room where event occurred (default: "kitchen")
        severity: Event severity ("info", "warning", "critical")
        metadata: Optional additional data (e.g., temperature, distance, volume)
    """
    event = {
        "id": int(time.time() * 1000),  # Timestamp in milliseconds as ID
        "timestamp": time.time(),
        "event_type": event_type,
        "message": message,
        "room": room,
        "severity": severity,
        "metadata": metadata or {}
    }
    
    with _event_lock:
        _events.append(event)
        event_count = len(_events)
    
    print(f"[EVENT LOGGED] {event_type}: {message} (Total events in memory: {event_count})")
    
    # Also send to API server if running in separate process (ifmagic_trial.py)
    # Only send if this is being called from ifmagic_trial.py (not from API server itself)
    try:
        import urllib.request
        import json
        import inspect
        # Check if we're being called from api_server.py to avoid duplicate storage
        call_stack = [frame.filename for frame in inspect.stack()]
        if 'api_server.py' not in str(call_stack):
            req = urllib.request.Request(
                API_URL,
                data=json.dumps(event).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            urllib.request.urlopen(req, timeout=0.1)  # Non-blocking, short timeout
            print(f"[EVENT] Sent to API server: {event_type}")
    except Exception as e:
        # Silently fail if API server not available (it's optional)
        pass


def get_recent_events(room: Optional[str] = None, limit: int = 20) -> List[Dict]:
    """
    Get recent events from the activity monitor.
    
    Args:
        room: Optional room filter (e.g., "kitchen", "bathroom")
        limit: Maximum number of events to return (default: 20)
        
    Returns:
        List of event dictionaries, sorted by timestamp (newest first)
    """
    with _event_lock:
        events = list(_events)
    
    # Filter by room if specified
    if room:
        events = [e for e in events if e["room"].lower() == room.lower()]
    
    # Sort by timestamp (newest first)
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Limit results
    return events[:limit]


def clear_events():
    """Clear all stored events (for testing/debugging)."""
    with _event_lock:
        _events.clear()


def get_event_count() -> int:
    """Get total number of events currently stored."""
    with _event_lock:
        return len(_events)

