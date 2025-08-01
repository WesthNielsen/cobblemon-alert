"""
Screenshot and monitoring functionality
"""
import numpy as np
import cv2
from PIL import Image
import logging
from .config import BLACK_PIXEL_WARNING_THRESHOLD

# Color detection ranges
BLUE_LOWER = np.array([0, 70, 75])
BLUE_UPPER = np.array([15, 155, 155])

class ScreenMonitor:
    """Handles screen capture and image analysis."""
    
    def __init__(self):
        # Import MSS only when needed
        self._mss = None
        # Use thread-local storage to ensure each thread gets its own MSS instance
        import threading
        self._thread_local = threading.local()
    
    def _get_mss(self):
        """Import and cache MSS module."""
        if self._mss is None:
            import mss
            self._mss = mss
        return self._mss
    
    def get_mss_instance(self):
        """Get or create MSS instance for screenshots (thread-safe)."""
        # Check if current thread has an MSS instance
        if not hasattr(self._thread_local, 'mss_instance') or self._thread_local.mss_instance is None:
            mss = self._get_mss()
            self._thread_local.mss_instance = mss.mss()
        return self._thread_local.mss_instance
    
    def cleanup(self):
        """Clean up MSS resources for current thread."""
        if hasattr(self._thread_local, 'mss_instance') and self._thread_local.mss_instance:
            self._thread_local.mss_instance.close()
            self._thread_local.mss_instance = None
    
    def take_screenshot(self, x, y, width, height):
        """Take screenshot using MSS for better multi-monitor support"""
        try:
            sct = self.get_mss_instance()
            monitor = {"top": y, "left": x, "width": width, "height": height}
            screenshot = sct.grab(monitor)
            return Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        except Exception as e:
            logging.error(f"MSS screenshot failed: {e}")
            return Image.new("RGB", (width, height), (0, 0, 0))
    
    def get_screen_size(self):
        """Get the total screen size across all monitors using MSS"""
        try:
            sct = self.get_mss_instance()
            monitors = sct.monitors
            if len(monitors) > 1:
                virtual_monitor = monitors[0]
                return virtual_monitor["width"], virtual_monitor["height"]
            else:
                primary = monitors[1] if len(monitors) > 1 else monitors[0]
                return primary["width"], primary["height"]
        except Exception as e:
            logging.error(f"Could not get screen size: {e}")
            return 1920, 1080
    
    def get_monitor_info(self):
        """Get detailed monitor information."""
        try:
            sct = self.get_mss_instance()
            monitors = sct.monitors
            info = f"Detected {len(monitors)} monitors:\n"
            for i, monitor in enumerate(monitors):
                if i == 0:
                    info += f"  Virtual Screen: {monitor}\n"
                else:
                    info += f"  Monitor {i}: {monitor}\n"
            return info
        except Exception as e:
            return f"Could not get detailed monitor info: {e}\n"
    
    def detect_white_pixels(self, image: Image.Image, threshold: int) -> float:
        """Detect white pixels in the image"""
        try:
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            white_pixels = np.count_nonzero(gray >= threshold)
            total_pixels = gray.size
            
            return (white_pixels / total_pixels) * 100
        except Exception as e:
            logging.error(f"Error detecting white pixels: {e}")
            return 0.0
    
    def detect_blue_pixels(self, image: Image.Image) -> float:
        """Detect blue pixels in the image"""
        try:
            img_array = np.array(image)
            
            blue_mask = cv2.inRange(img_array, BLUE_LOWER, BLUE_UPPER)
            blue_pixels = np.count_nonzero(blue_mask)
            total_pixels = img_array.shape[0] * img_array.shape[1]
            
            return (blue_pixels / total_pixels) * 100
        except Exception as e:
            logging.error(f"Error detecting blue pixels: {e}")
            return 0.0
    
    def analyze_screenshot_quality(self, image: Image.Image) -> tuple[bool, float]:
        """Analyze if screenshot appears valid (not mostly black)."""
        try:
            img_array = np.array(image)
            black_pixels = np.sum(np.all(img_array < 10, axis=2))
            total_pixels = img_array.shape[0] * img_array.shape[1]
            black_percentage = (black_pixels / total_pixels) * 100
            
            is_valid = black_percentage <= BLACK_PIXEL_WARNING_THRESHOLD
            return is_valid, black_percentage
        except Exception as e:
            logging.error(f"Error analyzing screenshot quality: {e}")
            return False, 100.0
