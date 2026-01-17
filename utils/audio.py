"""
Audio utility for ElevenLabs text-to-speech integration.
Handles audio warnings and messages for HelpingHome.
"""

import os
from typing import Optional

try:
    from dotenv import load_dotenv
    from elevenlabs.client import ElevenLabs
    from elevenlabs import play as elevenlabs_play
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    elevenlabs_play = None


# Load environment variables
load_dotenv()


class AudioAgent:
    """
    ElevenLabs audio agent for text-to-speech warnings and messages.
    """
    
    def __init__(self, api_key: Optional[str] = None, voice_id: Optional[str] = None):
        """
        Initialize the ElevenLabs audio agent.
        
        Args:
            api_key: ElevenLabs API key. If not provided, will try to get from ELEVENLABS_API_KEY env variable.
            voice_id: Voice ID to use. If not provided, uses a default calm voice.
        """
        if not ELEVENLABS_AVAILABLE:
            raise ImportError(
                "ElevenLabs package is not installed. Install it with: pip install elevenlabs"
            )
        
        if api_key is None:
            api_key = os.getenv("ELEVENLABS_API_KEY")
        
        if not api_key:
            raise ValueError(
                "ElevenLabs API key is required. Set ELEVENLABS_API_KEY in .env file "
                "or pass api_key parameter."
            )
        
        self.client = ElevenLabs(api_key=api_key)
        # Default to a calm, clear voice (Rachel - professional and clear)
        self.voice_id = voice_id or "21m00Tcm4TlvDq8ikWAM"
        self.model_id = "eleven_multilingual_v2"  # Multilingual model
    
    def speak(self, text: str, voice_id: Optional[str] = None) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to convert to speech
            voice_id: Optional voice ID (uses default if not provided)
        
        Returns:
            True if successful, False otherwise
        """
        voice = voice_id or self.voice_id
        
        try:
            print(f"[DEBUG] Calling ElevenLabs API with text: {text[:50]}...")
            print(f"[DEBUG] Voice ID: {voice}, Model: {self.model_id}")
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice,
                model_id=self.model_id,
                output_format="mp3_44100_128"
            )
            print("[DEBUG] API call successful, audio received")
            print("[DEBUG] Playing audio...")
            # Play the audio directly (no file saved)
            elevenlabs_play.play(audio)
            print("[DEBUG] Audio playback completed")
            return True
            
        except Exception as e:
            print(f"Error generating speech: {e}")
            # Fallback to print if audio fails
            print(f"[Audio would say: {text}]")
            return False
    
    def speak_warning(self, text: str) -> bool:
        """
        Speak a warning message.
        
        Args:
            text: Warning message to speak
        
        Returns:
            True if successful, False otherwise
        """
        return self.speak(text, voice_id=self.voice_id)
    
    def speak_calm(self, text: str) -> bool:
        """
        Speak a calming message.
        
        Args:
            text: Calming message to speak
        
        Returns:
            True if successful, False otherwise
        """
        return self.speak(text, voice_id=self.voice_id)


# Global audio agent instance (initialized when needed)
_audio_agent: Optional[AudioAgent] = None


def get_audio_agent() -> Optional[AudioAgent]:
    """Get or create the global audio agent instance."""
    global _audio_agent
    
    if _audio_agent is None:
        try:
            print("[DEBUG] Initializing ElevenLabs audio agent...")
            api_key = os.getenv("ELEVENLABS_API_KEY")
            if api_key:
                print(f"[DEBUG] API key found: {api_key[:10]}...{api_key[-4:]}")
            else:
                print("[DEBUG] ERROR: No API key found in environment")
            _audio_agent = AudioAgent()
            print("[DEBUG] Audio agent initialized successfully")
        except (ImportError, ValueError) as e:
            print(f"[DEBUG] Could not initialize audio agent: {e}")
            return None
    
    return _audio_agent


def speak_text(text: str) -> bool:
    """
    Convenience function to speak text using the global audio agent.
    
    Args:
        text: Text to speak
    
    Returns:
        True if successful, False otherwise
    """
    print(f"[DEBUG] speak_text called with: {text[:50]}...")
    agent = get_audio_agent()
    if agent:
        print("[DEBUG] Audio agent found, calling speak()...")
        try:
            result = agent.speak(text)
            print(f"[DEBUG] speak() returned: {result}")
            return result
        except Exception as e:
            print(f"[DEBUG] Error speaking text: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        print("[DEBUG] No audio agent available")
    return False

