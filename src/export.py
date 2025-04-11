"""
Export module for exporting analysis results.
"""
from pathlib import Path
import pandas as pd
import json
import csv
import time
from typing import Dict, Any, List, Optional, Union

from src.utils.helpers import ensure_directory_exists, generate_timestamp_filename

class Exporter:
    """
    Class for exporting analysis results.
    """
    def __init__(self, default_export_path: Optional[Path] = None):
        """
        Initialize the exporter.
        
        Args:
            default_export_path: Default path for exports
        """
        self.default_export_path = default_export_path or Path.home() / "Documents" / "AgeDetectionExports"
        ensure_directory_exists(self.default_export_path)
        
    def export_to_csv(self, 
                     results: pd.DataFrame, 
                     export_path: Optional[Path] = None,
                     filename: Optional[str] = None,
                     include_failed: bool = True,
                     failed_files: Optional[List[str]] = None) -> str:
        """
        Export results to CSV.
        
        Args:
            results: DataFrame of results
            export_path: Path to export the file to
            filename: Name of the export file
            include_failed: Whether to include failed files
            failed_files: List of failed files
            
        Returns:
            str: Path to the exported file
        """
        export_path = export_path or self.default_export_path
        ensure_directory_exists(export_path)
        
        if filename is None:
            filename = generate_timestamp_filename("face_analysis", "csv")
            
        file_path = export_path / filename
        
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
                
        return str(file_path)
    
    def export_to_json(self, 
                      results: pd.DataFrame, 
                      export_path: Optional[Path] = None,
                      filename: Optional[str] = None,
                      include_failed: bool = True,
                      failed_files: Optional[List[str]] = None) -> str:
        """
        Export results to JSON.
        
        Args:
            results: DataFrame of results
            export_path: Path to export the file to
            filename: Name of the export file
            include_failed: Whether to include failed files
            failed_files: List of failed files
            
        Returns:
            str: Path to the exported file
        """
        export_path = export_path or self.default_export_path
        ensure_directory_exists(export_path)
        
        if filename is None:
            filename = generate_timestamp_filename("face_analysis", "json")
            
        file_path = export_path / filename
        
        export_data = {}
        if not results.empty:
            export_data["results"] = results.to_dict(orient='records')
            
        if include_failed and failed_files:
            export_data["failed_files"] = failed_files
            
        if not export_data:
            export_data["message"] = "No results found"
            
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=4)
                
        return str(file_path)
    
    def export_results(self, 
                      results: pd.DataFrame, 
                      export_format: str = 'csv',
                      export_path: Optional[Path] = None,
                      filename: Optional[str] = None,
                      include_failed: bool = True,
                      failed_files: Optional[List[str]] = None) -> str:
        """
        Export results in the specified format.
        
        Args:
            results: DataFrame of results
            export_format: Format to export to ('csv' or 'json')
            export_path: Path to export the file to
            filename: Name of the export file
            include_failed: Whether to include failed files
            failed_files: List of failed files
            
        Returns:
            str: Path to the exported file
        """
        if export_format.lower() == 'csv':
            return self.export_to_csv(
                results, export_path, filename, include_failed, failed_files
            )
        elif export_format.lower() == 'json':
            return self.export_to_json(
                results, export_path, filename, include_failed, failed_files
            )
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
