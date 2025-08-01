"""
Main entry point for Pokemon Radar Alert
"""
from src.utils import setup_logging, prevent_system_sleep
from src.gui import PokemonRadarGUI

def main():
    """Main application entry point."""
    # Set up logging first
    setup_logging()
    
    # Prevent system sleep
    prevent_system_sleep()
    
    # Create and run the application
    app = PokemonRadarGUI()
    app.run()

if __name__ == "__main__":
    main()
