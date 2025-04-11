"""
Main application window for the Age Detection App.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sv_ttk
from pathlib import Path
import sys
import os

from src.gui.camera_frame import CameraFrame
from src.gui.batch_frame import BatchFrame
from src.gui.results_frame import ResultsFrame

class MainWindow:
    """
    Main window class for the Age Detection App.
    """
    def __init__(self, root=None):
        """
        Initialize the main window.
        
        Args:
            root: The root Tkinter window
        """
        self.root = root or tk.Tk()
        self.root.title("Age Detection App")
        self.root.geometry("1000x650")
        self.root.minsize(900, 600)
        
        # Apply the Sun Valley theme
        sv_ttk.set_theme("dark")  # Use dark theme by default
        
        # Create the main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create the frames
        self.camera_frame = CameraFrame(self.notebook, self)
        self.batch_frame = BatchFrame(self.notebook, self)
        self.results_frame = ResultsFrame(self.notebook, self)
        
        # Add frames to notebook
        self.notebook.add(self.camera_frame, text="Camera")
        self.notebook.add(self.batch_frame, text="Batch Processing")
        
        # Create the bottom frame for controls
        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Create a frame for the theme toggle
        self.theme_frame = ttk.Frame(self.bottom_frame)
        self.theme_frame.pack(side=tk.RIGHT, padx=5)
        
        # Theme toggle
        self.theme_label = ttk.Label(self.theme_frame, text="Theme:")
        self.theme_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.theme_var = tk.StringVar(value="dark")
        self.theme_toggle = ttk.Combobox(
            self.theme_frame, 
            textvariable=self.theme_var,
            values=["dark", "light"],
            width=10,
            state="readonly"
        )
        self.theme_toggle.pack(side=tk.LEFT)
        self.theme_toggle.bind("<<ComboboxSelected>>", self._on_theme_change)
        
        # Exit button
        self.exit_button = ttk.Button(
            self.bottom_frame, 
            text="Exit", 
            command=self.exit_application
        )
        self.exit_button.pack(side=tk.RIGHT, padx=5)
        
        # Setup close handlers
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)
        
        # Create and share analysis results reference
        self.current_results = None
        self.failed_files = None
        
    def _on_theme_change(self, event=None):
        """
        Handle theme change event.
        
        Args:
            event: The event that triggered the theme change
        """
        theme = self.theme_var.get()
        sv_ttk.set_theme(theme)
        
    def show_results(self, results, failed_files=None):
        """
        Show results in the results frame.
        
        Args:
            results: The results to show
            failed_files: List of files that failed analysis
        """
        self.current_results = results
        self.failed_files = failed_files
        
        # Update the results frame
        self.results_frame.update_results(results, failed_files)
        
        # Add the results tab if not already added
        if "Results" not in [self.notebook.tab(i, "text") for i in range(self.notebook.index("end"))]:
            self.notebook.add(self.results_frame, text="Results")
            
        # Switch to the results tab
        self.notebook.select(self.notebook.index(self.results_frame))
        
    def show_error(self, title, message):
        """
        Show an error message.
        
        Args:
            title: The error title
            message: The error message
        """
        messagebox.showerror(title, message)
        
    def show_info(self, title, message):
        """
        Show an info message.
        
        Args:
            title: The info title
            message: The info message
        """
        messagebox.showinfo(title, message)
        
    def exit_application(self):
        """
        Exit the application after cleanup.
        """
        try:
            # Stop camera if running
            if hasattr(self, 'camera_frame') and self.camera_frame:
                self.camera_frame.stop_camera()
                
            # Destroy the root window
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during application exit: {str(e)}")
            sys.exit(1)
            
    def run(self):
        """
        Run the main application loop.
        """
        self.root.mainloop()
