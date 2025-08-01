"""
Configuration classes and constants for Pokemon Radar Alert
"""
from dataclasses import dataclass
import platform

# Application constants
DEFAULT_MONITOR_X = 1535
DEFAULT_MONITOR_Y = 730
DEFAULT_MONITOR_SIZE = 275
DEFAULT_WHITE_THRESHOLD = 200
DEFAULT_BLUE_THRESHOLD = 60.0
DEFAULT_CHECK_INTERVAL = 0.5
MIN_CONSECUTIVE_DETECTIONS = 2
PREVIEW_SIZE = (150, 150)
BLACK_PIXEL_WARNING_THRESHOLD = 95
SOUND_FREQUENCY = 800
SOUND_DURATION = 0.02

@dataclass
class MonitorConfig:
    """Configuration for monitoring area and detection settings."""
    x: int = DEFAULT_MONITOR_X
    y: int = DEFAULT_MONITOR_Y
    width: int = DEFAULT_MONITOR_SIZE
    height: int = DEFAULT_MONITOR_SIZE
    white_threshold: int = DEFAULT_WHITE_THRESHOLD
    blue_threshold: float = DEFAULT_BLUE_THRESHOLD
    check_interval: float = DEFAULT_CHECK_INTERVAL

def get_default_coordinates():
    """Get platform-appropriate default coordinates."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        # macOS typically has menu bar at top, dock at bottom
        return {
            "x": 100,
            "y": 100,  # Account for menu bar
            "width": DEFAULT_MONITOR_SIZE,
            "height": DEFAULT_MONITOR_SIZE
        }
    elif system == "Linux":
        # Linux varies by desktop environment
        return {
            "x": 100,
            "y": 50,   # Account for potential top panel
            "width": DEFAULT_MONITOR_SIZE,
            "height": DEFAULT_MONITOR_SIZE
        }
    else:  # Windows or other
        return {
            "x": DEFAULT_MONITOR_X,
            "y": DEFAULT_MONITOR_Y,
            "width": DEFAULT_MONITOR_SIZE,
            "height": DEFAULT_MONITOR_SIZE
        }
