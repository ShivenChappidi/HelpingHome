# Opennote API client for HelpingHome
# Handles integration with Opennote for note-taking, journals, and other features

import os
import sys
import importlib
from typing import Optional


def _load_opennote_client():
    """
    Load OpennoteClient from the external package, avoiding the local opennote module shadow.
    """
    try:
        from opennote import OpennoteClient  # type: ignore
        return OpennoteClient
    except Exception:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        removed = False
        if project_root in sys.path:
            sys.path.remove(project_root)
            removed = True
        try:
            module = importlib.import_module("opennote")
            return getattr(module, "OpennoteClient", None)
        finally:
            if removed:
                sys.path.insert(0, project_root)


OpennoteClient = _load_opennote_client()


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

