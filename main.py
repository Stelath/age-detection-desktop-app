#!/usr/bin/env python3
"""
Main entry point for the Age Detection Desktop App.
"""
import tkinter as tk
import sv_ttk
import sys
import os
from pathlib import Path

from src.gui.main_window import MainWindow

def main():
    """
    Main entry point for the application.
    """
    # Create the Tkinter root window
    root = tk.Tk()
    
    # Initialize the main window
    app = MainWindow(root)
    
    # Run the application
    app.run()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        print(f"Error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
