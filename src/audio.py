"""
Audio functionality for alert sounds
"""
import numpy as np
import logging
from .config import SOUND_FREQUENCY, SOUND_DURATION

class AudioManager:
    """Handles sound playback for alerts."""
    
    def __init__(self):
        self.initialized = False
        self._pygame = None
        self.setup_pygame()
    
    def _get_pygame(self):
        """Import and cache pygame module."""
        if self._pygame is None:
            import pygame
            self._pygame = pygame
        return self._pygame
    
    def setup_pygame(self):
        """Initialize pygame for sound playback"""
        try:
            pygame = self._get_pygame()
            pygame.mixer.init()
            self.initialized = True
            logging.info("Audio system initialized")
        except Exception as e:
            logging.error(f"Failed to initialize audio: {e}")
            self.initialized = False
    
    def cleanup(self):
        """Clean up audio resources."""
        try:
            if self._pygame and self.initialized:
                self._pygame.mixer.quit()
            self.initialized = False
            logging.info("Audio system cleaned up")
        except Exception as e:
            logging.error(f"Error during audio cleanup: {e}")
    
    def play_alert_sound(self):
        """Play an alert sound"""
        if not self.initialized:
            print("\a")  # Fallback system beep
            return
        
        try:
            pygame = self._get_pygame()
            sample_rate = 44100
            
            t = np.linspace(0, SOUND_DURATION, int(sample_rate * SOUND_DURATION))
            wave = np.sin(2 * np.pi * SOUND_FREQUENCY * t)
            
            sound = (wave * 32767).astype(np.int16)
            stereo_sound = np.column_stack((sound, sound))
            
            sound_obj = pygame.sndarray.make_sound(stereo_sound)
            sound_obj.play(loops=2)
            
            logging.info("Alert sound played")
        except Exception as e:
            logging.error(f"Could not play sound: {e}")
            print("\a")  # Fallback system beep
