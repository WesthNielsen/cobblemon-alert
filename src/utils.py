"""
System utilities for cross-platform functionality
"""
import ctypes
import subprocess
import platform
import logging

# Windows execution state constants (Windows only)
if platform.system() == "Windows":
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002

def prevent_system_sleep():
    """Prevent system from going to sleep - cross-platform implementation."""
    system = platform.system()
    
    if system == "Windows":
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
            )
            logging.info("Windows sleep prevention enabled")
        except Exception as e:
            logging.warning(f"Could not prevent Windows sleep: {e}")
    
    elif system == "Darwin":  # macOS
        try:
            # Use caffeinate command on macOS
            subprocess.Popen(['caffeinate', '-d'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logging.info("macOS sleep prevention enabled via caffeinate")
        except Exception as e:
            logging.warning(f"Could not prevent macOS sleep: {e}")
    
    elif system == "Linux":
        try:
            # Try to use systemd-inhibit on Linux
            subprocess.Popen(['systemd-inhibit', '--what=idle', '--who=pokemon-radar', 
                            '--why=Pokemon monitoring', 'sleep', '999999'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logging.info("Linux sleep prevention enabled via systemd-inhibit")
        except Exception as e:
            logging.warning(f"Could not prevent Linux sleep: {e}")
    
    else:
        logging.warning(f"Sleep prevention not implemented for {system}")

def setup_logging():
    """Set up application logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pokemon_radar.log'),
            logging.StreamHandler()
        ]
    )
