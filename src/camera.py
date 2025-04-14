"""
Camera module for handling webcam access and image capture.
"""
import cv2
import threading
import time
from typing import Tuple, Optional, Callable, Any, List, Dict
from pathlib import Path
import numpy as np
from PIL import Image, ImageTk

class Camera:
    """
    Class for handling camera operations.
    """
    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        """
        Initialize the camera.
        
        Args:
            camera_id: The camera ID to use
            width: The width of the camera feed
            height: The height of the camera feed
        """
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = None
        self.running = False
        self.thread = None
        self.frame = None
        self.lock = threading.Lock()
    
    def start(self) -> bool:
        """
        Start the camera.
        
        Returns:
            bool: True if the camera was started successfully, False otherwise
        """
        if self.running:
            return True
        
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                return False
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
            self.running = True
            self.thread = threading.Thread(target=self._update_frame)
            self.thread.daemon = True
            self.thread.start()
            return True
        except Exception:
            self.running = False
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            return False
    
    def stop(self) -> None:
        """
        Stop the camera.
        """
        self.running = False
        if self.thread is not None:
            if self.thread.is_alive():
                self.thread.join(timeout=1.0)
            self.thread = None
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def _update_frame(self) -> None:
        """
        Update the current frame continuously.
        """
        while self.running:
            if self.cap is not None and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        self.frame = frame
            time.sleep(0.03)  # ~30 FPS
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        Get the current frame.
        
        Returns:
            Optional[np.ndarray]: The current frame or None if no frame is available
        """
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()
        return None
    
    def capture_image(self) -> Optional[np.ndarray]:
        """
        Capture a single image.
        
        Returns:
            Optional[np.ndarray]: The captured image or None if capture failed
        """
        return self.get_frame()
    
    def get_tk_image(self, frame: Optional[np.ndarray] = None, size: Optional[Tuple[int, int]] = None) -> Optional[ImageTk.PhotoImage]:
        """
        Convert a frame to a Tkinter-compatible image.
        
        Args:
            frame: The frame to convert (if None, the current frame is used)
            size: The size to resize the image to (if None, no resizing is done)
            
        Returns:
            Optional[ImageTk.PhotoImage]: The converted image or None if conversion failed
        """
        if frame is None:
            frame = self.get_frame()
        
        if frame is None:
            return None
        
        try:
            # Convert from BGR (OpenCV format) to RGB (PIL format)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
            
            if size is not None:
                pil_img = pil_img.resize(size, Image.LANCZOS)
            
            return ImageTk.PhotoImage(pil_img)
        except Exception:
            return None
    
    def save_image(self, image: np.ndarray, file_path: Path) -> bool:
        """
        Save an image to a file.
        
        Args:
            image: The image to save
            file_path: The path to save the image to
            
        Returns:
            bool: True if the image was saved successfully, False otherwise
        """
        try:
            cv2.imwrite(str(file_path), image)
            return True
        except Exception:
            return False

    def __del__(self):
        """
        Clean up resources when the object is destroyed.
        """
        self.stop()
        
    @staticmethod
    def get_available_cameras(max_cameras: int = 10) -> List[Dict[str, any]]:
        """
        Get a list of available cameras.
        
        Args:
            max_cameras: Maximum number of cameras to check
            
        Returns:
            List of dictionaries containing camera information
        """
        available_cameras = []
        
        # Try to open each camera index and check if it works
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                # Get camera name if possible
                camera_name = f"Camera {i}"
                
                # On some systems, we can get the camera name
                try:
                    # This might not work on all platforms
                    backend = cv2.CAP_ANY
                    camera_name = cap.getBackendName()
                    if not camera_name:
                        camera_name = f"Camera {i}"
                except:
                    pass
                
                available_cameras.append({
                    "id": i,
                    "name": camera_name
                })
                
                # Release the camera
                cap.release()
            else:
                # If we can't open this index, we've likely reached the end of available cameras
                if i > 0:  # Skip breaking on the first camera to handle cases where camera 0 is not available
                    break
        
        return available_cameras
