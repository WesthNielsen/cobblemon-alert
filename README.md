# Pokemon Radar Alert

A Python application that monitors a specific area of your screen for Pokemon radar alerts. The application detects color changes in a designated region and plays audio alerts when Pokemon are detected on your radar.

## Features

- **Real-time screen monitoring**: Continuously monitors a selected area of your screen
- **Color-based detection**: Detects white and blue pixels that indicate Pokemon on radar
- **Audio alerts**: Plays customizable sound alerts when Pokemon are detected
- **Preset management**: Save and load different monitoring configurations
- **Visual feedback**: Live preview of the monitored area with detection indicators
- **Configurable thresholds**: Adjust sensitivity for different radar types
- **Logging**: Comprehensive logging for debugging and monitoring

## Requirements

- Python 3.8 or higher

## Installation

### 1. Clone or Download the Project

Download or clone this project to your local machine.

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to avoid conflicts with other Python packages.

#### On Windows:
```powershell
# Create virtual environment
python -m venv pokemon_radar_env

# Activate virtual environment
pokemon_radar_env\Scripts\Activate.ps1
```

#### On macOS/Linux:
```bash
# Create virtual environment
python3 -m venv pokemon_radar_env

# Activate virtual environment
source pokemon_radar_env/bin/activate
```

### 3. Install Dependencies

With your virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

The required packages are:
- `opencv-python>=4.5.0` - Computer vision and image processing
- `numpy>=1.20.0` - Numerical computing
- `mss>=6.0.0` - Fast screen capture
- `pygame>=2.0.0` - Audio playback
- `Pillow>=8.0.0` - Image processing

## Usage

### Running the Application

With your virtual environment activated, run:

```bash
python main.py
```

### Initial Setup

1. **Select Monitor Area**: 
   - Click "Select Area" to choose the region of your screen to monitor
   - Draw a rectangle around your Pokemon radar area
   - The selected area will be shown in the preview window

2. **Configure Thresholds**:
   - **White Threshold**: Adjust sensitivity for detecting white pixels (Pokemon indicators)
   - **Blue Threshold**: Adjust sensitivity for detecting blue pixels (water/special areas)
   - **Check Interval**: Set how often to check for changes (in seconds)

3. **Test Audio**: Click "Test Audio" to ensure sound alerts are working

### Monitoring Process

1. Click "Start Monitoring" to begin detection
2. The application will continuously capture the selected screen area
3. When Pokemon are detected (based on color thresholds), an audio alert will play
4. The preview window shows real-time detection with colored indicators:
   - White pixels indicate detected Pokemon
   - Blue pixels indicate water/special areas
   - Red overlay shows areas with insufficient contrast

### Preset Management

- **Save Preset**: Save your current configuration with a custom name
- **Load Preset**: Quickly switch between different monitoring setups
- **Delete Preset**: Remove unwanted presets

Presets are automatically saved to `pokemon_radar_presets.json`.

## Configuration Files

The application creates several configuration files:

- `pokemon_radar_presets.json`: Stores saved monitoring presets
- `pokemon_radar_config.json`: Stores the last used configuration
- `pokemon_radar.log`: Application logs for debugging

## Troubleshooting

### Common Issues

1. **No audio alerts**:
   - Check that your system volume is on
   - Test audio using the "Test Audio" button
   - Ensure pygame is properly installed

2. **Screen capture not working**:
   - On macOS: Grant screen recording permissions in System Preferences
   - On Linux: Ensure X11 or Wayland compatibility
   - On Windows: If you see MSS threading errors, restart the application
   - Try restarting the application

3. **MSS Threading Error** (`'_thread._local' object has no attribute 'srcdc'`):
   - This is a known issue with the MSS library on Windows in multi-threaded applications
   - The application has been updated to handle this automatically
   - If the error persists, try restarting the application
   - Ensure you're using the latest version of the MSS library

4. **Detection not working**:
   - Adjust white/blue thresholds
   - Ensure the selected area contains the radar
   - Check that the radar has sufficient contrast

5. **Performance issues**:
   - Increase the check interval
   - Select a smaller monitoring area
   - Close other resource-intensive applications

### Logs

Check `pokemon_radar.log` for detailed error messages and debugging information.

## Development

### Project Structure

```
pokemon-radar-alert/
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/                   # Source code package
│   ├── __init__.py        # Package marker
│   ├── gui.py            # Main GUI application
│   ├── monitor.py        # Screen monitoring logic
│   ├── audio.py          # Audio management
│   ├── config.py         # Configuration classes
│   ├── config_manager.py # Preset management
│   └── utils.py          # Utility functions
└── __pycache__/          # Python cache files
```

### Key Components

- **GUI (`gui.py`)**: Main tkinter interface with real-time preview
- **Monitor (`monitor.py`)**: Screen capture and image analysis using OpenCV
- **Audio (`audio.py`)**: Sound alert management with pygame
- **Config (`config.py`, `config_manager.py`)**: Configuration and preset handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Disclaimer

This tool is designed for personal use and automation. Always ensure you comply with the terms of service of any games or applications you use this with. The developers are not responsible for any consequences of using this software.
