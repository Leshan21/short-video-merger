"""
Main window for the Short Video Merger GUI application.

Provides the primary user interface for video merging operations.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from typing import Optional, List
from pathlib import Path

from src.gui.styles import apply_theme, PADDING
from src.gui.widgets import (
    FolderSelector,
    FileSelector,
    VideoList,
    ProgressPanel,
    LogPanel
)
from src.core.config import (
    MergeConfig,
    OUTPUT_FORMATS,
    TRANSITION_EFFECTS,
    RESOLUTION_OPTIONS,
    get_default_output_path
)
from src.core.file_handler import FileHandler, VideoInfo
from src.core.video_processor import VideoProcessor, MergeResult
from src.utils.logger import ProgressCallback


class MainWindow:
    """Main application window for the Short Video Merger."""
    
    def __init__(self, root: Optional[tk.Tk] = None):
        """
        Initialize the main window.
        
        Args:
            root: Optional existing Tk root window.
        """
        # Create root window if not provided
        if root is None:
            self.root = tk.Tk()
        else:
            self.root = root
        
        self.root.title("Short Video Merger")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Apply theme
        apply_theme(self.root, 'light')
        
        # Initialize components
        self._file_handler = FileHandler()
        self._video_processor = VideoProcessor()
        self._merge_thread: Optional[threading.Thread] = None
        self._is_merging = False
        
        # Configuration
        self._config = MergeConfig()
        
        # Build UI
        self._create_menu()
        self._create_main_layout()
        
        # Set protocol for window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_menu(self) -> None:
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Folder...", command=self._browse_folder)
        file_menu.add_command(label="Save Configuration...", command=self._save_config)
        file_menu.add_command(label="Load Configuration...", command=self._load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_close)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Select All Videos", command=self._select_all)
        edit_menu.add_command(label="Deselect All Videos", command=self._deselect_all)
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences", command=self._show_preferences)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self._show_docs)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_main_layout(self) -> None:
        """Create the main window layout."""
        # Main container
        main_frame = ttk.Frame(self.root, padding=PADDING['large'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top section - Folder selection
        self._create_folder_section(main_frame)
        
        # Middle section - Video list and configuration
        self._create_content_section(main_frame)
        
        # Bottom section - Progress and controls
        self._create_control_section(main_frame)
    
    def _create_folder_section(self, parent: ttk.Frame) -> None:
        """Create the folder selection section."""
        folder_frame = ttk.LabelFrame(parent, text="Input Folder", padding=PADDING['medium'])
        folder_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))
        
        # Folder selector
        self._folder_selector = FolderSelector(
            folder_frame,
            label="Video Folder:",
            on_change=self._on_folder_change
        )
        self._folder_selector.pack(fill=tk.X, pady=(0, PADDING['small']))
        
        # Info row
        info_frame = ttk.Frame(folder_frame)
        info_frame.pack(fill=tk.X)
        
        self._video_count_var = tk.StringVar(value="No videos found")
        ttk.Label(
            info_frame,
            textvariable=self._video_count_var,
            style='Small.TLabel'
        ).pack(side=tk.LEFT)
        
        # Scan button
        self._scan_btn = ttk.Button(
            info_frame,
            text="Scan Folder",
            command=self._scan_folder
        )
        self._scan_btn.pack(side=tk.RIGHT)
    
    def _create_content_section(self, parent: ttk.Frame) -> None:
        """Create the main content section with video list and configuration."""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, PADDING['medium']))
        
        # Left side - Video list
        list_frame = ttk.LabelFrame(content_frame, text="Videos", padding=PADDING['medium'])
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, PADDING['medium']))
        
        self._video_list = VideoList(list_frame)
        self._video_list.pack(fill=tk.BOTH, expand=True)
        
        # Right side - Configuration
        config_frame = ttk.LabelFrame(content_frame, text="Configuration", padding=PADDING['medium'])
        config_frame.pack(side=tk.RIGHT, fill=tk.Y, ipadx=PADDING['medium'])
        
        self._create_config_panel(config_frame)
    
    def _create_config_panel(self, parent: ttk.Frame) -> None:
        """Create the configuration panel."""
        # Video count
        count_frame = ttk.Frame(parent)
        count_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))
        
        ttk.Label(count_frame, text="Videos to merge:").pack(side=tk.LEFT)
        self._count_var = tk.IntVar(value=0)
        self._count_spin = ttk.Spinbox(
            count_frame,
            from_=0,
            to=100,
            textvariable=self._count_var,
            width=8
        )
        self._count_spin.pack(side=tk.RIGHT)
        ttk.Label(count_frame, text="(0 = all)", style='Small.TLabel').pack(side=tk.RIGHT, padx=5)
        
        # Output file
        output_frame = ttk.Frame(parent)
        output_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))
        
        ttk.Label(output_frame, text="Output file:").pack(anchor=tk.W)
        self._output_selector = FileSelector(
            output_frame,
            label="",
            on_change=self._on_output_change
        )
        self._output_selector.pack(fill=tk.X)
        
        # Output format
        format_frame = ttk.Frame(parent)
        format_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))
        
        ttk.Label(format_frame, text="Output format:").pack(side=tk.LEFT)
        self._format_var = tk.StringVar(value='mp4')
        self._format_combo = ttk.Combobox(
            format_frame,
            textvariable=self._format_var,
            values=OUTPUT_FORMATS,
            state='readonly',
            width=10
        )
        self._format_combo.pack(side=tk.RIGHT)
        
        # Transition
        trans_frame = ttk.Frame(parent)
        trans_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))
        
        ttk.Label(trans_frame, text="Transition:").pack(side=tk.LEFT)
        self._transition_var = tk.StringVar(value='none')
        self._transition_combo = ttk.Combobox(
            trans_frame,
            textvariable=self._transition_var,
            values=TRANSITION_EFFECTS,
            state='readonly',
            width=10
        )
        self._transition_combo.pack(side=tk.RIGHT)
        
        # Transition duration
        dur_frame = ttk.Frame(parent)
        dur_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))
        
        ttk.Label(dur_frame, text="Transition duration:").pack(side=tk.LEFT)
        self._duration_var = tk.DoubleVar(value=1.0)
        self._duration_scale = ttk.Scale(
            dur_frame,
            from_=0,
            to=3,
            variable=self._duration_var,
            orient=tk.HORIZONTAL,
            length=100
        )
        self._duration_scale.pack(side=tk.RIGHT)
        self._duration_label = ttk.Label(dur_frame, text="1.0s", width=5)
        self._duration_label.pack(side=tk.RIGHT)
        self._duration_var.trace_add('write', self._update_duration_label)
        
        # Resolution mode
        res_frame = ttk.Frame(parent)
        res_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))
        
        ttk.Label(res_frame, text="Resolution:").pack(side=tk.LEFT)
        self._resolution_var = tk.StringVar(value='keep')
        self._resolution_combo = ttk.Combobox(
            res_frame,
            textvariable=self._resolution_var,
            values=RESOLUTION_OPTIONS,
            state='readonly',
            width=10
        )
        self._resolution_combo.pack(side=tk.RIGHT)
        
        # Audio normalization
        self._normalize_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            parent,
            text="Normalize audio",
            variable=self._normalize_var
        ).pack(anchor=tk.W, pady=(0, PADDING['medium']))
        
        # Random seed
        seed_frame = ttk.Frame(parent)
        seed_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))
        
        ttk.Label(seed_frame, text="Random seed:").pack(side=tk.LEFT)
        self._seed_var = tk.StringVar(value="")
        self._seed_entry = ttk.Entry(seed_frame, textvariable=self._seed_var, width=12)
        self._seed_entry.pack(side=tk.RIGHT)
        
        # Randomize button
        self._randomize_btn = ttk.Button(
            parent,
            text="🎲 Randomize Selection",
            command=self._randomize_selection
        )
        self._randomize_btn.pack(fill=tk.X, pady=(PADDING['medium'], 0))
    
    def _create_control_section(self, parent: ttk.Frame) -> None:
        """Create the control section with progress and buttons."""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X)
        
        # Progress panel
        progress_frame = ttk.LabelFrame(control_frame, text="Progress", padding=PADDING['medium'])
        progress_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))
        
        self._progress_panel = ProgressPanel(progress_frame)
        self._progress_panel.pack(fill=tk.X)
        
        # Log panel
        log_frame = ttk.LabelFrame(control_frame, text="Log", padding=PADDING['medium'])
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, PADDING['medium']))
        
        self._log_panel = LogPanel(log_frame, height=5)
        self._log_panel.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self._clear_btn = ttk.Button(
            button_frame,
            text="Clear",
            command=self._clear_all
        )
        self._clear_btn.pack(side=tk.LEFT, padx=(0, PADDING['small']))
        
        self._cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._cancel_merge,
            state=tk.DISABLED
        )
        self._cancel_btn.pack(side=tk.LEFT)
        
        self._merge_btn = ttk.Button(
            button_frame,
            text="▶ Start Merge",
            style='Accent.TButton',
            command=self._start_merge
        )
        self._merge_btn.pack(side=tk.RIGHT)
    
    def _on_folder_change(self, path: str) -> None:
        """Handle folder path change."""
        if path and Path(path).is_dir():
            self._file_handler.set_folder(path)
    
    def _on_output_change(self, path: str) -> None:
        """Handle output path change."""
        pass  # Just update the path
    
    def _update_duration_label(self, *args) -> None:
        """Update the duration label with current value."""
        value = self._duration_var.get()
        self._duration_label.config(text=f"{value:.1f}s")
    
    def _browse_folder(self) -> None:
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(title="Select Video Folder")
        if folder:
            self._folder_selector.path = folder
            self._scan_folder()
    
    def _scan_folder(self) -> None:
        """Scan the selected folder for videos."""
        folder_path = self._folder_selector.path
        
        if not folder_path:
            messagebox.showwarning("Warning", "Please select a folder first.")
            return
        
        if not Path(folder_path).is_dir():
            messagebox.showerror("Error", f"Folder does not exist: {folder_path}")
            return
        
        self._log_panel.log(f"Scanning folder: {folder_path}")
        
        # Scan for videos
        self._file_handler.set_folder(folder_path)
        videos = self._file_handler.scan_folder()
        
        # Update video list
        self._video_list.set_videos(videos)
        
        # Update count label
        count = len(videos)
        self._video_count_var.set(f"Found {count} video{'s' if count != 1 else ''}")
        
        self._log_panel.log(f"Found {count} video files", 'success' if count > 0 else 'warning')
        
        # Set default output path if not set
        if not self._output_selector.path:
            default_path = get_default_output_path()
            self._output_selector.path = default_path
    
    def _randomize_selection(self) -> None:
        """Randomize video selection."""
        videos = self._file_handler.videos
        if not videos:
            messagebox.showwarning("Warning", "No videos to randomize. Scan a folder first.")
            return
        
        count = self._count_var.get()
        seed_str = self._seed_var.get()
        seed = int(seed_str) if seed_str.isdigit() else None
        
        # Get random selection
        selected = self._file_handler.get_random_selection(count, seed)
        
        # Highlight selected videos
        selected_names = [v.filename for v in selected]
        self._video_list.highlight_videos(selected_names)
        self._video_list.select_videos(selected_names)
        
        self._log_panel.log(f"Randomly selected {len(selected)} videos")
    
    def _start_merge(self) -> None:
        """Start the merge operation."""
        # Validate inputs
        folder_path = self._folder_selector.path
        output_path = self._output_selector.path
        
        if not folder_path:
            messagebox.showerror("Error", "Please select an input folder.")
            return
        
        if not output_path:
            messagebox.showerror("Error", "Please specify an output file.")
            return
        
        videos = self._file_handler.videos
        if not videos:
            messagebox.showerror("Error", "No videos found. Scan the folder first.")
            return
        
        # Get selected videos
        selected_names = self._video_list.get_selected_filenames()
        if selected_names:
            selected = [v for v in videos if v.filename in selected_names]
        else:
            count = self._count_var.get()
            seed_str = self._seed_var.get()
            seed = int(seed_str) if seed_str.isdigit() else None
            selected = self._file_handler.get_random_selection(count, seed)
        
        if not selected:
            messagebox.showerror("Error", "No videos selected for merging.")
            return
        
        # Build configuration
        self._config = MergeConfig(
            input_folder=folder_path,
            output_path=output_path,
            video_count=len(selected),
            output_format=self._format_var.get(),
            transition=self._transition_var.get(),
            transition_duration=self._duration_var.get(),
            resolution_mode=self._resolution_var.get(),
            normalize_audio=self._normalize_var.get(),
            random_seed=int(self._seed_var.get()) if self._seed_var.get().isdigit() else None
        )
        
        # Start merge in background thread
        self._is_merging = True
        self._merge_btn.config(state=tk.DISABLED)
        self._cancel_btn.config(state=tk.NORMAL)
        self._progress_panel.reset()
        
        self._log_panel.log(f"Starting merge of {len(selected)} videos...")
        
        # Create progress callback
        progress = ProgressCallback(callback=self._update_progress)
        
        # Start merge thread
        self._merge_thread = threading.Thread(
            target=self._do_merge,
            args=(selected, self._config, progress),
            daemon=True
        )
        self._merge_thread.start()
        
        # Start progress polling
        self._poll_progress()
    
    def _do_merge(
        self,
        videos: List[VideoInfo],
        config: MergeConfig,
        progress: ProgressCallback
    ) -> None:
        """
        Execute the merge operation in a background thread.
        
        Args:
            videos: List of videos to merge.
            config: Merge configuration.
            progress: Progress callback.
        """
        try:
            result = self._video_processor.merge_videos(videos, config, progress)
            
            # Schedule result handling on main thread
            self.root.after(0, lambda: self._on_merge_complete(result))
            
        except Exception as e:
            result = MergeResult(success=False, error_message=str(e))
            self.root.after(0, lambda: self._on_merge_complete(result))
    
    def _update_progress(self, progress: float, message: str) -> None:
        """
        Update progress from background thread.
        
        Args:
            progress: Progress value 0-1.
            message: Status message.
        """
        # Schedule update on main thread
        self.root.after(0, lambda: self._progress_panel.update_progress(progress, message))
    
    def _poll_progress(self) -> None:
        """Poll for merge completion."""
        if self._merge_thread and self._merge_thread.is_alive():
            self.root.after(100, self._poll_progress)
    
    def _on_merge_complete(self, result: MergeResult) -> None:
        """
        Handle merge completion.
        
        Args:
            result: The merge result.
        """
        self._is_merging = False
        self._merge_btn.config(state=tk.NORMAL)
        self._cancel_btn.config(state=tk.DISABLED)
        
        if result.success:
            self._progress_panel.update_progress(1.0, "Complete!")
            self._log_panel.log(f"Merge completed successfully!", 'success')
            self._log_panel.log(f"Output: {result.output_path}", 'success')
            if result.duration:
                self._log_panel.log(f"Duration: {result.duration:.1f}s")
            if result.processing_time:
                self._log_panel.log(f"Processing time: {result.processing_time:.1f}s")
            
            for warning in result.warnings:
                self._log_panel.log(f"Warning: {warning}", 'warning')
            
            messagebox.showinfo(
                "Success",
                f"Video merge completed!\n\nOutput: {result.output_path}"
            )
        else:
            self._progress_panel.set_status("Failed")
            self._log_panel.log(f"Merge failed: {result.error_message}", 'error')
            
            for warning in result.warnings:
                self._log_panel.log(f"Warning: {warning}", 'warning')
            
            messagebox.showerror("Error", f"Merge failed:\n{result.error_message}")
    
    def _cancel_merge(self) -> None:
        """Cancel the current merge operation."""
        if self._is_merging:
            self._video_processor.cancel()
            self._log_panel.log("Cancelling merge operation...", 'warning')
    
    def _clear_all(self) -> None:
        """Clear all fields and reset the application."""
        self._folder_selector.path = ""
        self._output_selector.path = ""
        self._video_list.clear()
        self._video_count_var.set("No videos found")
        self._count_var.set(0)
        self._format_var.set('mp4')
        self._transition_var.set('none')
        self._duration_var.set(1.0)
        self._resolution_var.set('keep')
        self._normalize_var.set(False)
        self._seed_var.set("")
        self._progress_panel.reset()
        self._log_panel.clear()
        self._file_handler = FileHandler()
    
    def _select_all(self) -> None:
        """Select all videos."""
        videos = self._file_handler.videos
        self._video_list.select_videos([v.filename for v in videos])
    
    def _deselect_all(self) -> None:
        """Deselect all videos."""
        self._video_list.select_videos([])
    
    def _save_config(self) -> None:
        """Save current configuration to a file."""
        file_path = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                config = MergeConfig(
                    input_folder=self._folder_selector.path,
                    output_path=self._output_selector.path,
                    video_count=self._count_var.get(),
                    output_format=self._format_var.get(),
                    transition=self._transition_var.get(),
                    transition_duration=self._duration_var.get(),
                    resolution_mode=self._resolution_var.get(),
                    normalize_audio=self._normalize_var.get(),
                    random_seed=int(self._seed_var.get()) if self._seed_var.get().isdigit() else None
                )
                config.save(file_path)
                self._log_panel.log(f"Configuration saved to {file_path}", 'success')
            except Exception as e:
                messagebox.showerror("Error", f"Could not save configuration: {e}")
    
    def _load_config(self) -> None:
        """Load configuration from a file."""
        file_path = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            try:
                config = MergeConfig.load(file_path)
                
                # Apply configuration
                self._folder_selector.path = config.input_folder
                self._output_selector.path = config.output_path
                self._count_var.set(config.video_count)
                self._format_var.set(config.output_format)
                self._transition_var.set(config.transition)
                self._duration_var.set(config.transition_duration)
                self._resolution_var.set(config.resolution_mode)
                self._normalize_var.set(config.normalize_audio)
                self._seed_var.set(str(config.random_seed) if config.random_seed else "")
                
                self._log_panel.log(f"Configuration loaded from {file_path}", 'success')
                
                # Scan folder if set
                if config.input_folder and Path(config.input_folder).is_dir():
                    self._scan_folder()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Could not load configuration: {e}")
    
    def _show_preferences(self) -> None:
        """Show preferences dialog."""
        messagebox.showinfo("Preferences", "Preferences dialog coming soon!")
    
    def _show_docs(self) -> None:
        """Show documentation."""
        messagebox.showinfo(
            "Documentation",
            "Short Video Merger\n\n"
            "1. Select a folder containing video files\n"
            "2. Click 'Scan Folder' to find videos\n"
            "3. Configure merge settings\n"
            "4. Click 'Start Merge' to begin\n\n"
            "For more information, see the README.md file."
        )
    
    def _show_about(self) -> None:
        """Show about dialog."""
        messagebox.showinfo(
            "About",
            "Short Video Merger v1.0.0\n\n"
            "A Python-based application for merging\n"
            "short videos with GUI and CLI support.\n\n"
            "Built with tkinter and moviepy."
        )
    
    def _on_close(self) -> None:
        """Handle window close event."""
        if self._is_merging:
            if messagebox.askyesno("Confirm", "A merge is in progress. Cancel and exit?"):
                self._video_processor.cancel()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self) -> None:
        """Start the main event loop."""
        self.root.mainloop()


def launch_gui() -> None:
    """Launch the GUI application."""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    launch_gui()
