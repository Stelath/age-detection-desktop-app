"""
Batch processing frame for the Age Detection App.
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
from pathlib import Path
import os
import pandas as pd

from src.analysis import FaceAnalyzer
from src.batch_processor import BatchProcessor
from src.export import Exporter

class BatchFrame(ttk.Frame):
    """
    Frame for batch processing images.
    """
    def __init__(self, parent, main_window):
        """
        Initialize the batch processing frame.
        
        Args:
            parent: The parent widget
            main_window: The main application window
        """
        super().__init__(parent)
        self.main_window = main_window
        
        # Initialize components
        self.face_analyzer = FaceAnalyzer()
        self.batch_processor = BatchProcessor(self.face_analyzer)
        self.exporter = Exporter()
        
        # Frame state variables
        self.is_processing = False
        self.folder_path = None
        self.processing_thread = None
        self.current_results = None
        self.failed_files = None
        
        # Create UI components
        self._create_widgets()
        
    def _create_widgets(self):
        """
        Create the widgets for the batch processing frame.
        """
        # Create main layout
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Options section
        self.rowconfigure(1, weight=1)  # Progress section
        
        # Options section
        self.options_frame = ttk.LabelFrame(self, text="Batch Processing Options")
        self.options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Folder selection
        self.folder_frame = ttk.Frame(self.options_frame)
        self.folder_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.folder_label = ttk.Label(self.folder_frame, text="Image Folder:")
        self.folder_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.folder_var = tk.StringVar()
        self.folder_entry = ttk.Entry(self.folder_frame, textvariable=self.folder_var, width=50)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.browse_btn = ttk.Button(
            self.folder_frame, 
            text="Browse...", 
            command=self.browse_folder
        )
        self.browse_btn.pack(side=tk.LEFT)
        
        # Processing options
        self.processing_options = ttk.Frame(self.options_frame)
        self.processing_options.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Recursive option
        self.recursive_var = tk.BooleanVar(value=False)
        self.recursive_check = ttk.Checkbutton(
            self.processing_options, 
            text="Process subfolders recursively", 
            variable=self.recursive_var
        )
        self.recursive_check.pack(side=tk.LEFT, padx=(0, 20))
        
        # Analysis options
        self.analysis_options_frame = ttk.LabelFrame(self.options_frame, text="Analysis Options")
        self.analysis_options_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Analysis checkboxes
        self.analysis_options = ttk.Frame(self.analysis_options_frame)
        self.analysis_options.pack(fill=tk.X, padx=10, pady=10)
        
        self.age_var = tk.BooleanVar(value=True)
        self.age_check = ttk.Checkbutton(
            self.analysis_options, 
            text="Age", 
            variable=self.age_var
        )
        self.age_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.gender_var = tk.BooleanVar(value=True)
        self.gender_check = ttk.Checkbutton(
            self.analysis_options, 
            text="Gender", 
            variable=self.gender_var
        )
        self.gender_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.emotion_var = tk.BooleanVar(value=True)
        self.emotion_check = ttk.Checkbutton(
            self.analysis_options, 
            text="Emotion", 
            variable=self.emotion_var
        )
        self.emotion_check.pack(side=tk.LEFT, padx=(0, 10))
        
        self.race_var = tk.BooleanVar(value=True)
        self.race_check = ttk.Checkbutton(
            self.analysis_options, 
            text="Race", 
            variable=self.race_var
        )
        self.race_check.pack(side=tk.LEFT)
        
        # Action buttons
        self.action_buttons = ttk.Frame(self.options_frame)
        self.action_buttons.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.start_btn = ttk.Button(
            self.action_buttons, 
            text="Start Processing", 
            command=self.start_processing
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.cancel_btn = ttk.Button(
            self.action_buttons, 
            text="Cancel", 
            command=self.cancel_processing,
            state=tk.DISABLED
        )
        self.cancel_btn.pack(side=tk.LEFT)
        
        # Progress section
        self.progress_frame = ttk.LabelFrame(self, text="Processing Progress")
        self.progress_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Status label
        self.status_label = ttk.Label(
            self.progress_frame, 
            text="Ready", 
            font=("TkDefaultFont", 12, "bold")
        )
        self.status_label.pack(anchor=tk.W, padx=10, pady=10)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Progress stats
        self.stats_frame = ttk.Frame(self.progress_frame)
        self.stats_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # File count
        self.files_frame = ttk.Frame(self.stats_frame)
        self.files_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        self.files_label = ttk.Label(self.files_frame, text="Files:")
        self.files_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.files_value = ttk.Label(self.files_frame, text="0/0")
        self.files_value.pack(side=tk.LEFT)
        
        # Success count
        self.success_frame = ttk.Frame(self.stats_frame)
        self.success_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        self.success_label = ttk.Label(self.success_frame, text="Successful:")
        self.success_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.success_value = ttk.Label(self.success_frame, text="0")
        self.success_value.pack(side=tk.LEFT)
        
        # Failed count
        self.failed_frame = ttk.Frame(self.stats_frame)
        self.failed_frame.pack(side=tk.LEFT)
        
        self.failed_label = ttk.Label(self.failed_frame, text="Failed:")
        self.failed_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.failed_value = ttk.Label(self.failed_frame, text="0")
        self.failed_value.pack(side=tk.LEFT)
        
        # Results buttons
        self.results_buttons = ttk.Frame(self.progress_frame)
        self.results_buttons.pack(fill=tk.X, padx=10, pady=(10, 10))
        
        self.view_results_btn = ttk.Button(
            self.results_buttons, 
            text="View Results", 
            command=self.view_results,
            state=tk.DISABLED
        )
        self.view_results_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Export format
        self.export_format_frame = ttk.Frame(self.results_buttons)
        self.export_format_frame.pack(side=tk.RIGHT)
        
        self.export_format_label = ttk.Label(self.export_format_frame, text="Export Format:")
        self.export_format_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.export_format_var = tk.StringVar(value="csv")
        self.export_format = ttk.Combobox(
            self.export_format_frame, 
            textvariable=self.export_format_var,
            values=["csv", "json"],
            width=5,
            state="readonly"
        )
        self.export_format.pack(side=tk.LEFT, padx=(0, 5))
        
        self.export_btn = ttk.Button(
            self.results_buttons, 
            text="Export Results", 
            command=self.export_results,
            state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.RIGHT)
        
    def browse_folder(self):
        """
        Browse for a folder of images to process.
        """
        folder_path = filedialog.askdirectory(
            title="Select Image Folder",
            initialdir=os.path.expanduser("~/Pictures")
        )
        
        if folder_path:
            self.folder_path = folder_path
            self.folder_var.set(folder_path)
    
    def start_processing(self):
        """
        Start batch processing images.
        """
        if self.is_processing:
            return
            
        # Get the folder path
        folder_path = self.folder_var.get().strip()
        if not folder_path:
            self.main_window.show_error(
                "Input Error", 
                "Please select a folder to process."
            )
            return
            
        # Check if folder exists
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            self.main_window.show_error(
                "Input Error", 
                "The selected folder does not exist."
            )
            return
            
        # Get selected analysis actions
        actions = []
        if self.age_var.get():
            actions.append('age')
        if self.gender_var.get():
            actions.append('gender')
        if self.emotion_var.get():
            actions.append('emotion')
        if self.race_var.get():
            actions.append('race')
            
        if not actions:
            self.main_window.show_error(
                "Input Error", 
                "Please select at least one analysis option."
            )
            return
            
        # Update UI for processing state
        self.is_processing = True
        self.start_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.browse_btn.config(state=tk.DISABLED)
        self.view_results_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        
        # Reset progress indicators
        self.progress_bar['value'] = 0
        self.files_value.config(text="0/0")
        self.success_value.config(text="0")
        self.failed_value.config(text="0")
        self.status_label.config(text="Processing...")
        
        # Start processing in a separate thread
        self.processing_thread = threading.Thread(
            target=self._perform_batch_processing,
            args=(folder_path, actions, self.recursive_var.get())
        )
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
    def _perform_batch_processing(self, folder_path, actions, recursive):
        """
        Perform batch processing in a separate thread.
        
        Args:
            folder_path: Path to the folder containing images
            actions: List of analysis actions to perform
            recursive: Whether to search recursively in subfolders
        """
        try:
            # Process the folder
            results, failed = self.batch_processor.process_folder(
                folder_path=folder_path,
                actions=actions,
                recursive=recursive,
                progress_callback=self._update_progress
            )
            
            # Store the results
            self.current_results = results
            self.failed_files = failed
            
            # Update UI after processing
            self.after(0, lambda: self._processing_complete())
            
        except Exception as e:
            print(f"Batch processing error: {str(e)}")
            self.after(0, lambda: self._processing_error(str(e)))
    
    def _update_progress(self, current, total, info=None):
        """
        Update the progress indicators.
        
        Args:
            current: Current number of processed files
            total: Total number of files to process
            info: Additional progress information
        """
        # Calculate progress percentage
        if total > 0:
            progress = (current / total) * 100
        else:
            progress = 0
            
        # Update UI elements
        self.after(0, lambda: self._update_progress_ui(current, total, progress, info))
    
    def _update_progress_ui(self, current, total, progress, info):
        """
        Update the progress UI elements.
        
        Args:
            current: Current number of processed files
            total: Total number of files to process
            progress: Progress percentage
            info: Additional progress information
        """
        # Update progress bar
        self.progress_bar['value'] = progress
        
        # Update status text
        self.files_value.config(text=f"{current}/{total}")
        
        if info:
            success_count = info.get('success', 0)
            failed_count = info.get('failed', 0)
            
            self.success_value.config(text=str(success_count))
            self.failed_value.config(text=str(failed_count))
    
    def _processing_complete(self):
        """
        Handle completion of batch processing.
        """
        # Update UI
        self.is_processing = False
        self.status_label.config(text="Processing complete")
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.browse_btn.config(state=tk.NORMAL)
        
        # Enable result buttons if we have results
        if self.current_results is not None and not self.current_results.empty:
            self.view_results_btn.config(state=tk.NORMAL)
            self.export_btn.config(state=tk.NORMAL)
            
            # Show number of results
            num_results = len(self.current_results)
            num_failed = len(self.failed_files) if self.failed_files else 0
            
            messagebox.showinfo(
                "Processing Complete",
                f"Successfully processed {num_results} images.\n"
                f"Failed to process {num_failed} images."
            )
        else:
            messagebox.showinfo(
                "Processing Complete",
                "No faces were detected in any of the images."
            )
    
    def _processing_error(self, error_message):
        """
        Handle batch processing errors.
        
        Args:
            error_message: The error message
        """
        # Update UI
        self.is_processing = False
        self.status_label.config(text="Processing failed")
        self.start_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.browse_btn.config(state=tk.NORMAL)
        
        # Show error
        self.main_window.show_error(
            "Processing Error",
            f"Error during batch processing: {error_message}"
        )
    
    def cancel_processing(self):
        """
        Cancel the current batch processing operation.
        """
        if not self.is_processing:
            return
            
        # Set cancel flag
        self.batch_processor.cancel_processing()
        
        # Update UI
        self.status_label.config(text="Cancelling...")
        self.cancel_btn.config(state=tk.DISABLED)
    
    def view_results(self):
        """
        View the batch processing results.
        """
        if self.current_results is None or self.current_results.empty:
            self.main_window.show_error(
                "No Results",
                "There are no results to view."
            )
            return
            
        # Show results in the main window
        self.main_window.show_results(self.current_results, self.failed_files)
    
    def export_results(self):
        """
        Export the batch processing results.
        """
        if self.current_results is None or self.current_results.empty:
            self.main_window.show_error(
                "No Results",
                "There are no results to export."
            )
            return
            
        # Ask for export location
        export_dir = filedialog.askdirectory(
            title="Select Export Directory",
            initialdir=self.exporter.default_export_path
        )
        
        if not export_dir:
            return
            
        try:
            # Export the results
            export_format = self.export_format_var.get()
            export_path = self.exporter.export_results(
                results=self.current_results,
                export_format=export_format,
                export_path=Path(export_dir),
                include_failed=True,
                failed_files=self.failed_files
            )
            
            # Show success message
            self.main_window.show_info(
                "Export Successful",
                f"Results exported to {export_path}"
            )
            
        except Exception as e:
            self.main_window.show_error(
                "Export Error",
                f"Error exporting results: {str(e)}"
            )
