"""
Results frame for displaying analysis results.
"""
import tkinter as tk
from tkinter import ttk
import pandas as pd
from typing import Dict, Any, List, Optional
import json

class ResultsFrame(ttk.Frame):
    """
    Frame for displaying analysis results.
    """
    def __init__(self, parent, main_window):
        """
        Initialize the results frame.
        
        Args:
            parent: The parent widget
            main_window: The main application window
        """
        super().__init__(parent)
        self.main_window = main_window
        
        # Data
        self.results = None
        self.failed_files = None
        
        # Create UI components
        self._create_widgets()
        
    def _create_widgets(self):
        """
        Create the widgets for the results frame.
        """
        # Configure grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # Controls area
        self.rowconfigure(1, weight=1)  # Results treeview
        self.rowconfigure(2, weight=0)  # Summary area
        
        # Controls area
        self.controls_frame = ttk.Frame(self)
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Filter controls
        self.filter_frame = ttk.LabelFrame(self.controls_frame, text="Filter Results")
        self.filter_frame.pack(fill=tk.X, expand=True)
        
        # Age filter
        self.age_filter_frame = ttk.Frame(self.filter_frame)
        self.age_filter_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.age_label = ttk.Label(self.age_filter_frame, text="Age Range:")
        self.age_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.age_min_var = tk.StringVar()
        self.age_min_entry = ttk.Entry(self.age_filter_frame, textvariable=self.age_min_var, width=5)
        self.age_min_entry.pack(side=tk.LEFT)
        
        self.age_to_label = ttk.Label(self.age_filter_frame, text="to")
        self.age_to_label.pack(side=tk.LEFT, padx=5)
        
        self.age_max_var = tk.StringVar()
        self.age_max_entry = ttk.Entry(self.age_filter_frame, textvariable=self.age_max_var, width=5)
        self.age_max_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Gender filter
        self.gender_filter_frame = ttk.Frame(self.filter_frame)
        self.gender_filter_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.gender_label = ttk.Label(self.gender_filter_frame, text="Gender:")
        self.gender_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.gender_var = tk.StringVar(value="All")
        self.gender_combo = ttk.Combobox(
            self.gender_filter_frame, 
            textvariable=self.gender_var,
            values=["All", "Man", "Woman"],
            width=8,
            state="readonly"
        )
        self.gender_combo.pack(side=tk.LEFT)
        
        # Emotion filter
        self.emotion_filter_frame = ttk.Frame(self.filter_frame)
        self.emotion_filter_frame.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.emotion_label = ttk.Label(self.emotion_filter_frame, text="Emotion:")
        self.emotion_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.emotion_var = tk.StringVar(value="All")
        self.emotion_combo = ttk.Combobox(
            self.emotion_filter_frame, 
            textvariable=self.emotion_var,
            values=["All", "Happy", "Sad", "Angry", "Fear", "Surprise", "Neutral", "Disgust"],
            width=10,
            state="readonly"
        )
        self.emotion_combo.pack(side=tk.LEFT)
        
        # Filter button
        self.filter_btn = ttk.Button(
            self.filter_frame, 
            text="Apply Filters", 
            command=self._apply_filters
        )
        self.filter_btn.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Reset button
        self.reset_btn = ttk.Button(
            self.filter_frame, 
            text="Reset Filters", 
            command=self._reset_filters
        )
        self.reset_btn.pack(side=tk.LEFT, padx=(0, 10), pady=5)
        
        # Results area
        self.results_frame = ttk.Frame(self)
        self.results_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Create notebook for results tabs
        self.notebook = ttk.Notebook(self.results_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Results tab
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Results")
        
        # Create treeview for results
        self.results_tree_frame = ttk.Frame(self.results_tab)
        self.results_tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.results_tree = ttk.Treeview(
            self.results_tree_frame,
            columns=("file", "age", "gender", "emotion", "race"),
            show="headings"
        )
        
        # Configure treeview columns
        self.results_tree.heading("file", text="File")
        self.results_tree.heading("age", text="Age")
        self.results_tree.heading("gender", text="Gender")
        self.results_tree.heading("emotion", text="Emotion")
        self.results_tree.heading("race", text="Race")
        
        self.results_tree.column("file", width=300)
        self.results_tree.column("age", width=60, anchor=tk.CENTER)
        self.results_tree.column("gender", width=100, anchor=tk.CENTER)
        self.results_tree.column("emotion", width=100, anchor=tk.CENTER)
        self.results_tree.column("race", width=100, anchor=tk.CENTER)
        
        # Add scrollbars
        self.y_scrollbar = ttk.Scrollbar(self.results_tree_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=self.y_scrollbar.set)
        
        self.x_scrollbar = ttk.Scrollbar(self.results_tree_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(xscrollcommand=self.x_scrollbar.set)
        
        # Pack scrollbars and treeview
        self.y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Failed files tab
        self.failed_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.failed_tab, text="Failed Files")
        
        # Create listbox for failed files
        self.failed_frame = ttk.Frame(self.failed_tab)
        self.failed_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.failed_list = tk.Listbox(self.failed_frame, selectmode=tk.SINGLE)
        self.failed_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.failed_scrollbar = ttk.Scrollbar(self.failed_frame, orient=tk.VERTICAL, command=self.failed_list.yview)
        self.failed_list.configure(yscrollcommand=self.failed_scrollbar.set)
        self.failed_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Summary area
        self.summary_frame = ttk.LabelFrame(self, text="Summary")
        self.summary_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        
        # Count summary
        self.count_frame = ttk.Frame(self.summary_frame)
        self.count_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.total_label = ttk.Label(self.count_frame, text="Total Files:")
        self.total_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.total_value = ttk.Label(self.count_frame, text="0")
        self.total_value.pack(side=tk.LEFT, padx=(0, 15))
        
        self.success_label = ttk.Label(self.count_frame, text="Successful:")
        self.success_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.success_value = ttk.Label(self.count_frame, text="0")
        self.success_value.pack(side=tk.LEFT, padx=(0, 15))
        
        self.failed_label = ttk.Label(self.count_frame, text="Failed:")
        self.failed_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.failed_value = ttk.Label(self.count_frame, text="0")
        self.failed_value.pack(side=tk.LEFT)
        
        # Age statistics
        self.age_stats_frame = ttk.Frame(self.summary_frame)
        self.age_stats_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        self.age_avg_label = ttk.Label(self.age_stats_frame, text="Average Age:")
        self.age_avg_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.age_avg_value = ttk.Label(self.age_stats_frame, text="-")
        self.age_avg_value.pack(side=tk.LEFT, padx=(0, 15))
        
        self.age_min_label = ttk.Label(self.age_stats_frame, text="Min Age:")
        self.age_min_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.age_min_value = ttk.Label(self.age_stats_frame, text="-")
        self.age_min_value.pack(side=tk.LEFT, padx=(0, 15))
        
        self.age_max_label = ttk.Label(self.age_stats_frame, text="Max Age:")
        self.age_max_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.age_max_value = ttk.Label(self.age_stats_frame, text="-")
        self.age_max_value.pack(side=tk.LEFT)
        
        # Gender statistics
        self.gender_stats_frame = ttk.Frame(self.summary_frame)
        self.gender_stats_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        self.men_label = ttk.Label(self.gender_stats_frame, text="Men:")
        self.men_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.men_value = ttk.Label(self.gender_stats_frame, text="0 (0%)")
        self.men_value.pack(side=tk.LEFT, padx=(0, 15))
        
        self.women_label = ttk.Label(self.gender_stats_frame, text="Women:")
        self.women_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.women_value = ttk.Label(self.gender_stats_frame, text="0 (0%)")
        self.women_value.pack(side=tk.LEFT)
        
        # View details button
        self.details_btn = ttk.Button(
            self.summary_frame, 
            text="View Selected Details", 
            command=self._view_selected_details
        )
        self.details_btn.pack(side=tk.RIGHT, padx=10, pady=(0, 5))
        
        # Initialize with empty data
        self.update_results(pd.DataFrame(), [])
        
    def update_results(self, results: pd.DataFrame, failed_files: Optional[List[str]] = None):
        """
        Update the results display with new data.
        
        Args:
            results: DataFrame of analysis results
            failed_files: List of files that failed analysis
        """
        # Store the data
        self.results = results
        self.failed_files = failed_files or []
        
        # Clear existing data
        self._clear_display()
        
        # Update the treeview with results
        if not results.empty:
            for _, row in results.iterrows():
                file_path = row.get('file_path', '')
                age = row.get('age', 'N/A')
                gender = row.get('gender', 'N/A')
                emotion = row.get('dominant_emotion', 'N/A').capitalize()
                race = row.get('dominant_race', 'N/A').capitalize()
                
                file_name = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1] if '\\' in file_path else file_path
                
                self.results_tree.insert(
                    "", tk.END, 
                    values=(file_name, age, gender, emotion, race),
                    tags=("result",)
                )
                
        # Update failed files list
        for file_path in self.failed_files:
            file_name = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1] if '\\' in file_path else file_path
            self.failed_list.insert(tk.END, file_name)
            
        # Update summary statistics
        self._update_summary()
        
        # Set tab text with counts
        success_count = len(results) if not results.empty else 0
        failed_count = len(self.failed_files)
        
        self.notebook.tab(0, text=f"Results ({success_count})")
        self.notebook.tab(1, text=f"Failed Files ({failed_count})")
        
    def _clear_display(self):
        """
        Clear all displayed data.
        """
        # Clear treeview
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        # Clear failed files list
        self.failed_list.delete(0, tk.END)
        
    def _update_summary(self):
        """
        Update the summary statistics display.
        """
        success_count = len(self.results) if not self.results.empty else 0
        failed_count = len(self.failed_files)
        total_count = success_count + failed_count
        
        # Update count values
        self.total_value.config(text=str(total_count))
        self.success_value.config(text=str(success_count))
        self.failed_value.config(text=str(failed_count))
        
        # Calculate age statistics
        if not self.results.empty and 'age' in self.results.columns:
            try:
                avg_age = self.results['age'].mean()
                min_age = self.results['age'].min()
                max_age = self.results['age'].max()
                
                self.age_avg_value.config(text=f"{avg_age:.1f}")
                self.age_min_value.config(text=str(min_age))
                self.age_max_value.config(text=str(max_age))
            except:
                # Handle non-numeric age values
                self.age_avg_value.config(text="-")
                self.age_min_value.config(text="-")
                self.age_max_value.config(text="-")
        else:
            self.age_avg_value.config(text="-")
            self.age_min_value.config(text="-")
            self.age_max_value.config(text="-")
            
        # Calculate gender statistics
        if not self.results.empty and 'gender' in self.results.columns:
            try:
                gender_counts = self.results['gender'].value_counts()
                
                men_count = gender_counts.get('Man', 0)
                women_count = gender_counts.get('Woman', 0)
                
                men_pct = (men_count / success_count) * 100 if success_count > 0 else 0
                women_pct = (women_count / success_count) * 100 if success_count > 0 else 0
                
                self.men_value.config(text=f"{men_count} ({men_pct:.1f}%)")
                self.women_value.config(text=f"{women_count} ({women_pct:.1f}%)")
            except:
                self.men_value.config(text="0 (0%)")
                self.women_value.config(text="0 (0%)")
        else:
            self.men_value.config(text="0 (0%)")
            self.women_value.config(text="0 (0%)")
            
    def _apply_filters(self):
        """
        Apply filters to the results.
        """
        if self.results is None or self.results.empty:
            return
            
        # Get filter values
        age_min = self.age_min_var.get().strip()
        age_max = self.age_max_var.get().strip()
        gender = self.gender_var.get()
        emotion = self.emotion_var.get()
        
        # Create a copy of the results
        filtered_results = self.results.copy()
        
        # Apply age filter
        if age_min and age_min.isdigit():
            filtered_results = filtered_results[filtered_results['age'] >= int(age_min)]
            
        if age_max and age_max.isdigit():
            filtered_results = filtered_results[filtered_results['age'] <= int(age_max)]
            
        # Apply gender filter
        if gender != "All":
            filtered_results = filtered_results[filtered_results['gender'] == gender]
            
        # Apply emotion filter
        if emotion != "All":
            filtered_results = filtered_results[filtered_results['dominant_emotion'].str.lower() == emotion.lower()]
            
        # Clear and update the treeview
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        for _, row in filtered_results.iterrows():
            file_path = row.get('file_path', '')
            age = row.get('age', 'N/A')
            gender = row.get('gender', 'N/A')
            emotion = row.get('dominant_emotion', 'N/A').capitalize()
            race = row.get('dominant_race', 'N/A').capitalize()
            
            file_name = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1] if '\\' in file_path else file_path
            
            self.results_tree.insert(
                "", tk.END, 
                values=(file_name, age, gender, emotion, race),
                tags=("result",)
            )
            
        # Update the results tab text
        self.notebook.tab(0, text=f"Results ({len(filtered_results)})")
        
    def _reset_filters(self):
        """
        Reset all filters and show all results.
        """
        # Clear filter values
        self.age_min_var.set("")
        self.age_max_var.set("")
        self.gender_var.set("All")
        self.emotion_var.set("All")
        
        # Refresh the display with all results
        self._clear_display()
        
        if not self.results.empty:
            for _, row in self.results.iterrows():
                file_path = row.get('file_path', '')
                age = row.get('age', 'N/A')
                gender = row.get('gender', 'N/A')
                emotion = row.get('dominant_emotion', 'N/A').capitalize()
                race = row.get('dominant_race', 'N/A').capitalize()
                
                file_name = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1] if '\\' in file_path else file_path
                
                self.results_tree.insert(
                    "", tk.END, 
                    values=(file_name, age, gender, emotion, race),
                    tags=("result",)
                )
                
            # Update failed files list
            for file_path in self.failed_files:
                file_name = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1] if '\\' in file_path else file_path
                self.failed_list.insert(tk.END, file_name)
                
            # Reset tab text
            self.notebook.tab(0, text=f"Results ({len(self.results)})")
            
    def _view_selected_details(self):
        """
        View detailed results for the selected item.
        """
        selected_items = self.results_tree.selection()
        
        if not selected_items:
            self.main_window.show_error(
                "No Selection", 
                "Please select a result to view details."
            )
            return
            
        # Get the selected item index
        selected_item = selected_items[0]
        values = self.results_tree.item(selected_item, 'values')
        file_name = values[0]
        
        # Find the corresponding data in the results DataFrame
        result_data = None
        for _, row in self.results.iterrows():
            path = row.get('file_path', '')
            if path.endswith(file_name):
                result_data = row.to_dict()
                break
                
        if not result_data:
            self.main_window.show_error(
                "Data Error", 
                "Could not find the corresponding result data."
            )
            return
            
        # Create a details window
        self._show_details_window(result_data)
        
    def _show_details_window(self, result_data):
        """
        Show a window with detailed result information.
        
        Args:
            result_data: The result data dictionary
        """
        details_window = tk.Toplevel(self)
        details_window.title("Result Details")
        details_window.geometry("700x500")
        details_window.grab_set()  # Make window modal
        
        # Create a text widget to display the results
        text_frame = ttk.Frame(details_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, padx=5, pady=5)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Format and insert the results
        text_widget.insert(tk.END, json.dumps(result_data, indent=4))
        text_widget.config(state=tk.DISABLED)  # Make read-only
        
        # Add a close button
        close_btn = ttk.Button(
            details_window, 
            text="Close", 
            command=details_window.destroy
        )
        close_btn.pack(pady=(0, 10))
