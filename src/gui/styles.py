"""
GUI styling and theme configuration for the Short Video Merger application.

Provides consistent styling for tkinter widgets.
"""

import tkinter as tk
from tkinter import ttk


# Color schemes
COLORS = {
    'light': {
        'bg': '#f0f0f0',
        'fg': '#333333',
        'accent': '#4a90d9',
        'accent_hover': '#357abd',
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'button_bg': '#e0e0e0',
        'entry_bg': '#ffffff',
        'border': '#cccccc',
        'highlight': '#e8f4fd',
    },
    'dark': {
        'bg': '#2d2d2d',
        'fg': '#e0e0e0',
        'accent': '#4a90d9',
        'accent_hover': '#5ba0e9',
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'button_bg': '#404040',
        'entry_bg': '#3d3d3d',
        'border': '#555555',
        'highlight': '#3a4d5c',
    }
}

# Font configurations
FONTS = {
    'default': ('Helvetica', 10),
    'title': ('Helvetica', 14, 'bold'),
    'heading': ('Helvetica', 12, 'bold'),
    'small': ('Helvetica', 9),
    'monospace': ('Courier', 10),
}

# Padding and spacing
PADDING = {
    'small': 2,
    'medium': 5,
    'large': 10,
    'xlarge': 15,
}


def apply_theme(root: tk.Tk, theme: str = 'light') -> None:
    """
    Apply a theme to the application.
    
    Args:
        root: The root Tk window.
        theme: Theme name ('light' or 'dark').
    """
    colors = COLORS.get(theme, COLORS['light'])
    
    style = ttk.Style(root)
    
    # Try to use a modern theme as base
    available_themes = style.theme_names()
    if 'clam' in available_themes:
        style.theme_use('clam')
    elif 'default' in available_themes:
        style.theme_use('default')
    
    # Configure common styles
    style.configure(
        '.',
        background=colors['bg'],
        foreground=colors['fg'],
        font=FONTS['default']
    )
    
    # Frame styles
    style.configure(
        'TFrame',
        background=colors['bg']
    )
    
    style.configure(
        'Card.TFrame',
        background=colors['bg'],
        relief='raised',
        borderwidth=1
    )
    
    # Label styles
    style.configure(
        'TLabel',
        background=colors['bg'],
        foreground=colors['fg'],
        font=FONTS['default']
    )
    
    style.configure(
        'Title.TLabel',
        font=FONTS['title']
    )
    
    style.configure(
        'Heading.TLabel',
        font=FONTS['heading']
    )
    
    style.configure(
        'Small.TLabel',
        font=FONTS['small']
    )
    
    style.configure(
        'Success.TLabel',
        foreground=colors['success']
    )
    
    style.configure(
        'Error.TLabel',
        foreground=colors['error']
    )
    
    # Button styles
    style.configure(
        'TButton',
        background=colors['button_bg'],
        foreground=colors['fg'],
        font=FONTS['default'],
        padding=(10, 5)
    )
    
    style.map(
        'TButton',
        background=[('active', colors['accent_hover']), ('pressed', colors['accent'])]
    )
    
    style.configure(
        'Accent.TButton',
        background=colors['accent'],
        foreground='white'
    )
    
    style.map(
        'Accent.TButton',
        background=[('active', colors['accent_hover']), ('pressed', colors['accent'])]
    )
    
    # Entry styles
    style.configure(
        'TEntry',
        fieldbackground=colors['entry_bg'],
        foreground=colors['fg']
    )
    
    # Combobox styles
    style.configure(
        'TCombobox',
        fieldbackground=colors['entry_bg'],
        foreground=colors['fg']
    )
    
    # Progressbar styles
    style.configure(
        'TProgressbar',
        background=colors['accent'],
        troughcolor=colors['button_bg']
    )
    
    # Treeview styles (for video list)
    style.configure(
        'Treeview',
        background=colors['entry_bg'],
        foreground=colors['fg'],
        fieldbackground=colors['entry_bg'],
        font=FONTS['default']
    )
    
    style.configure(
        'Treeview.Heading',
        background=colors['button_bg'],
        foreground=colors['fg'],
        font=FONTS['default']
    )
    
    style.map(
        'Treeview',
        background=[('selected', colors['accent'])],
        foreground=[('selected', 'white')]
    )
    
    # LabelFrame styles
    style.configure(
        'TLabelframe',
        background=colors['bg']
    )
    
    style.configure(
        'TLabelframe.Label',
        background=colors['bg'],
        foreground=colors['fg'],
        font=FONTS['heading']
    )
    
    # Checkbutton styles
    style.configure(
        'TCheckbutton',
        background=colors['bg'],
        foreground=colors['fg']
    )
    
    # Scale (slider) styles
    style.configure(
        'TScale',
        background=colors['bg']
    )
    
    # Spinbox styles
    style.configure(
        'TSpinbox',
        fieldbackground=colors['entry_bg'],
        foreground=colors['fg']
    )


def get_icon_path(icon_name: str) -> str:
    """
    Get the path to an icon file.
    
    Args:
        icon_name: Name of the icon.
        
    Returns:
        Path to the icon file or empty string if not found.
    """
    # Icon paths would be defined here if using custom icons
    return ""
