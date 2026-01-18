# Opennote API client for HelpingHome
# Handles integration with Opennote for note-taking, journals, and other features

import os
import sys
from typing import Optional

# Workaround: Import from installed package, not local directory
# The local opennote/ directory shadows the installed package, so we clear cache and remove from path
path_to_remove = None
try:
    # Clear any cached opennote module
    if 'opennote' in sys.modules:
        del sys.modules['opennote']
    
    # Save current directory from path and remove it
    current_dir = os.getcwd()
    if current_dir in sys.path:
        path_to_remove = current_dir
        sys.path.remove(current_dir)
    
    # Also remove script directory if it's different
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    if project_root in sys.path:
        sys.path.remove(project_root)
    
    # Now import from installed package
    from opennote import OpennoteClient
    
except ImportError:
    OpennoteClient = None
finally:
    # Restore paths if we removed them
    if path_to_remove:
        sys.path.insert(0, path_to_remove)
    if project_root in sys.path or project_root not in [p for p in sys.path]:
        try:
            sys.path.insert(0, project_root)
        except:
            pass


class OpenNoteService:
    """
    Service class for interacting with Opennote API.
    
    This class handles authentication, journal creation, and other Opennote features
    that can assist users with autism in their daily routines.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Opennote service.
        
        Args:
            api_key: Opennote API key. If not provided, will try to get from OPENNOTE_API_KEY env variable.
        
        Raises:
            ValueError: If API key is not provided or Opennote package is not installed.
        """
        if OpennoteClient is None:
            raise ImportError(
                "Opennote package is not installed. Install it with: pip install opennote"
            )
        
        if api_key is None:
            api_key = os.getenv("OPENNOTE_API_KEY")
        
        if not api_key:
            raise ValueError(
                "Opennote API key is required. Set OPENNOTE_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.client = OpennoteClient(api_key=api_key)
    
    # Add your Opennote methods here
    # Example structure for journal methods:
    # def create_journal(self, title: str):
    #     """Create a new journal in Opennote."""
    #     pass
    # 
    # def get_journal(self, journal_id: str):
    #     """Retrieve a journal by ID."""
    #     pass

