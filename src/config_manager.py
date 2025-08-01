"""
Configuration and preset management
"""
import json
import os
import logging
from .config import MonitorConfig

class ConfigManager:
    """Handles saving and loading of configuration and presets."""
    
    def __init__(self, presets_file="pokemon_radar_presets.json", config_file="pokemon_radar_config.json"):
        self.presets_file = presets_file
        self.config_file = config_file
        self.presets = self.load_presets()
    
    def load_presets(self):
        """Load presets from JSON file"""
        try:
            if os.path.exists(self.presets_file):
                with open(self.presets_file, 'r') as f:
                    return json.load(f)
            else:
                return {}
        except Exception as e:
            logging.error(f"Could not load presets: {e}")
            return {}
    
    def save_presets(self):
        """Save presets to JSON file"""
        try:
            with open(self.presets_file, 'w') as f:
                json.dump(self.presets, f, indent=2)
        except Exception as e:
            logging.error(f"Could not save presets: {e}")
            raise
    
    def add_preset(self, name: str, config: MonitorConfig):
        """Add a new preset."""
        self.presets[name] = {
            "x": config.x,
            "y": config.y,
            "width": config.width,
            "height": config.height,
            "white_threshold": config.white_threshold,
            "blue_threshold": config.blue_threshold,
            "check_interval": config.check_interval
        }
        self.save_presets()
    
    def get_preset(self, name: str) -> dict:
        """Get a preset by name."""
        return self.presets.get(name)
    
    def delete_preset(self, name: str):
        """Delete a preset."""
        if name in self.presets:
            del self.presets[name]
            self.save_presets()
    
    def get_preset_names(self) -> list:
        """Get list of all preset names."""
        return list(self.presets.keys())
    
    def save_config_to_file(self, config: MonitorConfig):
        """Save current configuration to file."""
        config_data = {
            "x": config.x,
            "y": config.y,
            "width": config.width,
            "height": config.height,
            "white_threshold": config.white_threshold,
            "blue_threshold": config.blue_threshold,
            "check_interval": config.check_interval
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=2)
            logging.info("Configuration saved to file")
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            raise

    def load_config_from_file(self) -> MonitorConfig:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                config = MonitorConfig()
                config.x = config_data.get("x", config.x)
                config.y = config_data.get("y", config.y)
                config.width = config_data.get("width", config.width)
                config.height = config_data.get("height", config.height)
                config.white_threshold = config_data.get("white_threshold", config.white_threshold)
                config.blue_threshold = config_data.get("blue_threshold", config.blue_threshold)
                config.check_interval = config_data.get("check_interval", config.check_interval)
                
                logging.info("Configuration loaded from file")
                return config
            except Exception as e:
                logging.error(f"Failed to load configuration: {e}")
                return MonitorConfig()
        else:
            return MonitorConfig()
