"""
Custom widgets for the Short Video Merger GUI.

Provides reusable widget components for the main window.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Callable, Optional, List
from pathlib import Path


class FolderSelector(ttk.Frame):
    """Widget for selecting a folder with browse button."""
    
    def __init__(
        self,
        parent,
        label: str = "Folder:",
        on_change: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """
        Initialize the folder selector.
        
        Args:
            parent: Parent widget.
            label: Label text.
            on_change: Callback when folder changes.
        """
        super().__init__(parent, **kwargs)
        
        self._on_change = on_change
        self._path_var = tk.StringVar()
        
        # Label
        ttk.Label(self, text=label).pack(side=tk.LEFT, padx=(0, 5))
        
        # Entry field
        self._entry = ttk.Entry(self, textvariable=self._path_var, width=50)
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Browse button
        self._browse_btn = ttk.Button(self, text="Browse...", command=self._browse)
        self._browse_btn.pack(side=tk.LEFT)
        
        # Bind change event
        self._path_var.trace_add('write', self._on_path_change)
    
    def _browse(self) -> None:
        """Open folder browser dialog."""
        folder = filedialog.askdirectory(
            title="Select Video Folder",
            initialdir=self._path_var.get() or str(Path.home())
        )
        if folder:
            self._path_var.set(folder)
    
    def _on_path_change(self, *args) -> None:
        """Handle path change event."""
        if self._on_change:
            self._on_change(self._path_var.get())
    
    @property
    def path(self) -> str:
        """Get the current folder path."""
        return self._path_var.get()
    
    @path.setter
    def path(self, value: str) -> None:
        """Set the folder path."""
        self._path_var.set(value)


class FileSelector(ttk.Frame):
    """Widget for selecting an output file with browse button."""
    
    def __init__(
        self,
        parent,
        label: str = "Output File:",
        filetypes: Optional[List[tuple]] = None,
        default_extension: str = ".mp4",
        on_change: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        """
        Initialize the file selector.
        
        Args:
            parent: Parent widget.
            label: Label text.
            filetypes: List of (description, extension) tuples.
            default_extension: Default file extension.
            on_change: Callback when file changes.
        """
        super().__init__(parent, **kwargs)
        
        self._on_change = on_change
        self._path_var = tk.StringVar()
        self._filetypes = filetypes or [
            ("MP4 files", "*.mp4"),
            ("AVI files", "*.avi"),
            ("MOV files", "*.mov"),
            ("MKV files", "*.mkv"),
            ("All files", "*.*")
        ]
        self._default_extension = default_extension
        
        # Label
        ttk.Label(self, text=label).pack(side=tk.LEFT, padx=(0, 5))
        
        # Entry field
        self._entry = ttk.Entry(self, textvariable=self._path_var, width=50)
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Browse button
        self._browse_btn = ttk.Button(self, text="Browse...", command=self._browse)
        self._browse_btn.pack(side=tk.LEFT)
        
        # Bind change event
        self._path_var.trace_add('write', self._on_path_change)
    
    def _browse(self) -> None:
        """Open file save dialog."""
        file_path = filedialog.asksaveasfilename(
            title="Save Merged Video As",
            defaultextension=self._default_extension,
            filetypes=self._filetypes,
            initialdir=str(Path.home() / "Videos")
        )
        if file_path:
            self._path_var.set(file_path)
    
    def _on_path_change(self, *args) -> None:
        """Handle path change event."""
        if self._on_change:
            self._on_change(self._path_var.get())
    
    @property
    def path(self) -> str:
        """Get the current file path."""
        return self._path_var.get()
    
    @path.setter
    def path(self, value: str) -> None:
        """Set the file path."""
        self._path_var.set(value)


class VideoList(ttk.Frame):
    """Widget for displaying and selecting videos."""
    
    def __init__(
        self,
        parent,
        on_selection_change: Optional[Callable[[List[str]], None]] = None,
        **kwargs
    ):
        """
        Initialize the video list.
        
        Args:
            parent: Parent widget.
            on_selection_change: Callback when selection changes.
        """
        super().__init__(parent, **kwargs)
        
        self._on_selection_change = on_selection_change
        self._videos = {}  # filename -> (VideoInfo, selected)
        
        # Create treeview
        columns = ('name', 'duration', 'resolution', 'size')
        self._tree = ttk.Treeview(
            self,
            columns=columns,
            show='headings',
            selectmode='extended'
        )
        
        # Configure columns
        self._tree.heading('name', text='Name', anchor=tk.W)
        self._tree.heading('duration', text='Duration', anchor=tk.CENTER)
        self._tree.heading('resolution', text='Resolution', anchor=tk.CENTER)
        self._tree.heading('size', text='Size', anchor=tk.E)
        
        self._tree.column('name', width=300, minwidth=150)
        self._tree.column('duration', width=80, minwidth=60)
        self._tree.column('resolution', width=100, minwidth=80)
        self._tree.column('size', width=80, minwidth=60)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        x_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._tree.xview)
        self._tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Pack widgets
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self._tree.bind('<<TreeviewSelect>>', self._on_select)
    
    def set_videos(self, videos: list) -> None:
        """
        Set the list of videos to display.
        
        Args:
            videos: List of VideoInfo objects.
        """
        # Clear existing items
        for item in self._tree.get_children():
            self._tree.delete(item)
        
        self._videos.clear()
        
        # Add new items
        for video in videos:
            size_str = f"{video.size_mb:.1f} MB"
            
            item_id = self._tree.insert(
                '',
                tk.END,
                values=(
                    video.filename,
                    video.duration_formatted,
                    video.resolution,
                    size_str
                ),
                tags=('enabled' if video.enabled else 'disabled',)
            )
            
            self._videos[video.filename] = (video, item_id)
    
    def get_selected_filenames(self) -> List[str]:
        """Get list of selected video filenames."""
        selected = []
        for item_id in self._tree.selection():
            values = self._tree.item(item_id)['values']
            if values:
                selected.append(values[0])
        return selected
    
    def select_videos(self, filenames: List[str]) -> None:
        """
        Select specific videos by filename.
        
        Args:
            filenames: List of filenames to select.
        """
        # Clear current selection
        self._tree.selection_remove(self._tree.selection())
        
        # Select specified videos
        for filename in filenames:
            if filename in self._videos:
                _, item_id = self._videos[filename]
                self._tree.selection_add(item_id)
    
    def highlight_videos(self, filenames: List[str]) -> None:
        """
        Highlight specific videos (for random selection display).
        
        Args:
            filenames: List of filenames to highlight.
        """
        # Configure tags
        self._tree.tag_configure('highlighted', background='#e8f4fd')
        self._tree.tag_configure('normal', background='')
        
        # Update tags
        for filename, (video, item_id) in self._videos.items():
            if filename in filenames:
                self._tree.item(item_id, tags=('highlighted',))
            else:
                self._tree.item(item_id, tags=('normal',))
    
    def _on_select(self, event) -> None:
        """Handle selection change event."""
        if self._on_selection_change:
            self._on_selection_change(self.get_selected_filenames())
    
    def clear(self) -> None:
        """Clear all videos from the list."""
        for item in self._tree.get_children():
            self._tree.delete(item)
        self._videos.clear()


class ProgressPanel(ttk.Frame):
    """Widget for displaying progress information."""
    
    def __init__(self, parent, **kwargs):
        """
        Initialize the progress panel.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent, **kwargs)
        
        # Status label
        self._status_var = tk.StringVar(value="Ready")
        self._status_label = ttk.Label(
            self,
            textvariable=self._status_var,
            style='Small.TLabel'
        )
        self._status_label.pack(fill=tk.X, pady=(0, 5))
        
        # Progress bar
        self._progress_var = tk.DoubleVar(value=0)
        self._progress_bar = ttk.Progressbar(
            self,
            variable=self._progress_var,
            maximum=100,
            mode='determinate'
        )
        self._progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # Percentage label
        self._percent_var = tk.StringVar(value="0%")
        self._percent_label = ttk.Label(
            self,
            textvariable=self._percent_var,
            style='Small.TLabel'
        )
        self._percent_label.pack(fill=tk.X)
    
    def update_progress(self, progress: float, message: str = "") -> None:
        """
        Update the progress display.
        
        Args:
            progress: Progress value between 0 and 1.
            message: Optional status message.
        """
        percent = int(progress * 100)
        self._progress_var.set(percent)
        self._percent_var.set(f"{percent}%")
        
        if message:
            self._status_var.set(message)
    
    def set_status(self, message: str) -> None:
        """
        Set the status message.
        
        Args:
            message: Status message to display.
        """
        self._status_var.set(message)
    
    def reset(self) -> None:
        """Reset the progress panel to initial state."""
        self._progress_var.set(0)
        self._percent_var.set("0%")
        self._status_var.set("Ready")
    
    def set_indeterminate(self, active: bool) -> None:
        """
        Set the progress bar to indeterminate mode.
        
        Args:
            active: Whether to activate indeterminate mode.
        """
        if active:
            self._progress_bar.configure(mode='indeterminate')
            self._progress_bar.start(10)
        else:
            self._progress_bar.stop()
            self._progress_bar.configure(mode='determinate')


class LogPanel(ttk.Frame):
    """Widget for displaying log messages."""
    
    def __init__(self, parent, height: int = 8, **kwargs):
        """
        Initialize the log panel.
        
        Args:
            parent: Parent widget.
            height: Number of visible text lines.
        """
        super().__init__(parent, **kwargs)
        
        # Text widget with scrollbar
        self._text = tk.Text(
            self,
            height=height,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=('Courier', 9)
        )
        
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._text.yview)
        self._text.configure(yscrollcommand=scrollbar.set)
        
        self._text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure text tags for different log levels
        self._text.tag_configure('info', foreground='black')
        self._text.tag_configure('success', foreground='green')
        self._text.tag_configure('warning', foreground='orange')
        self._text.tag_configure('error', foreground='red')
    
    def log(self, message: str, level: str = 'info') -> None:
        """
        Add a log message.
        
        Args:
            message: Message to log.
            level: Log level ('info', 'success', 'warning', 'error').
        """
        self._text.configure(state=tk.NORMAL)
        self._text.insert(tk.END, message + '\n', level)
        self._text.see(tk.END)
        self._text.configure(state=tk.DISABLED)
    
    def clear(self) -> None:
        """Clear all log messages."""
        self._text.configure(state=tk.NORMAL)
        self._text.delete('1.0', tk.END)
        self._text.configure(state=tk.DISABLED)
