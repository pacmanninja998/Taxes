import tkinter as tk
from tkinter import ttk

class ToggleSwitch(ttk.Frame):
    """Text-based toggle widget that displays "Completed" checkbox or checkmark"""
    def __init__(self, parent, command=None, initial_state=False, **kwargs):
        """Initialize text toggle
        
        Args:
            parent: Parent widget
            command: Function to call when toggled
            initial_state: Initial state (True=checked, False=unchecked)
        """
        super().__init__(parent, **kwargs)
        
        self.command = command
        self.is_checked = initial_state
        
        # Size settings
        self.width = 100
        self.height = 24
        
        # Create a frame for the toggle
        self.inner_frame = ttk.Frame(self)
        self.inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the checkbox/checkmark and text
        self.checkmark = ttk.Label(self.inner_frame, text="", width=2)
        self.checkmark.pack(side=tk.LEFT, padx=(0, 5))
        
        self.label = ttk.Label(self.inner_frame, text="Completed")
        self.label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Bind click events
        self.checkmark.bind("<Button-1>", self.toggle)
        self.label.bind("<Button-1>", self.toggle)
        self.inner_frame.bind("<Button-1>", self.toggle)
        
        # Draw initial state
        self.update_display()
    
    def update_display(self):
        """Update the display based on current state"""
        # Get theme colors from root window
        bg_color, fg_color = self._get_theme_colors()
        
        if self.is_checked:
            self.checkmark.config(text="✓", foreground=fg_color)
        else:
            self.checkmark.config(text="□", foreground=fg_color)
            
        # Configure background to match parent
        self.inner_frame.configure(style="")
        self.checkmark.configure(style="")
        self.label.configure(style="")
    
    def _get_theme_colors(self):
        """Get colors from current theme"""
        # Default colors
        bg_color = "#ffffff"
        fg_color = "#000000"
        
        # Try to get colors from root window's theme data
        try:
            root = self.winfo_toplevel()
            if hasattr(root, 'theme_data'):
                theme_data = root.theme_data
                bg_color = theme_data.get("entry_bg", bg_color)
                fg_color = theme_data.get("accent", fg_color) if self.is_checked else theme_data.get("foreground", fg_color)
        except (AttributeError, KeyError):
            pass
            
        return bg_color, fg_color
    
    def toggle(self, event=None):
        """Toggle the checkbox state"""
        self.is_checked = not self.is_checked
        self.update_display()
        
        if self.command:
            self.command()
        
        return "break"  # Prevent event propagation
    
    def set(self, state):
        """Set the checkbox state without triggering command"""
        if self.is_checked != bool(state):
            self.is_checked = bool(state)
            self.update_display()
    
    def get(self):
        """Get the current state"""
        return self.is_checked