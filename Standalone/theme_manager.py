import tkinter as tk
from tkinter import ttk, colorchooser
import json
from pathlib import Path
import os
import platform

# Get user's Documents folder and create our app directory
USER_DOCS = Path.home() / "Documents" / "Tax Doc Helper"
if not USER_DOCS.exists():
    USER_DOCS.mkdir(parents=True)

# Theme file location
THEME_FILE = USER_DOCS / 'theme_settings.json'

# Default themes
LIGHT_THEME = {
    "background": "#f8f9fa",
    "foreground": "#212529",
    "accent": "#3498db",
    "accent_fg": "#ffffff",
    "header_bg": "#e9ecef",
    "header_fg": "#2c3e50",
    "entry_bg": "#ffffff",
    "entry_fg": "#495057",
    "hover": "#e9ecef",
    "selected": "#007bff",
    "selected_fg": "#ffffff",
    "completed": "#7f8c8d",
    "needed": "#27ae60",
    "date_passed": "#27ae60",  # Green for dates that have passed (received before deadline)
    "error": "#e74c3c",
    "name": "Light"
}

DARK_THEME = {
    "background": "#212529",
    "foreground": "#f8f9fa",
    "accent": "#3498db",
    "accent_fg": "#ffffff",
    "header_bg": "#343a40",
    "header_fg": "#f8f9fa",
    "entry_bg": "#495057",
    "entry_fg": "#e9ecef",
    "hover": "#343a40",
    "selected": "#007bff",
    "selected_fg": "#ffffff",
    "completed": "#7f8c8d",
    "needed": "#2ecc71",
    "date_passed": "#2ecc71",  # Green for dates that have passed (received before deadline)
    "error": "#e74c3c",
    "name": "Dark"
}

def load_theme():
    """Load theme from file or return default light theme"""
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
                print(f"Raw theme data loaded: {list(theme_data.keys())}")
                
                # Validate that all required keys are present
                complete_theme = LIGHT_THEME.copy()  # Start with default values
                
                # Update with loaded values
                for key, value in theme_data.items():
                    complete_theme[key] = value
                
                print(f"Loaded theme: {complete_theme.get('name', 'Custom')}")
                return complete_theme
        except Exception as e:
            print(f"Error loading theme: {e}")
    else:
        print(f"Theme file not found at {THEME_FILE}")
    
    # Return default theme if file doesn't exist or is invalid
    default_theme = LIGHT_THEME.copy()
    save_theme(default_theme)  # Ensure the theme file exists
    return default_theme

def save_theme(theme_data):
    """Save theme to file"""
    try:
        # Ensure directory exists
        if not USER_DOCS.exists():
            USER_DOCS.mkdir(parents=True)
        
        # Make sure the theme has all required keys
        complete_theme = LIGHT_THEME.copy()  # Start with all default values
        
        # Update with provided theme data
        for key, value in theme_data.items():
            complete_theme[key] = value
        
        # Specifically ensure the name is preserved
        if 'name' in theme_data:
            complete_theme['name'] = theme_data['name']
            
        print(f"Saving theme: {complete_theme.get('name', 'Custom')} with keys: {list(complete_theme.keys())}")
            
        # Save to file
        with open(THEME_FILE, 'w', encoding='utf-8') as f:
            json.dump(complete_theme, f, indent=2)
            
        print(f"Theme successfully saved to {THEME_FILE}")
        return True
    except Exception as e:
        print(f"Error saving theme: {e}")
        return False

def apply_theme(root, theme_data):
    """Apply theme to root window and ttk styles"""
    print(f"Applying theme: {theme_data.get('name')} with {len(theme_data)} properties")
    style = ttk.Style()
    
    # Get current platform
    current_platform = platform.system()  # 'Windows', 'Darwin' (macOS), or 'Linux'
    
    # Force reset of all styles first
    style.theme_use("default")
    style.theme_use("clam")  # "clam" works better for customization
    
    # Ensure a complete theme with all required properties
    complete_theme = LIGHT_THEME.copy()
    for key, value in theme_data.items():
        complete_theme[key] = value
    
    # Use the complete theme for all styling
    theme_data = complete_theme
    
    # Set global settings
    style.configure(".", 
                   background=theme_data["background"],
                   foreground=theme_data["foreground"],
                   troughcolor=theme_data["entry_bg"],
                   selectbackground=theme_data["selected"],
                   selectforeground=theme_data["selected_fg"],
                   fieldbackground=theme_data["entry_bg"],
                   borderwidth=1,
                   darkcolor=theme_data["background"],
                   lightcolor=theme_data["background"])
    
    # Configure colors for ttk widgets with explicit foreground and background settings
    style.configure("TFrame", background=theme_data["background"])
    style.configure("TLabel", background=theme_data["background"], foreground=theme_data["foreground"])
    
    # Redefine the button layout to fix white boxes
    if current_platform == "Windows":
        # Windows-specific fix
        style.layout("TButton", [
            ("Button.border", {
                "sticky": "nswe", 
                "border": "1", 
                "children": [
                    ("Button.focus", {
                        "sticky": "nswe", 
                        "children": [
                            ("Button.padding", {
                                "sticky": "nswe", 
                                "children": [
                                    ("Button.label", {"sticky": "nswe"})
                                ]
                            })
                        ]
                    })
                ]
            })
        ])
        
        # Windows-specific combobox layout
        style.layout("TCombobox", [
            ("Combobox.field", {"sticky": "nswe", "children": [
                ("Combobox.downarrow", {"side": "right", "sticky": "ns"}),
                ("Combobox.padding", {"expand": "1", "sticky": "nswe", "children": [
                    ("Combobox.textarea", {"sticky": "nswe"})
                ]})
            ]})
        ])
    
    # Configure button styles
    style.configure("TButton", 
                   background=theme_data["accent"],
                   foreground=theme_data["accent_fg"],
                   borderwidth=1,
                   relief="raised")
    
    # Button mapping for hover and active states
    style.map("TButton",
             background=[("active", theme_data["hover"]), 
                         ("pressed", theme_data["hover"]),
                         ("!disabled", theme_data["accent"]),
                         ("disabled", theme_data["background"])],
             foreground=[("active", theme_data["accent_fg"]), 
                         ("disabled", theme_data["completed"])])
    
    # Configure Combobox explicitly
    style.configure("TCombobox", 
                  selectbackground=theme_data["selected"],
                  selectforeground=theme_data["selected_fg"],
                  fieldbackground=theme_data["entry_bg"],
                  background=theme_data["entry_bg"],
                  foreground=theme_data["entry_fg"],
                  arrowcolor=theme_data["foreground"],
                  borderwidth=1,
                  relief="solid")
    
    # Define mappings for all states to ensure no white appears
    style.map("TCombobox",
             fieldbackground=[("readonly", theme_data["entry_bg"]), 
                             ("disabled", theme_data["background"]),
                             ("active", theme_data["entry_bg"]),
                             ("focus", theme_data["entry_bg"]),
                             ("hover", theme_data["entry_bg"]),
                             ("!disabled", theme_data["entry_bg"])],
             selectbackground=[("readonly", theme_data["selected"])],
             selectforeground=[("readonly", theme_data["selected_fg"])],
             background=[("readonly", theme_data["entry_bg"]), 
                       ("active", theme_data["entry_bg"]),
                       ("focus", theme_data["entry_bg"]),
                       ("hover", theme_data["entry_bg"]),
                       ("!disabled", theme_data["entry_bg"]),
                       ("disabled", theme_data["background"])],
             foreground=[("readonly", theme_data["entry_fg"]), 
                        ("disabled", theme_data["header_fg"]),
                        ("active", theme_data["entry_fg"]),
                        ("focus", theme_data["entry_fg"]),
                        ("hover", theme_data["entry_fg"])])
    
    # Configure the dropdown list style
    style.configure('TCombobox.Listbox', 
                   background=theme_data["entry_bg"],
                   foreground=theme_data["entry_fg"],
                   selectbackground=theme_data["selected"],
                   selectforeground=theme_data["selected_fg"],
                   borderwidth=1)
    
    # Try to configure the dropdown arrow specifically
    # Skip this as element_configure is not available on some systems
    # We'll handle this differently through the _patch_windows_tk_widgets function
    
    # Configure Checkbutton explicitly
    style.configure("TCheckbutton", 
                  background=theme_data["background"],
                  foreground=theme_data["foreground"])
    
    style.map("TCheckbutton",
             background=[("active", theme_data["background"]),
                        ("disabled", theme_data["background"]),
                        ("selected", theme_data["background"]),
                        ("!disabled", theme_data["background"])],
             foreground=[("active", theme_data["foreground"])])
    
    # Entry field styling with explicit mappings
    style.configure("TEntry", 
                   fieldbackground=theme_data["entry_bg"],
                   foreground=theme_data["entry_fg"],
                   selectbackground=theme_data["selected"],
                   selectforeground=theme_data["selected_fg"],
                   borderwidth=1)
    
    style.map("TEntry",
             fieldbackground=[("disabled", theme_data["background"]),
                             ("readonly", theme_data["entry_bg"]),
                             ("active", theme_data["entry_bg"]),
                             ("focus", theme_data["entry_bg"])],
             foreground=[("disabled", theme_data["header_fg"])])
    
    # Configure specific styles
    style.configure("Header.TLabel", 
                   font=("Segoe UI", 16, "bold"), 
                   foreground=theme_data["header_fg"],
                   background=theme_data["background"])
    
    style.configure("YearBanner.TLabel", 
                   font=("Segoe UI", 14, "bold"), 
                   background=theme_data["accent"], 
                   foreground=theme_data["accent_fg"],
                   padding=10)
    
    style.configure("SectionHeader.TLabel", 
                   font=("Segoe UI", 12, "bold"), 
                   foreground=theme_data["header_fg"],
                   background=theme_data["background"],
                   padding=5)
    
    # Button styles with explicit active states
    style.configure("Primary.TButton", 
                   background=theme_data["accent"], 
                   foreground=theme_data["accent_fg"])
    
    style.map("Primary.TButton",
             background=[("active", theme_data["hover"]), 
                         ("pressed", theme_data["hover"]),
                         ("!disabled", theme_data["accent"]),
                         ("disabled", theme_data["background"])],
             foreground=[("active", theme_data["accent_fg"]), 
                         ("disabled", theme_data["completed"])])
    
    style.configure("Edit.TButton", 
                   background=theme_data["needed"],
                   foreground=theme_data["accent_fg"])
    
    style.configure("Delete.TButton", 
                   background=theme_data["error"],
                   foreground=theme_data["accent_fg"])
    
    # Treeview styling with explicit configurations
    style.configure("Treeview", 
                   background=theme_data["entry_bg"],
                   foreground=theme_data["entry_fg"],
                   fieldbackground=theme_data["entry_bg"],
                   borderwidth=1)
    
    style.configure("Treeview.Heading", 
                   background=theme_data["header_bg"],
                   foreground=theme_data["header_fg"],
                   font=("Segoe UI", 9, "bold"))
    
    # Apply explicit mappings for selected items
    style.map("Treeview",
             background=[("selected", theme_data["selected"])],
             foreground=[("selected", theme_data["selected_fg"])])
    
    # Configure the tag colors for treeview
    try:
        style.map("Treeview",
                 foreground=[("tag-completed", theme_data["completed"]),
                            ("tag-date_passed", theme_data["date_passed"])])
    except tk.TclError:
        pass  # Tags might not exist yet
    
    # Update default background for all widgets
    root.configure(background=theme_data["background"])
    
    # Fix for scrollbar appearance
    style.configure("TScrollbar", 
                   background=theme_data["background"],
                   arrowcolor=theme_data["foreground"],
                   bordercolor=theme_data["background"],
                   troughcolor=theme_data["entry_bg"],
                   gripcount=0,
                   borderwidth=1)
    
    # Scrollbar styling through standard configuration
    # Don't try to use element_configure as it's not available on some systems
    style.configure("TScrollbar", 
                   background=theme_data["background"],
                   arrowcolor=theme_data["foreground"],
                   troughcolor=theme_data["entry_bg"])
    
    # Fix for DateEntry widget from tkcalendar
    try:
        style.configure("DateEntry.TEntry",
                       background=theme_data["accent"],
                       foreground=theme_data["accent_fg"],
                       fieldbackground=theme_data["entry_bg"],
                       selectbackground=theme_data["selected"],
                       selectforeground=theme_data["selected_fg"])
    except:
        pass  # DateEntry might not be available yet
    
    # Apply theme to customizer-specific styles
    style.configure("Customizer.TFrame", background=theme_data["background"])
    style.configure("Customizer.TLabel", background=theme_data["background"], foreground=theme_data["foreground"])
    
    # Apply color to all menu widgets
    for widget in root.winfo_children():
        if isinstance(widget, tk.Menu):
            widget.configure(
                background=theme_data["background"],
                foreground=theme_data["foreground"],
                activebackground=theme_data["hover"],
                activeforeground=theme_data["foreground"],
                borderwidth=1
            )
            _update_menu_items(widget, theme_data)
    
    # Store the theme data in the root widget for access by child components
    root.theme_data = theme_data
    
    # Force update of display
    root.update_idletasks()
    
    # For Windows platform specifically - additional fix for white boxes
    if current_platform == "Windows":
        # Patch tk widgets that ttk can't properly theme on Windows
        _patch_windows_tk_widgets(root, theme_data)
    
    return theme_data

def _patch_windows_tk_widgets(parent, theme_data):
    """Special fix for Windows platform to replace ttk widgets with tk widgets where needed"""
    try:
        for widget in parent.winfo_children():
            # Process each widget
            try:
                # Try to fix ttk.Button by replacing its background directly
                if widget.winfo_class() == "TButton":
                    widget._style_name = widget.cget("style")
                    
                    # Get the underlying Tk widget
                    widget_path = str(widget)
                    try:
                        # Try to access the underlying tk frame
                        label_path = widget_path + ".Button.label"
                        parent.tk.call(label_path, "configure", "-background", theme_data["accent"])
                    except:
                        pass
                    
                # Special handling for combobox which often has white background in arrows
                elif widget.winfo_class() == "TCombobox":
                    widget._style_name = widget.cget("style")
                    # Try to access the underlying dropdown button
                    try:
                        widget_path = str(widget)
                        # Configure all parts explicitly
                        parent.tk.call(widget_path, "configure", "-background", theme_data["entry_bg"])
                        parent.tk.call(widget_path, "configure", "-foreground", theme_data["entry_fg"])
                        parent.tk.call(widget_path, "configure", "-fieldbackground", theme_data["entry_bg"])
                    except:
                        pass
                
                # Process children recursively
                _patch_windows_tk_widgets(widget, theme_data)
                
            except (AttributeError, tk.TclError):
                # Skip any widgets that can't be configured this way
                continue
    except:
        # Fail gracefully if patching doesn't work
        pass

def _update_menu_items(menu, theme_data):
    """Recursively update menu items with theme colors"""
    for index in range(menu.index("end") + 1 if menu.index("end") is not None else 0):
        try:
            if menu.type(index) == "cascade":
                submenu = menu.nametowidget(menu.entrycget(index, "menu"))
                submenu.configure(
                    background=theme_data["background"],
                    foreground=theme_data["foreground"],
                    activebackground=theme_data["hover"],
                    activeforeground=theme_data["foreground"]
                )
                _update_menu_items(submenu, theme_data)
        except (tk.TclError, AttributeError):
            pass

class ThemeCustomizer:
    def __init__(self, parent, initial_theme=None, apply_callback=None):
        """Initialize theme customizer dialog
        
        Args:
            parent: Parent window
            initial_theme: Initial theme dictionary
            apply_callback: Function to call with theme data when applied
        """
        self.parent = parent
        self.theme_data = initial_theme or load_theme()
        self.apply_callback = apply_callback
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Theme Customizer")
        self.dialog.geometry("650x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Initialize variables
        self.name_var = tk.StringVar(value=self.theme_data.get("name", "Custom"))
        self.color_displays = {}
        
        # Make dialog modal
        self.dialog.focus_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self.apply_theme)
        
        # Apply theme to make the dialog match current theme
        style = ttk.Style()
        background = self.theme_data.get("background", "#f8f9fa")
        foreground = self.theme_data.get("foreground", "#212529")
        style.configure("Customizer.TFrame", background=background)
        style.configure("Customizer.TLabel", background=background, foreground=foreground)
        
        # Create widgets
        self.create_widgets()
        
        # Center dialog on parent
        self.center_on_parent()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20", style="Customizer.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Preset buttons frame
        preset_frame = ttk.Frame(main_frame, style="Customizer.TFrame")
        preset_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(preset_frame, text="Theme Presets:", style="Customizer.TLabel").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            preset_frame, 
            text="Light Theme",
            command=lambda: self.load_preset(LIGHT_THEME.copy())
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            preset_frame, 
            text="Dark Theme",
            command=lambda: self.load_preset(DARK_THEME.copy())
        ).pack(side=tk.LEFT)
        
        # Color customization frame
        color_frame = ttk.Frame(main_frame, style="Customizer.TFrame")
        color_frame.pack(fill=tk.BOTH, expand=True)
        
        # Grid layout for color pickers
        for idx, (key, label) in enumerate(self.get_color_fields()):
            row = idx // 2
            col = idx % 2 * 2  # Multiply by 2 to leave space for the color button
            
            # Create label for color field
            ttk.Label(color_frame, text=label + ":", style="Customizer.TLabel").grid(
                row=row, column=col, sticky=tk.W, padx=(5 if col > 0 else 0, 5), pady=5
            )
            
            # Frame to hold color display and label
            color_container = ttk.Frame(color_frame, style="Customizer.TFrame")
            color_container.grid(row=row, column=col+1, padx=5)
            
            # Color frame to show the current color
            color_display = tk.Frame(
                color_container, 
                width=20, 
                height=20, 
                bg=self.theme_data.get(key, "#ffffff")
            )
            color_display.pack(side=tk.LEFT, padx=(0, 5))
            
            # Store reference to color display for later updates
            self.color_displays[key] = color_display
            
            # Make color display clickable
            color_display.bind("<Button-1>", lambda e, k=key: self.pick_color(k))
            
            # Add clickable label
            change_label = ttk.Label(color_container, text="[Change]", cursor="hand2", style="Customizer.TLabel")
            change_label.pack(side=tk.LEFT)
            change_label.bind("<Button-1>", lambda e, k=key: self.pick_color(k))
        
        # Theme name frame
        name_frame = ttk.Frame(main_frame, style="Customizer.TFrame")
        name_frame.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(name_frame, text="Theme Name:", style="Customizer.TLabel").pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Entry(name_frame, textvariable=self.name_var, width=30).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Apply button frame
        button_frame = ttk.Frame(main_frame, style="Customizer.TFrame")
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(
            button_frame, 
            text="Apply Theme",
            command=self.apply_theme,
            style="Primary.TButton"
        ).pack(side=tk.LEFT, padx=(0, 5))
    
    def get_color_fields(self):
        """Return list of color field keys and labels"""
        return [
            ("background", "Background Color"),
            ("foreground", "Text Color"),
            ("accent", "Accent Color"),
            ("accent_fg", "Accent Text Color"),
            ("header_bg", "Header Background"),
            ("header_fg", "Header Text"),
            ("entry_bg", "Input Background"),
            ("entry_fg", "Input Text"),
            ("selected", "Selected Item"),
            ("selected_fg", "Selected Text"),
            ("needed", "Needed Item Color"),
            ("completed", "Completed Item Color"),
            ("date_passed", "Passed Date Color"),
            ("error", "Error/Delete Color")
        ]
    
    def pick_color(self, key):
        """Open color picker for the specified key"""
        current_color = self.theme_data.get(key, "#ffffff")
        color = colorchooser.askcolor(color=current_color, title=f"Select {key} color")
        
        if color[1]:  # If a color was chosen (not cancelled)
            self.theme_data[key] = color[1]
            # Update color display
            if key in self.color_displays:
                self.color_displays[key].configure(bg=color[1])
    
    def load_preset(self, preset_theme):
        """Load a preset theme"""
        self.theme_data = preset_theme
        self.name_var.set(preset_theme.get("name", "Custom"))
        
        # Update all color displays
        for key, display in self.color_displays.items():
            if key in preset_theme:
                display.configure(bg=preset_theme[key])
    
    def apply_theme(self):
        """Apply the current theme and close dialog"""
        # Update the theme name
        self.theme_data["name"] = self.name_var.get()
        
        # Ensure all required keys are present
        complete_theme = LIGHT_THEME.copy()
        for key, value in self.theme_data.items():
            complete_theme[key] = value
        complete_theme["name"] = self.name_var.get()
        
        # Save the theme
        save_theme(complete_theme)
        
        # Call the apply callback if provided
        if self.apply_callback:
            self.apply_callback(complete_theme)
        
        # Close the dialog
        self.dialog.destroy()
    
    def center_on_parent(self):
        """Center the dialog on the parent window"""
        self.dialog.update_idletasks()
        
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")