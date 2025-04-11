"""
Face analysis module using deepface for detecting age, gender, emotion, and race.
"""
import os
import time
from typing import Dict, Any, List, Optional, Union, Tuple
import numpy as np
from pathlib import Path
import pandas as pd
from deepface import DeepFace
from src.utils.helpers import validate_face_detection, is_supported_image

class FaceAnalyzer:
    """
    Class for analyzing faces using the deepface library.
    """
    def __init__(self, 
                 detector_backend: str = "opencv", 
                 enforce_detection: bool = False,
                 align: bool = True):
        """
        Initialize the face analyzer.
        
        Args:
            detector_backend: The face detector backend to use
            enforce_detection: Whether to enforce face detection
            align: Whether to align detected faces
        """
        self.detector_backend = detector_backend
        self.enforce_detection = enforce_detection
        self.align = align
        
    def analyze_face(self, 
                     img_path: Union[str, np.ndarray, Path], 
                     actions: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Analyze a face in an image.
        
        Args:
            img_path: Path to the image, numpy array, or Path object
            actions: List of analysis actions to perform (age, gender, emotion, race)
            
        Returns:
            Optional[Dict[str, Any]]: The analysis results or None if no face was detected
        """
        if actions is None:
            actions = ['age', 'gender', 'emotion', 'race']
            
        try:
            result = DeepFace.analyze(
                img_path=img_path,
                detector_backend=self.detector_backend,
                enforce_detection=self.enforce_detection,
                align=self.align,
                actions=actions
            )
            
            # DeepFace.analyze returns a list of dictionaries, one for each face detected
            # For this application, we'll focus on the first face detected
            if result and isinstance(result, list) and len(result) > 0:
                return result[0]
            return None
            
        except Exception as e:
            # This likely means no face was detected
            print(f"Analysis error: {str(e)}")
            return None
    
    def batch_analyze(self, 
                      folder_path: Union[str, Path], 
                      actions: List[str] = None,
                      recursive: bool = False) -> Tuple[pd.DataFrame, List[str]]:
        """
        Analyze faces in all images in a folder.
        
        Args:
            folder_path: Path to the folder containing images
            actions: List of analysis actions to perform
            recursive: Whether to search recursively in subfolders
            
        Returns:
            Tuple[pd.DataFrame, List[str]]: DataFrame of results and list of failed files
        """
        if actions is None:
            actions = ['age', 'gender', 'emotion', 'race']
            
        # Convert to Path object if it's a string
        if isinstance(folder_path, str):
            folder_path = Path(folder_path)
            
        # Get list of image files
        all_files = []
        failed_files = []
        
        if recursive:
            for file_path in folder_path.rglob('*'):
                if file_path.is_file() and is_supported_image(file_path):
                    all_files.append(file_path)
        else:
            for file_path in folder_path.glob('*'):
                if file_path.is_file() and is_supported_image(file_path):
                    all_files.append(file_path)
        
        # Create a list to store results
        results = []
        
        # Process each file
        for file_path in all_files:
            try:
                result = self.analyze_face(file_path, actions)
                
                if result:
                    # Add the file path to the result
                    result['file_path'] = str(file_path)
                    results.append(result)
                else:
                    failed_files.append(str(file_path))
                
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")
                failed_files.append(str(file_path))
        
        # Convert results to DataFrame
        if results:
            return pd.DataFrame(results), failed_files
        else:
            return pd.DataFrame(), failed_files
    
    def verify_face(self, 
                   img_path1: Union[str, np.ndarray, Path], 
                   img_path2: Union[str, np.ndarray, Path],
                   model_name: str = "Facenet512",
                   distance_metric: str = "cosine") -> Optional[Dict[str, Any]]:
        """
        Verify if two faces belong to the same person.
        
        Args:
            img_path1: Path to the first image
            img_path2: Path to the second image
            model_name: Face recognition model to use
            distance_metric: Distance metric to use for comparison
            
        Returns:
            Optional[Dict[str, Any]]: Verification result or None if error
        """
        try:
            result = DeepFace.verify(
                img1_path=img_path1,
                img2_path=img_path2,
                model_name=model_name,
                detector_backend=self.detector_backend,
                enforce_detection=self.enforce_detection,
                align=self.align,
                distance_metric=distance_metric
            )
            return result
        except Exception as e:
            print(f"Verification error: {str(e)}")
            return None
    
    def get_embedding(self, 
                     img_path: Union[str, np.ndarray, Path],
                     model_name: str = "Facenet512") -> Optional[np.ndarray]:
        """
        Get the facial embedding for an image.
        
        Args:
            img_path: Path to the image
            model_name: Face recognition model to use
            
        Returns:
            Optional[np.ndarray]: Facial embedding or None if error
        """
        try:
            embedding_objs = DeepFace.represent(
                img_path=img_path,
                model_name=model_name,
                detector_backend=self.detector_backend,
                enforce_detection=self.enforce_detection,
                align=self.align
            )
            
            if embedding_objs and isinstance(embedding_objs, list) and len(embedding_objs) > 0:
                return embedding_objs[0]['embedding']
            return None
            
        except Exception as e:
            print(f"Embedding error: {str(e)}")
            return None
