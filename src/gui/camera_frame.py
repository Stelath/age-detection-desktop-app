"""
Camera frame for the Age Detection App.
"""
import tkinter as tk
from tkinter import ttk, filedialog
import cv2
import threading
import time
from pathlib import Path
import os
from PIL import Image, ImageTk
import numpy as np
from datetime import datetime

from src.camera import Camera
from src.analysis import FaceAnalyzer, ModelLoader

class CameraFrame(ttk.Frame):
    """
    Frame for camera operations and displaying live feed.
    """
    def __init__(self, parent, main_window):
        """
        Initialize the camera frame.
        
        Args:
            parent: The parent widget
            main_window: The main application window
        """
        super().__init__(parent)
        self.main_window = main_window
        
        # Initialize camera and analyzer
        self.camera = None
        self.face_analyzer = FaceAnalyzer()
        
        # Frame state variables
        self.is_camera_running = False
        self.is_analyzing = False
        self.current_frame = None
        self.analysis_result = None
        self.update_thread = None
        self.frame_update_running = False
        
        # Create the UI components
        self._create_widgets()
        
    def _create_widgets(self):
        """
        Create the widgets for the camera frame.
        """
        # Create main layout
        self.columnconfigure(0, weight=1)  # Camera view column
        self.columnconfigure(1, weight=1)  # Results column
        self.rowconfigure(0, weight=0)     # Model selection row
        self.rowconfigure(1, weight=1)     # Main content row
        
        # Model selection frame
        self.model_frame = ttk.LabelFrame(self, text="Model Settings")
        self.model_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 0), sticky="ew")
        
        # Model selection options
        self.model_options = ttk.Frame(self.model_frame)
        self.model_options.pack(fill=tk.X, padx=10, pady=10)
        
        # Face detector selection
        self.detector_frame = ttk.Frame(self.model_options)
        self.detector_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        self.detector_label = ttk.Label(self.detector_frame, text="Face Detector:")
        self.detector_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.detector_var = tk.StringVar(value="opencv")
        self.detector_combo = ttk.Combobox(
            self.detector_frame,
            textvariable=self.detector_var,
            values=["opencv", "retinaface", "mtcnn", "ssd"],
            width=10,
            state="readonly"
        )
        self.detector_combo.pack(side=tk.LEFT)
        self.detector_combo.bind("<<ComboboxSelected>>", self._update_detector)
        
        # Face recognition model selection
        self.model_frame = ttk.Frame(self.model_options)
        self.model_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        self.model_label = ttk.Label(self.model_frame, text="Recognition Model:")
        self.model_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.model_var = tk.StringVar(value="Facenet512")
        self.model_combo = ttk.Combobox(
            self.model_frame,
            textvariable=self.model_var,
            values=["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "ArcFace"],
            width=10,
            state="readonly"
        )
        self.model_combo.pack(side=tk.LEFT)
        
        # Preload models button
        self.preload_btn = ttk.Button(
            self.model_options,
            text="Preload Models",
            command=self._preload_models
        )
        self.preload_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Left side - Camera View
        self.camera_frame = ttk.LabelFrame(self, text="Camera Feed")
        self.camera_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Camera canvas
        self.canvas = tk.Canvas(self.camera_frame, bg="black", width=480, height=360)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Camera controls frame
        self.camera_controls = ttk.Frame(self.camera_frame)
        self.camera_controls.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Camera controls
        self.camera_toggle_btn = ttk.Button(
            self.camera_controls, 
            text="Start Camera", 
            command=self.toggle_camera
        )
        self.camera_toggle_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.capture_btn = ttk.Button(
            self.camera_controls, 
            text="Capture & Analyze", 
            command=self.capture_and_analyze,
            state=tk.DISABLED
        )
        self.capture_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(
            self.camera_controls, 
            text="Save Image", 
            command=self.save_image,
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Right side - Results View
        self.results_frame = ttk.LabelFrame(self, text="Analysis Results")
        self.results_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Status label
        self.status_label = ttk.Label(
            self.results_frame, 
            text="Camera not started", 
            font=("TkDefaultFont", 12, "bold")
        )
        self.status_label.pack(anchor=tk.W, padx=10, pady=10)
        
        # Face detection status
        self.face_status_frame = ttk.Frame(self.results_frame)
        self.face_status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.face_status_label = ttk.Label(
            self.face_status_frame, 
            text="Face Detection:", 
            width=15, 
            anchor=tk.W
        )
        self.face_status_label.pack(side=tk.LEFT)
        
        self.face_status_value = ttk.Label(
            self.face_status_frame, 
            text="Not detected", 
            foreground="red"
        )
        self.face_status_value.pack(side=tk.LEFT, padx=(0, 10))
        
        # Results display
        self.results_display = ttk.Frame(self.results_frame)
        self.results_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Age result
        self.age_frame = ttk.Frame(self.results_display)
        self.age_frame.pack(fill=tk.X, pady=2)
        
        self.age_label = ttk.Label(self.age_frame, text="Age:", width=15, anchor=tk.W)
        self.age_label.pack(side=tk.LEFT)
        
        self.age_value = ttk.Label(self.age_frame, text="-")
        self.age_value.pack(side=tk.LEFT)
        
        # Gender result
        self.gender_frame = ttk.Frame(self.results_display)
        self.gender_frame.pack(fill=tk.X, pady=2)
        
        self.gender_label = ttk.Label(self.gender_frame, text="Gender:", width=15, anchor=tk.W)
        self.gender_label.pack(side=tk.LEFT)
        
        self.gender_value = ttk.Label(self.gender_frame, text="-")
        self.gender_value.pack(side=tk.LEFT)
        
        # Emotion result
        self.emotion_frame = ttk.Frame(self.results_display)
        self.emotion_frame.pack(fill=tk.X, pady=2)
        
        self.emotion_label = ttk.Label(self.emotion_frame, text="Emotion:", width=15, anchor=tk.W)
        self.emotion_label.pack(side=tk.LEFT)
        
        self.emotion_value = ttk.Label(self.emotion_frame, text="-")
        self.emotion_value.pack(side=tk.LEFT)
        
        # Race result
        self.race_frame = ttk.Frame(self.results_display)
        self.race_frame.pack(fill=tk.X, pady=2)
        
        self.race_label = ttk.Label(self.race_frame, text="Race:", width=15, anchor=tk.W)
        self.race_label.pack(side=tk.LEFT)
        
        self.race_value = ttk.Label(self.race_frame, text="-")
        self.race_value.pack(side=tk.LEFT)
        
        # Confidence frame
        self.confidence_frame = ttk.Frame(self.results_display)
        self.confidence_frame.pack(fill=tk.X, pady=2)
        
        self.confidence_label = ttk.Label(
            self.confidence_frame, 
            text="Confidence:", 
            width=15, 
            anchor=tk.W
        )
        self.confidence_label.pack(side=tk.LEFT)
        
        self.confidence_value = ttk.Label(self.confidence_frame, text="-")
        self.confidence_value.pack(side=tk.LEFT)
        
        # Add "Show All Data" button
        self.show_all_btn = ttk.Button(
            self.results_frame, 
            text="Show All Data", 
            command=self.show_all_results,
            state=tk.DISABLED
        )
        self.show_all_btn.pack(pady=(10, 10))
        
    def toggle_camera(self):
        """
        Toggle the camera on/off.
        """
        if not self.is_camera_running:
            self.start_camera()
        else:
            self.stop_camera()
            
    def start_camera(self):
        """
        Start the camera.
        """
        if self.is_camera_running:
            return
            
        # Initialize camera object
        self.camera = Camera()
        
        # Start the camera
        if self.camera.start():
            self.is_camera_running = True
            self.frame_update_running = True
            
            # Update UI
            self.camera_toggle_btn.config(text="Stop Camera")
            self.capture_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Camera running")
            
            # Start the frame update thread
            self.update_thread = threading.Thread(target=self._update_frame)
            self.update_thread.daemon = True
            self.update_thread.start()
        else:
            self.main_window.show_error(
                "Camera Error", 
                "Could not start the camera. Please check if it's connected properly."
            )
            
    def stop_camera(self):
        """
        Stop the camera.
        """
        if not self.is_camera_running:
            return
            
        # Stop the frame update thread
        self.frame_update_running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
            
        # Stop the camera
        if self.camera:
            self.camera.stop()
            self.camera = None
            
        # Update UI
        self.is_camera_running = False
        self.camera_toggle_btn.config(text="Start Camera")
        self.capture_btn.config(state=tk.DISABLED)
        self.save_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Camera stopped")
        
        # Clear canvas
        self.canvas.delete("all")
        
    def _update_frame(self):
        """
        Update the camera frame continuously.
        """
        while self.frame_update_running and self.camera:
            try:
                # Get frame from camera
                frame = self.camera.get_frame()
                
                if frame is not None:
                    self.current_frame = frame
                    
                    # Convert to Tkinter image
                    frame_h, frame_w = frame.shape[:2]
                    canvas_w = self.canvas.winfo_width()
                    canvas_h = self.canvas.winfo_height()
                    
                    # Calculate scaling to fit the canvas while maintaining aspect ratio
                    scale = min(canvas_w/frame_w, canvas_h/frame_h)
                    new_w = int(frame_w * scale)
                    new_h = int(frame_h * scale)
                    
                    # Convert and resize the image
                    img_tk = self.camera.get_tk_image(frame, (new_w, new_h))
                    
                    if img_tk:
                        # Update canvas
                        self.canvas.delete("all")
                        self.canvas.create_image(
                            canvas_w//2, canvas_h//2, 
                            anchor=tk.CENTER, 
                            image=img_tk
                        )
                        self.canvas.image = img_tk  # Keep a reference
            except Exception as e:
                print(f"Error updating frame: {str(e)}")
                
            # Sleep to reduce CPU usage
            time.sleep(0.03)  # ~30 FPS
            
    def capture_and_analyze(self):
        """
        Capture the current frame and analyze it.
        """
        if not self.is_camera_running or not self.current_frame is not None:
            return
            
        # Disable the button during analysis
        self.capture_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Analyzing face...")
        
        # Start analysis in a separate thread
        threading.Thread(target=self._perform_analysis).start()
        
    def _perform_analysis(self):
        """
        Perform face analysis on the current frame.
        """
        try:
            # Analyze the current frame
            result = self.face_analyzer.analyze_face(
                self.current_frame,
                actions=['age', 'gender', 'emotion', 'race']
            )
            
            # Update UI with results
            self.after(0, lambda: self._update_results(result))
            
        except Exception as e:
            # Handle errors
            print(f"Analysis error: {str(e)}")
            self.after(0, lambda: self._handle_analysis_error(str(e)))
            
    def _update_results(self, result):
        """
        Update the UI with analysis results.
        
        Args:
            result: The analysis result
        """
        # Store the result
        self.analysis_result = result
        
        if result:
            # Face detected
            self.face_status_value.config(text="Detected", foreground="green")
            
            # Update result values
            self.age_value.config(text=f"{result.get('age', 'N/A')} years")
            
            # For gender, use dominant_gender and its confidence from the gender dict
            gender = result.get('dominant_gender', 'N/A')
            gender_confidence = result.get('gender', {}).get(gender, 0)
            self.gender_value.config(text=f"{gender} ({gender_confidence:.1f}%)")
            
            # For emotion, use dominant_emotion and its confidence from the emotion dict
            emotion = result.get('dominant_emotion', 'N/A')
            emotion_confidence = result.get('emotion', {}).get(emotion, 0)
            self.emotion_value.config(text=f"{emotion.capitalize()} ({emotion_confidence:.1f}%)")
            
            # For race, use dominant_race and its confidence from the race dict
            race = result.get('dominant_race', 'N/A')
            race_confidence = result.get('race', {}).get(race, 0)
            self.race_value.config(text=f"{race.capitalize()} ({race_confidence:.1f}%)")
            
            # Enable save and show all buttons
            self.save_btn.config(state=tk.NORMAL)
            self.show_all_btn.config(state=tk.NORMAL)
            
        else:
            # No face detected
            self.face_status_value.config(text="Not detected", foreground="red")
            
            # Clear result values
            self.age_value.config(text="-")
            self.gender_value.config(text="-")
            self.emotion_value.config(text="-")
            self.race_value.config(text="-")
            self.confidence_value.config(text="-")
            
            # Disable save and show all buttons
            self.save_btn.config(state=tk.DISABLED)
            self.show_all_btn.config(state=tk.DISABLED)
            
            # Show error
            self.main_window.show_error(
                "Analysis Error", 
                "No face detected in the image."
            )
            
        # Re-enable the capture button
        self.capture_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Analysis complete")
        
    def _handle_analysis_error(self, error_message):
        """
        Handle analysis errors.
        
        Args:
            error_message: The error message
        """
        # Clear result values
        self.face_status_value.config(text="Error", foreground="red")
        self.age_value.config(text="-")
        self.gender_value.config(text="-")
        self.emotion_value.config(text="-")
        self.race_value.config(text="-")
        self.confidence_value.config(text="-")
        
        # Re-enable the capture button
        self.capture_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Analysis failed")
        
        # Show error
        self.main_window.show_error(
            "Analysis Error", 
            f"Error analyzing face: {error_message}"
        )
        
    def save_image(self):
        """
        Save the current frame to a file.
        """
        if self.current_frame is None:
            return
            
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            initialdir=os.path.expanduser("~/Pictures"),
            title="Save Image",
            filetypes=[("JPEG files", "*.jpg"), ("All files", "*.*")],
            defaultextension=".jpg"
        )
        
        if file_path:
            try:
                # Save the image
                cv2.imwrite(file_path, self.current_frame)
                
                # Save analysis result as JSON if available
                if self.analysis_result:
                    json_path = Path(file_path).with_suffix('.json')
                    import json
                    with open(json_path, 'w') as f:
                        json.dump(self.analysis_result, f, indent=4)
                        
                self.main_window.show_info(
                    "Save Successful", 
                    f"Image saved to {file_path}"
                )
                
            except Exception as e:
                self.main_window.show_error(
                    "Save Error", 
                    f"Error saving image: {str(e)}"
                )
                
    def _update_detector(self, event=None):
        """
        Update the face detector when the selection changes.
        
        Args:
            event: The event that triggered the update
        """
        detector = self.detector_var.get()
        self.face_analyzer.detector_backend = detector
        print(f"Face detector changed to: {detector}")
        
    def _preload_models(self):
        """
        Preload the models to avoid delays during analysis.
        """
        # Disable the button during loading
        self.preload_btn.config(state=tk.DISABLED)
        self.status_label.config(text="Loading models...")
        
        # Create model loader with progress dialog
        model_loader = ModelLoader(self)
        
        # Start loading models
        model_loader.load_models(
            actions=['age', 'gender', 'emotion', 'race'],
            callback=self._on_models_loaded
        )
        
    def _on_models_loaded(self):
        """
        Callback for when models are loaded.
        """
        self.preload_btn.config(state=tk.NORMAL)
        self.status_label.config(text="Models loaded")
        self.main_window.show_info(
            "Models Loaded",
            "All models have been successfully loaded!"
        )
        
    def show_all_results(self):
        """
        Show all analysis results in a new window.
        """
        if not self.analysis_result:
            return
            
        # Create a new top-level window
        result_window = tk.Toplevel(self)
        result_window.title("Complete Analysis Results")
        result_window.geometry("600x500")
        result_window.grab_set()  # Make window modal
        
        # Create a text widget to display the results
        text_frame = ttk.Frame(result_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, padx=5, pady=5)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Insert the results
        import json
        
        # Convert numpy arrays to lists for JSON serialization
        result_copy = {}
        for key, value in self.analysis_result.items():
            if isinstance(value, dict):
                result_copy[key] = {k: float(v) if hasattr(v, 'item') else v for k, v in value.items()}
            elif hasattr(value, 'tolist') and callable(getattr(value, 'tolist')):
                result_copy[key] = value.tolist()
            else:
                result_copy[key] = value
        
        text_widget.insert(tk.END, json.dumps(result_copy, indent=4))
        text_widget.config(state=tk.DISABLED)  # Make read-only
        
        # Add a close button
        close_btn = ttk.Button(
            result_window, 
            text="Close", 
            command=result_window.destroy
        )
        close_btn.pack(pady=(0, 10))
