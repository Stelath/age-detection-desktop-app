"""
Batch processing module for analyzing multiple images.
"""
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union, Callable
import pandas as pd
import json
import csv
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.analysis import FaceAnalyzer
from src.utils.helpers import ensure_directory_exists, generate_timestamp_filename

class BatchProcessor:
    """
    Class for batch processing images for face analysis.
    """
    def __init__(self, face_analyzer: FaceAnalyzer = None):
        """
        Initialize the batch processor.
        
        Args:
            face_analyzer: The face analyzer to use
        """
        self.face_analyzer = face_analyzer or FaceAnalyzer()
        self.processing = False
        self.progress_callback = None
        self.cancel_flag = False
        
    def process_folder(self, 
                       folder_path: Union[str, Path], 
                       actions: List[str] = None, 
                       recursive: bool = False,
                       max_workers: int = 2,  # Reduced workers to prevent memory issues
                       progress_callback: Callable[[int, int, Dict[str, Any]], None] = None) -> Tuple[pd.DataFrame, List[str]]:
        """
        Process all images in a folder.
        
        Args:
            folder_path: Path to the folder containing images
            actions: List of analysis actions to perform
            recursive: Whether to search recursively in subfolders
            max_workers: Maximum number of worker threads
            progress_callback: Callback for progress updates
            
        Returns:
            Tuple[pd.DataFrame, List[str]]: DataFrame of results and list of failed files
        """
        self.processing = True
        self.cancel_flag = False
        self.progress_callback = progress_callback
        
        if isinstance(folder_path, str):
            folder_path = Path(folder_path)
            
        if not folder_path.exists() or not folder_path.is_dir():
            self.processing = False
            return pd.DataFrame(), ["Invalid folder path"]
        
        # Get all image files
        image_files = []
        if recursive:
            for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                image_files.extend(list(folder_path.rglob(f"*{ext}")))
                image_files.extend(list(folder_path.rglob(f"*{ext.upper()}")))
        else:
            for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                image_files.extend(list(folder_path.glob(f"*{ext}")))
                image_files.extend(list(folder_path.glob(f"*{ext.upper()}")))
                
        total_files = len(image_files)
        if total_files == 0:
            self.processing = False
            return pd.DataFrame(), ["No image files found"]
        
        # Initialize progress
        processed_count = 0
        if self.progress_callback:
            self.progress_callback(processed_count, total_files, None)
        
        results = []
        failed_files = []
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(self._process_single_file, file_path, actions): file_path
                for file_path in image_files
            }
            
            for future in as_completed(future_to_file):
                if self.cancel_flag:
                    # Cancel all pending tasks
                    for f in future_to_file:
                        f.cancel()
                    self.processing = False
                    return pd.DataFrame(results) if results else pd.DataFrame(), failed_files
                
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    else:
                        failed_files.append(str(file_path))
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")
                    failed_files.append(str(file_path))
                
                processed_count += 1
                if self.progress_callback:
                    progress_info = {
                        'current': processed_count,
                        'total': total_files,
                        'success': len(results),
                        'failed': len(failed_files)
                    }
                    self.progress_callback(processed_count, total_files, progress_info)
        
        self.processing = False
        return pd.DataFrame(results) if results else pd.DataFrame(), failed_files
    
    def _process_single_file(self, file_path: Path, actions: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Process a single image file.
        
        Args:
            file_path: Path to the image file
            actions: List of analysis actions to perform
            
        Returns:
            Optional[Dict[str, Any]]: Analysis result or None if failed
        """
        try:
            # Create a thread-local face analyzer for each file to avoid resource conflicts
            # This prevents sharing the analyzer instance across threads which can cause segmentation faults
            local_analyzer = FaceAnalyzer(
                detector_backend=self.face_analyzer.detector_backend,
                enforce_detection=self.face_analyzer.enforce_detection,
                align=self.face_analyzer.align
            )
            
            # Use the thread-local analyzer
            result = local_analyzer.analyze_face(file_path, actions)
            if result:
                result['file_path'] = str(file_path)
                result['file_name'] = file_path.name
                return result
            return None
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            return None
    
    def cancel_processing(self) -> None:
        """
        Cancel the current processing operation.
        """
        self.cancel_flag = True
        
    def export_results(self, 
                       results: pd.DataFrame, 
                       export_path: Union[str, Path], 
                       format: str = 'csv',
                       include_failed: bool = True,
                       failed_files: List[str] = None) -> str:
        """
        Export analysis results to a file.
        
        Args:
            results: DataFrame of results
            export_path: Path to export the results to
            format: Export format ('csv' or 'json')
            include_failed: Whether to include failed files in the export
            failed_files: List of files that failed analysis
            
        Returns:
            str: Path to the exported file
        """
        if isinstance(export_path, str):
            export_path = Path(export_path)
            
        ensure_directory_exists(export_path)
        
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        
        if format.lower() == 'csv':
            file_path = export_path / f"face_analysis_{timestamp}.csv"
            
            # Export results
            if not results.empty:
                results.to_csv(file_path, index=False)
                
                # Append failed files if requested
                if include_failed and failed_files:
                    with open(file_path, 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([])
                        writer.writerow(["Failed Files"])
                        for failed_file in failed_files:
                            writer.writerow([failed_file])
            elif include_failed and failed_files:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Failed Files"])
                    for failed_file in failed_files:
                        writer.writerow([failed_file])
            else:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["No results found"])
                    
        elif format.lower() == 'json':
            file_path = export_path / f"face_analysis_{timestamp}.json"
            
            export_data = {}
            if not results.empty:
                export_data["results"] = results.to_dict(orient='records')
                
            if include_failed and failed_files:
                export_data["failed_files"] = failed_files
                
            if not export_data:
                export_data["message"] = "No results found"
                
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=4)
        else:
            raise ValueError(f"Unsupported export format: {format}")
            
        return str(file_path)
