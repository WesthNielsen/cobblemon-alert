"""
Main GUI application class
"""
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import tkinter.scrolledtext as scrolledtext
import threading
import time
import logging
from PIL import Image, ImageTk

from .config import MonitorConfig, get_default_coordinates, PREVIEW_SIZE, MIN_CONSECUTIVE_DETECTIONS, BLACK_PIXEL_WARNING_THRESHOLD
from .monitor import ScreenMonitor
from .audio import AudioManager
from .config_manager import ConfigManager

class PokemonRadarGUI:
    """Main GUI application for Pokemon Radar Alert."""
    
    def __init__(self):
        """Initialize the Pokemon Radar Alert application."""
        self.monitoring = False
        self.monitor_thread = None
        self.consecutive_detections = 0
        
        # Initialize components
        self.screen_monitor = ScreenMonitor()
        self.audio_manager = AudioManager()
        self.config_manager = ConfigManager()
        
        # Configuration
        default_coords = get_default_coordinates()
        self.config = MonitorConfig(
            x=default_coords["x"],
            y=default_coords["y"],
            width=default_coords["width"],
            height=default_coords["height"]
        )
        
        # Try to load saved configuration
        saved_config = self.config_manager.load_config_from_file()
        if saved_config:
            self.config = saved_config
        
        # GUI variables
        self.root = None
        self.preview_label = None
        self.status_var = None
        
        try:
            self.setup_gui()
            logging.info("Pokemon Radar Alert initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize application: {e}")
            raise
    
    def setup_gui(self):
        """Create the GUI interface"""
        self.root = tk.Tk()
        self.root.title("Pokemon Radar Alert")
        self.root.geometry("275x600")
        
        # Add keyboard bindings
        self.root.bind('<F1>', lambda e: self.start_monitoring())
        self.root.bind('<F2>', lambda e: self.stop_monitoring())
        self.root.bind('<F3>', lambda e: self.test_area())
        self.root.bind('<Control-s>', lambda e: self.save_current_as_preset())
        
        self._create_title_section()
        self._create_monitor_area_section()
        self._create_preset_section()
        self._create_settings_section()
        self._create_preview_section()
        self._create_control_section()
        self._create_status_section()
        self._create_shortcuts_section()
    
    def _create_title_section(self):
        """Create the title section."""
        title_label = tk.Label(self.root, text="Pokemon Radar Alert", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
    
    def _create_monitor_area_section(self):
        """Create the monitor area configuration section."""
        area_frame = tk.LabelFrame(self.root, text="Monitor Area", padx=10, pady=10)
        area_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(area_frame, text="X Position:").grid(row=0, column=0, sticky="w")
        self.x_var = tk.StringVar(value=str(self.config.x))
        tk.Entry(area_frame, textvariable=self.x_var, width=10).grid(row=0, column=1, padx=5)
        
        tk.Label(area_frame, text="Y Position:").grid(row=1, column=0, sticky="w")
        self.y_var = tk.StringVar(value=str(self.config.y))
        tk.Entry(area_frame, textvariable=self.y_var, width=10).grid(row=1, column=1, padx=5)
        
        tk.Label(area_frame, text="Width:").grid(row=2, column=0, sticky="w")
        self.width_var = tk.StringVar(value=str(self.config.width))
        tk.Entry(area_frame, textvariable=self.width_var, width=10).grid(row=2, column=1, padx=5)
        
        tk.Label(area_frame, text="Height:").grid(row=3, column=0, sticky="w")
        self.height_var = tk.StringVar(value=str(self.config.height))
        tk.Entry(area_frame, textvariable=self.height_var, width=10).grid(row=3, column=1, padx=5)
        
        tk.Button(area_frame, text="Update Area", command=self.update_monitor_area).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(area_frame, text="Test Area (Screenshot)", command=self.test_area).grid(row=5, column=0, columnspan=2, pady=2)
        tk.Button(area_frame, text="Show Monitor Info", command=self.show_monitor_info).grid(row=6, column=0, columnspan=2, pady=2)
    
    def _create_preset_section(self):
        """Create the preset management section."""
        preset_frame = tk.LabelFrame(self.root, text="Coordinate Presets", padx=10, pady=10)
        preset_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(preset_frame, text="Select Preset:").grid(row=0, column=0, sticky="w")
        self.preset_dropdown = ttk.Combobox(preset_frame, state="readonly", width=12)
        self.preset_dropdown.grid(row=0, column=1, padx=5, sticky="ew")
        self.preset_dropdown.bind('<<ComboboxSelected>>', self.on_preset_selected)
        
        preset_btn_frame = tk.Frame(preset_frame)
        preset_btn_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        preset_frame.columnconfigure(1, weight=1)
        
        tk.Button(preset_btn_frame, text="Save Current", command=self.save_current_as_preset, 
                 bg="blue", fg="white", font=("Arial", 9)).pack(side="left", fill="x", expand=True, padx=1)
        tk.Button(preset_btn_frame, text="Delete Selected", command=self.delete_selected_preset, 
                 bg="red", fg="white", font=("Arial", 9)).pack(side="right", fill="x", expand=True, padx=1)
        
        self.update_preset_dropdown()
    
    def _create_settings_section(self):
        """Create the detection settings section."""
        settings_frame = tk.LabelFrame(self.root, text="Detection Settings", padx=10, pady=10)
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(settings_frame, text="White Threshold (200-255):").grid(row=0, column=0, sticky="w")
        self.threshold_var = tk.StringVar(value=str(self.config.white_threshold))
        tk.Entry(settings_frame, textvariable=self.threshold_var, width=10).grid(row=0, column=1, padx=5)
        
        tk.Label(settings_frame, text="Blue Percentage Required (%):").grid(row=1, column=0, sticky="w")
        self.blue_threshold_var = tk.StringVar(value=str(self.config.blue_threshold))
        tk.Entry(settings_frame, textvariable=self.blue_threshold_var, width=10).grid(row=1, column=1, padx=5)
        
        tk.Label(settings_frame, text="Check Interval (seconds):").grid(row=2, column=0, sticky="w")
        self.interval_var = tk.StringVar(value=str(self.config.check_interval))
        tk.Entry(settings_frame, textvariable=self.interval_var, width=10).grid(row=2, column=1, padx=5)
    
    def _create_preview_section(self):
        """Create the live preview section."""
        preview_frame = tk.LabelFrame(self.root, text="Live Preview", padx=10, pady=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.preview_label = tk.Label(preview_frame, text="Click 'Start Monitoring' to see preview")
        self.preview_label.pack(expand=True)
    
    def _create_control_section(self):
        """Create the control buttons section."""
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        self.start_button = tk.Button(control_frame, text="Start Monitoring", command=self.start_monitoring, 
                                     bg="green", fg="white", font=("Arial", 12, "bold"))
        self.start_button.pack(side="left", fill="x", expand=True, padx=2)
        
        self.stop_button = tk.Button(control_frame, text="Stop Monitoring", command=self.stop_monitoring, 
                                    bg="red", fg="white", font=("Arial", 12, "bold"), state="disabled")
        self.stop_button.pack(side="right", fill="x", expand=True, padx=2)
    
    def _create_status_section(self):
        """Create the status display section."""
        self.status_var = tk.StringVar(value="Ready to start monitoring")
        status_label = tk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_label.pack(fill="x", padx=10, pady=5)
    
    def _create_shortcuts_section(self):
        """Create the keyboard shortcuts info section."""
        shortcuts_frame = tk.Frame(self.root)
        shortcuts_frame.pack(fill="x", padx=10, pady=2)
        tk.Label(shortcuts_frame, text="Shortcuts: F1=Start, F2=Stop, F3=Test, Ctrl+S=Save", 
                 font=("Arial", 8), fg="gray").pack()
    
    def validate_inputs(self):
        """Validate GUI input values."""
        try:
            x = int(self.x_var.get())
            y = int(self.y_var.get())
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            threshold = int(self.threshold_var.get())
            blue_threshold = float(self.blue_threshold_var.get())
            interval = float(self.interval_var.get())
            
            # Validate ranges
            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be positive")
            if not (0 <= threshold <= 255):
                raise ValueError("White threshold must be between 0 and 255")
            if not (0 <= blue_threshold <= 100):
                raise ValueError("Blue threshold must be between 0 and 100")
            if interval <= 0:
                raise ValueError("Check interval must be positive")
                
            return True
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return False

    def validate_configuration(self) -> tuple[bool, str]:
        """Validate current configuration before starting monitoring."""
        try:
            # Check if coordinates are reasonable
            screen_width, screen_height = self.screen_monitor.get_screen_size()
            
            if (self.config.x < -screen_width * 2 or 
                self.config.x > screen_width * 3 or
                self.config.y < -screen_height or 
                self.config.y > screen_height * 2):
                return False, f"Coordinates appear to be out of bounds for your monitor setup"
            
            # Test screenshot capability
            test_screenshot = self.screen_monitor.take_screenshot(
                self.config.x, self.config.y, min(self.config.width, 100), min(self.config.height, 100))
            
            if test_screenshot is None:
                return False, "Cannot take screenshots at specified coordinates"
            
            # Check if screenshot is mostly black
            is_valid, black_percentage = self.screen_monitor.analyze_screenshot_quality(test_screenshot)
            
            if not is_valid:
                return False, f"Screenshot area is {black_percentage:.1f}% black - likely invalid coordinates"
            
            return True, "Configuration is valid"
            
        except Exception as e:
            return False, f"Configuration validation failed: {e}"

    def update_monitor_area(self):
        """Update the monitoring area based on GUI inputs"""
        if not self.validate_inputs():
            return
            
        try:
            self.config.x = int(self.x_var.get())
            self.config.y = int(self.y_var.get())
            self.config.width = int(self.width_var.get())
            self.config.height = int(self.height_var.get())
            self.config.white_threshold = int(self.threshold_var.get())
            self.config.blue_threshold = float(self.blue_threshold_var.get())
            self.config.check_interval = float(self.interval_var.get())
            
            # Save configuration automatically
            self.config_manager.save_config_to_file(self.config)
            
            self.status_var.set(f"Updated area: ({self.config.x}, {self.config.y}) {self.config.width}x{self.config.height}")
            logging.info(f"Monitor area updated: {self.config}")
        except Exception as e:
            logging.error(f"Failed to update monitor area: {e}")
            messagebox.showerror("Error", f"Failed to update settings: {e}")
    
    def save_current_as_preset(self):
        """Save current settings as a new preset"""
        self.update_monitor_area()
        
        preset_name = simpledialog.askstring("Save Preset", "Enter a name for this preset:")
        if not preset_name:
            return
        
        if preset_name in self.config_manager.presets:
            if not messagebox.askyesno("Overwrite Preset", f"Preset '{preset_name}' already exists. Overwrite?"):
                return
        
        try:
            self.config_manager.add_preset(preset_name, self.config)
            self.update_preset_dropdown()
            self.status_var.set(f"Preset '{preset_name}' saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save preset: {e}")
    
    def load_preset(self, preset_name):
        """Load a preset and update GUI"""
        preset = self.config_manager.get_preset(preset_name)
        if not preset:
            messagebox.showerror("Error", f"Preset '{preset_name}' not found")
            return
        
        self.x_var.set(str(preset["x"]))
        self.y_var.set(str(preset["y"]))
        self.width_var.set(str(preset["width"]))
        self.height_var.set(str(preset["height"]))
        self.threshold_var.set(str(preset["white_threshold"]))
        self.blue_threshold_var.set(str(preset["blue_threshold"]))
        self.interval_var.set(str(preset["check_interval"]))
        
        self.update_monitor_area()
        self.status_var.set(f"Loaded preset '{preset_name}'")
    
    def delete_selected_preset(self):
        """Delete the currently selected preset"""
        selected = self.preset_dropdown.get()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a preset to delete")
            return
        
        if messagebox.askyesno("Delete Preset", f"Are you sure you want to delete preset '{selected}'?"):
            try:
                self.config_manager.delete_preset(selected)
                self.update_preset_dropdown()
                self.status_var.set(f"Preset '{selected}' deleted")
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete preset: {e}")
    
    def update_preset_dropdown(self):
        """Update the preset dropdown with current presets"""
        preset_names = self.config_manager.get_preset_names()
        self.preset_dropdown['values'] = preset_names
        if preset_names:
            self.preset_dropdown.set('')
    
    def on_preset_selected(self, event):
        """Handle preset selection from dropdown"""
        selected = self.preset_dropdown.get()
        if selected and selected in self.config_manager.presets:
            self.load_preset(selected)
    
    def test_area(self):
        """Take a screenshot of the monitoring area and show it"""
        try:
            if not self.validate_inputs():
                return
                
            self.update_monitor_area()
            screen_width, screen_height = self.screen_monitor.get_screen_size()
            
            if (self.config.x < -screen_width or 
                self.config.x > screen_width * 2 or
                self.config.y < 0 or 
                self.config.y > screen_height):
                messagebox.showwarning("Warning", 
                    f"Coordinates might be out of bounds.\n"
                    f"Screen size: {screen_width}x{screen_height}\n"
                    f"Your coordinates: ({self.config.x}, {self.config.y})")
            
            screenshot = self.screen_monitor.take_screenshot(
                self.config.x, self.config.y, self.config.width, self.config.height)
            
            if screenshot is None:
                messagebox.showerror("Error", "Failed to take screenshot")
                return
            
            is_valid, black_percentage = self.screen_monitor.analyze_screenshot_quality(screenshot)
            
            if not is_valid:
                messagebox.showwarning("Screenshot Warning", 
                    f"Screenshot is {black_percentage:.1f}% black. "
                    f"This might indicate invalid coordinates for your monitor setup.\n"
                    f"Try using 'Show Monitor Info' to find valid coordinates.")
            
            screenshot.show()
            logging.info(f"Test screenshot taken: {black_percentage:.1f}% black pixels")
        except Exception as e:
            logging.error(f"Could not take test screenshot: {e}")
            messagebox.showerror("Error", f"Could not take screenshot: {str(e)}")
    
    def show_monitor_info(self):
        """Show information about monitor setup to help find correct coordinates"""
        try:
            screen_width, screen_height = self.screen_monitor.get_screen_size()
            monitor_info = self.screen_monitor.get_monitor_info()
            
            info_window = tk.Toplevel(self.root)
            info_window.title("Monitor Information")
            info_window.geometry("500x400")
            
            text_widget = scrolledtext.ScrolledText(info_window, wrap=tk.WORD, width=60, height=25)
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)
            
            info_text = f"""Monitor Setup Information (MSS):

{monitor_info}Total Virtual Screen Size: {screen_width} x {screen_height}

MSS provides excellent multi-monitor support including:
- Negative coordinates for left monitors
- Full virtual desktop coverage
- Better performance than PyAutoGUI

For multi-monitor setups:
- If your second monitor is on the LEFT of your primary monitor:
  • X coordinates typically range from -{screen_width} to 0
  • Y coordinates are usually 0 to {screen_height}
  • Try starting with X = -{screen_width//2}, Y = 100

- If your second monitor is on the RIGHT of your primary monitor:
  • X coordinates typically range from {screen_width} to {screen_width*2}
  • Y coordinates are usually 0 to {screen_height}

Current Settings:
X: {self.config.x}
Y: {self.config.y}
Width: {self.config.width}
Height: {self.config.height}

Tips for finding the right coordinates:
1. Try these common left monitor coordinates:
   • X: -{screen_width//2}, Y: {screen_height//4}
   • X: -{screen_width}, Y: 0
   • X: -{screen_width + 100}, Y: 100

2. MSS handles negative coordinates much better than PyAutoGUI
3. Use the monitor information above to see exact bounds
4. Windows Display Settings shows monitor arrangement
"""
            
            text_widget.insert(tk.END, info_text)
            text_widget.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not show monitor info: {str(e)}")
    
    def monitor_screen(self):
        """Main monitoring loop"""
        self.consecutive_detections = 0
        error_count = 0
        max_errors = 5
        loop_times = []
        
        while self.monitoring:
            loop_start = time.time()
            
            try:
                screenshot = self.screen_monitor.take_screenshot(
                    self.config.x, self.config.y, self.config.width, self.config.height)
                
                if screenshot is None:
                    error_count += 1
                    if error_count >= max_errors:
                        self.status_var.set("Too many screenshot errors - stopping monitoring")
                        self.stop_monitoring()
                        return
                    self.status_var.set(f"Error: Failed to take screenshot (attempt {error_count}/{max_errors})")
                    time.sleep(self.config.check_interval)
                    continue
                
                # Reset error count on successful screenshot
                error_count = 0
                
                is_valid, black_percentage = self.screen_monitor.analyze_screenshot_quality(screenshot)
                
                if not is_valid:
                    self.status_var.set(f"Warning: Screenshot is {black_percentage:.1f}% black - check coordinates!")
                    time.sleep(self.config.check_interval)
                    continue
                
                white_percentage = self.screen_monitor.detect_white_pixels(screenshot, self.config.white_threshold)
                blue_percentage = self.screen_monitor.detect_blue_pixels(screenshot)
                
                # Update preview
                try:
                    preview_img = screenshot.resize(PREVIEW_SIZE, Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(preview_img)
                    self.preview_label.configure(image=photo, text="")
                    self.preview_label.image = photo
                except Exception as e:
                    logging.warning(f"Failed to update preview: {e}")
                
                white_detected = white_percentage > 0.1
                blue_detected = blue_percentage >= self.config.blue_threshold
                
                # Track performance
                loop_time = time.time() - loop_start
                loop_times.append(loop_time)
                
                # Keep only last 10 measurements
                if len(loop_times) > 10:
                    loop_times.pop(0)
                
                avg_time = sum(loop_times) / len(loop_times)
                
                if white_detected and blue_detected:
                    self.consecutive_detections += 1
                    self.status_var.set(f"POKEMON DETECTED! {white_percentage:.1f}% white, {blue_percentage:.1f}% blue (detection #{self.consecutive_detections})")
                    
                    if self.consecutive_detections >= MIN_CONSECUTIVE_DETECTIONS:
                        self.audio_manager.play_alert_sound()
                        logging.info(f"Pokemon detected: {white_percentage:.1f}% white, {blue_percentage:.1f}% blue")
                        time.sleep(2)
                else:
                    self.consecutive_detections = 0
                    status_msg = f"Monitoring... {white_percentage:.1f}% white, {blue_percentage:.1f}% blue"
                    if white_detected and not blue_detected:
                        status_msg += " (White detected but insufficient blue)"
                    elif blue_detected and not white_detected:
                        status_msg += " (Blue detected but no white)"
                    
                    # Add performance info when not detecting
                    status_msg += f" | Avg loop: {avg_time:.2f}s"
                    self.status_var.set(status_msg)
                
                time.sleep(self.config.check_interval)
                
            except Exception as e:
                error_count += 1
                error_msg = f"Monitoring error ({error_count}/{max_errors}): {str(e)}"
                self.status_var.set(error_msg)
                logging.error(error_msg)
                
                if error_count >= max_errors:
                    self.status_var.set("Too many errors - stopping monitoring")
                    self.stop_monitoring()
                    return
                
                time.sleep(1)
    
    def start_monitoring(self):
        """Start the monitoring process"""
        if not self.monitoring:
            # Validate configuration first
            is_valid, message = self.validate_configuration()
            if not is_valid:
                messagebox.showerror("Invalid Configuration", 
                    f"Cannot start monitoring: {message}\n\n"
                    f"Please check your coordinates and try 'Test Area' first.")
                return
            
            self.update_monitor_area()
            self.monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_screen, daemon=True)
            self.monitor_thread.start()
            
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.status_var.set("Monitoring started...")
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_var.set("Monitoring stopped")
        
        self.preview_label.configure(image="", text="Click 'Start Monitoring' to see preview")
    
    def cleanup_resources(self):
        """Clean up all resources."""
        try:
            self.screen_monitor.cleanup()
            self.audio_manager.cleanup()
            logging.info("Resources cleaned up successfully")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing"""
        try:
            self.stop_monitoring()
            self.cleanup_resources()
            logging.info("Application closed successfully")
        except Exception as e:
            logging.error(f"Error during application closure: {e}")
        finally:
            self.root.destroy()
