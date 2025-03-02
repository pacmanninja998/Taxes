import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import datetime
import json
import os
from pathlib import Path
import webbrowser
import sys
from tkcalendar import DateEntry  # You'll need to install this: pip install tkcalendar

# Import custom modules
from data_manager import (
    load_all_data, save_all_data, 
    get_documents_for_year, save_documents_for_year,
    import_from_last_year, USER_DOCS
)
from document_editor import DocumentEditor
from theme_manager import ThemeCustomizer, load_theme, apply_theme, save_theme
from toggle_switch import ToggleSwitch

class TaxDocumentTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Tax Document Tracker")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize variables
        self.current_tax_year = self.get_current_tax_year()
        self.current_view_mode = tk.StringVar(value="All")
        self.documents = []
        self.status_message = tk.StringVar()
        
        # Load the theme data first
        print("Loading theme in __init__")
        self.theme_data = load_theme()
        print(f"Loaded theme: {self.theme_data.get('name')}")
        
        # Store theme data in root for access by components
        self.root.theme_data = self.theme_data
        
        # Create a ttk style object
        self.style = ttk.Style()
        
        # Configure basic styles first - this establishes a baseline
        self.configure_basic_styles()
        
        # Set root window background
        bg_color = self.theme_data.get("background", "#f8f9fa")
        self.root.configure(background=bg_color)
        
        # Create main frame with explicit background color
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.apply_theme_to_widget(self.main_frame, "background")
        
        # Create the GUI components
        self.create_header()
        self.create_year_selector()
        self.create_data_management()
        self.create_add_document_button()
        self.create_view_selector()
        self.create_document_list()
        self.create_status_bar()
        
        # Create menu
        self.create_menu()
        
        # Load documents for current year
        self.load_documents()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()
        
        # Final pass to ensure theme is applied to all widgets
        self.apply_theme_to_all_widgets()
    
    def get_current_tax_year(self):
        """Get the current tax year (previous calendar year if before April)"""
        current_date = datetime.datetime.now()
        return current_date.year - 1 if current_date.month < 4 else current_date.year

    def configure_styles(self):
        """Configure ttk styles for the application"""
        style = ttk.Style()
        
        # Configure main styles
        style.configure("TFrame", background="#f8f9fa")
        style.configure("TLabel", background="#f8f9fa", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        
        # Header styles
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#2c3e50")
        style.configure("YearBanner.TLabel", 
                       font=("Segoe UI", 14, "bold"), 
                       background="#3498db", 
                       foreground="white",
                       padding=10)
        
        # Section header style
        style.configure("SectionHeader.TLabel", 
                       font=("Segoe UI", 12, "bold"), 
                       foreground="#2c3e50",
                       padding=5)
        
        # Button styles
        style.configure("Primary.TButton", 
                       background="#3498db", 
                       foreground="white")
        style.configure("Edit.TButton", 
                       background="#f39c12")
        style.configure("Delete.TButton", 
                       background="#e74c3c")
        
        # Apply tag colors initially
        if hasattr(self, 'tree'):
            self.apply_tag_colors()

    def create_header(self):
        """Create the application header"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Tax Document Tracker", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Theme toggle button
        theme_frame = ttk.Frame(header_frame)
        theme_frame.pack(side=tk.RIGHT)
        
        # Use regular Tk button
        theme_btn = tk.Button(
            theme_frame,
            text="Customize Theme",
            command=self.open_theme_customizer,
            background=self.theme_data.get("accent"),
            foreground=self.theme_data.get("accent_fg"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("accent_fg"),
            relief="raised",
            borderwidth=1,
            padx=10,
            pady=2
        )
        theme_btn.pack(side=tk.RIGHT)
        
        # Tax year banner
        self.year_banner = ttk.Label(
            self.main_frame, 
            text=f"Tax Year: {self.current_tax_year} (Due in April, {self.current_tax_year + 1})",
            style="YearBanner.TLabel",
            anchor="center"
        )
        self.year_banner.pack(fill=tk.X, pady=(0, 20))

    def create_year_selector(self):
        """Create the year selector controls"""
        year_frame = ttk.Frame(self.main_frame)
        year_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Use regular Tk buttons
        prev_year_btn = tk.Button(
            year_frame, 
            text="← Previous Year",
            command=self.go_to_previous_year,
            background=self.theme_data.get("accent"),
            foreground=self.theme_data.get("accent_fg"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("accent_fg"),
            relief="raised",
            borderwidth=1,
            padx=10,
            pady=2
        )
        prev_year_btn.pack(side=tk.LEFT)
        
        self.current_year_label = ttk.Label(
            year_frame, 
            text=f"Tax Year {self.current_tax_year}",
            font=("Segoe UI", 12, "bold")
        )
        self.current_year_label.pack(side=tk.LEFT, expand=True)
        
        next_year_btn = tk.Button(
            year_frame, 
            text="Next Year →",
            command=self.go_to_next_year,
            background=self.theme_data.get("accent"),
            foreground=self.theme_data.get("accent_fg"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("accent_fg"),
            relief="raised",
            borderwidth=1,
            padx=10,
            pady=2
        )
        next_year_btn.pack(side=tk.RIGHT)

    def create_data_management(self):
        """Create data management controls"""
        data_frame = ttk.Frame(self.main_frame)
        data_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Use regular Tk button
        import_btn = tk.Button(
            data_frame, 
            text="Import Last Year's Documents",
            command=self.import_last_year_documents,
            background=self.theme_data.get("accent"),
            foreground=self.theme_data.get("accent_fg"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("accent_fg"),
            relief="raised",
            borderwidth=1,
            padx=10,
            pady=2
        )
        import_btn.pack(side=tk.LEFT)

    def create_add_document_button(self):
        """Create button to add new documents"""
        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        self.apply_theme_to_widget(button_frame, "frame")
        
        # Add document button - use tk.Button instead of ttk.Button
        add_btn = tk.Button(
            button_frame, 
            text="Add New Document",
            command=self.open_add_document_dialog,
            background=self.theme_data.get("accent"),
            foreground=self.theme_data.get("accent_fg"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("accent_fg"),
            relief="raised",
            borderwidth=1
        )
        add_btn.pack(side=tk.LEFT)

    def create_view_selector(self):
        """Create view mode selector"""
        view_frame = ttk.Frame(self.main_frame)
        view_frame.pack(fill=tk.X, pady=(0, 10))
        self.apply_theme_to_widget(view_frame, "frame")
        
        view_label = ttk.Label(view_frame, text="View Mode:")
        view_label.pack(side=tk.LEFT, padx=(0, 10))
        self.apply_theme_to_widget(view_label, "frame")
        
        # Use a regular TK OptionMenu instead of ttk.Combobox for better theming
        self.current_view_mode = tk.StringVar(value="All")
        options = ["All", "Needed", "Completed"]
        
        # Create OptionMenu
        view_dropdown = tk.OptionMenu(view_frame, self.current_view_mode, *options)
        view_dropdown.configure(
            background=self.theme_data.get("entry_bg"),
            foreground=self.theme_data.get("entry_fg"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("foreground"),
            highlightthickness=1,
            highlightbackground=self.theme_data.get("entry_bg"),
            highlightcolor=self.theme_data.get("accent")
        )
        
        # Configure dropdown menu
        dropdown_menu = view_dropdown["menu"]
        dropdown_menu.configure(
            background=self.theme_data.get("entry_bg"),
            foreground=self.theme_data.get("entry_fg"),
            activebackground=self.theme_data.get("selected"),
            activeforeground=self.theme_data.get("selected_fg")
        )
        
        view_dropdown.pack(side=tk.LEFT)
        
        # Trace variable changes
        self.current_view_mode.trace_add("write", lambda *args: self.load_documents())

    def create_document_list(self):
        """Create the document list area"""
        # Container frame for the list
        list_container = tk.Frame(
            self.main_frame, 
            relief=tk.GROOVE, 
            borderwidth=1,
            background=self.theme_data.get("background")
        )
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview widget - use "tree headings" to show both tree and column headers
        columns = ("name", "expected_date", "previous_date", "website")
        self.tree = ttk.Treeview(list_container, columns=columns, show="tree headings", selectmode="browse")
        
        # Define headings
        self.tree.heading("#0", text="Status")  # Tree column as Status
        self.tree.heading("name", text="Document")
        self.tree.heading("expected_date", text="Expected Date")
        self.tree.heading("previous_date", text="Last Year's Date")
        self.tree.heading("website", text="Website")
        
        # Define columns with minimum widths
        self.tree.column("#0", width=150, minwidth=100)  # Tree column (status)
        self.tree.column("name", width=250, minwidth=150)
        self.tree.column("expected_date", width=120, minwidth=120)
        self.tree.column("previous_date", width=120, minwidth=120)
        self.tree.column("website", width=200, minwidth=120)
        
        # Create scrollbars
        vsb = tk.Scrollbar(list_container, orient="vertical", command=self.tree.yview)
        hsb = tk.Scrollbar(list_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        bg_color = self.theme_data.get("entry_bg")
        fg_color = self.theme_data.get("entry_fg")
        select_color = self.theme_data.get("selected")
        select_fg = self.theme_data.get("selected_fg")
        accent=self.theme_data.get("accent")
        background=self.theme_data.get("background")
        troughcolor=self.theme_data.get("entry_bg")
        activebackground=self.theme_data.get("accent")
        style = ttk.Style()
        
        # Set scrollbar colors
        vsb.configure(
            background=self.theme_data.get("background"),
            troughcolor=self.theme_data.get("entry_bg"),
            activebackground=self.theme_data.get("accent")
        )
        hsb.configure(
            background=self.theme_data.get("background"),
            troughcolor=self.theme_data.get("entry_bg"),
            activebackground=self.theme_data.get("accent")
        )
        
        # Grid layout
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)  # Right click
        
        # Apply treeview styling
        self.style = ttk.Style()     
     
        # Configure Treeview colors
        self.style.configure("Treeview", 
                           background=self.theme_data.get("entry_bg"),
                           foreground=self.theme_data.get("entry_fg"),
                           fieldbackground=self.theme_data.get("entry_bg"),
                           borderwidth=1)
        
        # Configure column headers
        self.style.configure("Treeview.Heading", 
                           background=self.theme_data.get("header_bg"),
                           foreground=self.theme_data.get("header_fg"),
                           relief="raised")
 
        # Configure selection colors       
        self.style.map("Treeview.Heading", 
                           background=[("selected", self.theme_data.get("header_bg"))],
                           foreground=[("selected", self.theme_data.get("header_fg"))])
        self.style.map("Treeview",
                     background=[("selected", self.theme_data.get("selected"))],
                     foreground=[("selected", self.theme_data.get("selected_fg"))],
                     fieldbackground=[("selected", self.theme_data.get("entry_bg"))])
        
        # Apply tag colors
        self.apply_tag_colors()

    def create_status_bar(self):
        """Create status bar at the bottom of the window"""
        status_frame = tk.Frame(
            self.root, 
            relief=tk.SUNKEN, 
            borderwidth=1,
            background=self.theme_data.get("background")
        )
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        status_label = tk.Label(
            status_frame, 
            textvariable=self.status_message, 
            anchor=tk.W,
            background=self.theme_data.get("background"),
            foreground=self.theme_data.get("foreground"),
            padx=5,
            pady=2
        )
        status_label.pack(side=tk.LEFT, fill=tk.X)
        
        # Initial status message
        self.set_status(f"Ready - Documents folder: {USER_DOCS}")

    def create_menu(self):
        """Create application menu"""
        menu_bar = tk.Menu(
            self.root,
            background=self.theme_data.get("background"),
            foreground=self.theme_data.get("foreground"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("foreground"),
            relief="flat",
            borderwidth=1
        )
        self.root.config(menu=menu_bar)
        
        # File menu
        file_menu = tk.Menu(
            menu_bar, 
            tearoff=0,
            background=self.theme_data.get("background"),
            foreground=self.theme_data.get("foreground"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("foreground")
        )
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add New Document", command=self.open_add_document_dialog, accelerator="Ctrl+N")
        file_menu.add_command(label="Import from Last Year", command=self.import_last_year_documents)
        file_menu.add_separator()
        file_menu.add_command(label="Refresh", command=self.load_documents, accelerator="F5")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(
            menu_bar, 
            tearoff=0,
            background=self.theme_data.get("background"),
            foreground=self.theme_data.get("foreground"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("foreground")
        )
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Edit Selected Document", command=self.edit_selected_document)
        edit_menu.add_command(label="Delete Selected Document", command=self.delete_selected_document, accelerator="Delete")
        edit_menu.add_separator()
        edit_menu.add_command(label="Toggle Document Status", command=self.toggle_selected_document)
        
        # View menu
        view_menu = tk.Menu(
            menu_bar, 
            tearoff=0,
            background=self.theme_data.get("background"),
            foreground=self.theme_data.get("foreground"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("foreground")
        )
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # View mode submenu
        view_mode_menu = tk.Menu(
            view_menu, 
            tearoff=0,
            background=self.theme_data.get("background"),
            foreground=self.theme_data.get("foreground"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("foreground")
        )
        view_menu.add_cascade(label="View Mode", menu=view_mode_menu)
        
        # Radio buttons for view mode
        self.view_mode_var = tk.StringVar(value=self.current_view_mode.get())
        view_mode_menu.add_radiobutton(label="All Documents", variable=self.view_mode_var, value="All", 
                                      command=self.change_view_mode)
        view_mode_menu.add_radiobutton(label="Needed Documents", variable=self.view_mode_var, value="Needed", 
                                      command=self.change_view_mode)
        view_mode_menu.add_radiobutton(label="Completed Documents", variable=self.view_mode_var, value="Completed", 
                                      command=self.change_view_mode)
        
        view_menu.add_separator()
        view_menu.add_command(label="Customize Theme", command=self.open_theme_customizer)
        
        # Help menu
        help_menu = tk.Menu(
            menu_bar, 
            tearoff=0,
            background=self.theme_data.get("background"),
            foreground=self.theme_data.get("foreground"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("foreground")
        )
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)

    def change_view_mode(self):
        """Change view mode from menu"""
        self.current_view_mode.set(self.view_mode_var.get())
        self.load_documents()
    
    def edit_selected_document(self):
        """Edit the selected document"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        
        # Ignore section headers
        if not self.tree.parent(item):
            return
            
        # Get document index
        tags = self.tree.item(item, "tags")
        if tags:
            tag = tags[0]
            if tag.startswith("index:"):
                index = int(tag.split(":")[1])
                self.edit_document(index)
    
    def toggle_selected_document(self):
        """Toggle the status of the selected document"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        
        # Ignore section headers
        if not self.tree.parent(item):
            return
            
        self.toggle_document_status(item)
    
    def open_theme_customizer(self):
        """Open theme customizer dialog"""
        ThemeCustomizer(self.root, self.theme_data, self.apply_theme_callback)
    
    def apply_theme_callback(self, theme_data):
        """Callback when theme is applied from customizer"""
        self.theme_data = theme_data
        
        # Save the theme to file first to ensure it persists
        save_success = save_theme(theme_data)
        
        # Store in root for component access
        self.root.theme_data = theme_data
        
        # Apply the theme
        apply_theme(self.root, theme_data)
        
        # Update treeview colors
        self.apply_tag_colors()
        
        # Update status message
        status_msg = f"Applied theme: {theme_data.get('name', 'Custom')}"
        if save_success:
            status_msg += " (Saved)"
        else:
            status_msg += " (Failed to save)"
        
        self.set_status(status_msg)
    
    def apply_tag_colors(self):
        """Apply colors to treeview tags based on current theme"""
        # Configure the date_passed tag with the user's chosen color
        self.tree.tag_configure("date_passed", foreground=self.theme_data.get("date_passed", "#27ae60"))
        # Configure other tags
        self.tree.tag_configure("Completed", foreground=self.theme_data.get("Completed", "#7f8c8d"))
        bg_color = self.theme_data.get("entry_bg")
        fg_color = self.theme_data.get("entry_fg")
        select_color = self.theme_data.get("selected")
        select_fg = self.theme_data.get("selected_fg")
        style = ttk.Style()
        style.configure("Treeview", 
                  fieldbackground=bg_color,  # This is the main table background
                  background=bg_color,       # Background for non-selected items
                  foreground=fg_color) 
        style.configure("Treeview.Heading",
                  background=self.theme_data.get("header_bg"),
                  foreground=self.theme_data.get("header_fg"),
                  relief="flat")
        style.map("Treeview",
             background=[("selected", select_color)],
             foreground=[("selected", select_fg)])
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Tax Document Tracker
Version 1.0

A simple application to help track tax documents.

Created by pacmanninja998.
    """
        self.show_custom_dialog("About", about_text)
    
    def show_shortcuts(self):
        """Show keyboard shortcuts"""
        shortcuts_text = """
        Keyboard Shortcuts:

        Ctrl+N: Add new document
        Delete: Delete selected document
        F5: Refresh document list
        Double-click: Open website (if available) or toggle status
        Right-click: Show context menu
        """
        self.show_custom_dialog("Keyboard Shortcuts", shortcuts_text)
    
    def show_custom_dialog(self, title, message):
        """Show a custom themed dialog box"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(background=self.theme_data.get("background"))
        
        # Message frame
        message_frame = tk.Frame(
            dialog,
            background=self.theme_data.get("background"),
            padx=20,
            pady=20
        )
        message_frame.pack(fill=tk.BOTH, expand=True)
        
        # Message label
        msg_label = tk.Label(
            message_frame,
            text=message,
            justify=tk.LEFT,
            background=self.theme_data.get("background"),
            foreground=self.theme_data.get("foreground"),
            padx=10,
            pady=10
        )
        msg_label.pack(fill=tk.BOTH, expand=True)
        
        # OK button
        button_frame = tk.Frame(
            dialog,
            background=self.theme_data.get("background"),
            pady=10
        )
        button_frame.pack(fill=tk.X)
        
        ok_button = tk.Button(
            button_frame,
            text="OK",
            command=dialog.destroy,
            background=self.theme_data.get("accent"),
            foreground=self.theme_data.get("accent_fg"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("accent_fg"),
            padx=20,
            pady=2
        )
        ok_button.pack()
        
        # Center dialog on parent
        self.center_dialog(dialog)
        
        # Make dialog modal
        dialog.focus_set()
        dialog.wait_window()
    
    def center_dialog(self, dialog):
        """Center dialog on parent window"""
        dialog.update_idletasks()
        
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()
        parent_x = self.root.winfo_rootx()
        parent_y = self.root.winfo_rooty()
        
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        dialog.geometry(f"+{x}+{y}")

    def load_documents(self):
        """Load documents for current tax year and update the display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Load documents
        self.documents = get_documents_for_year(self.current_tax_year)
                       
        # Filter documents based on view mode
        view_mode = self.current_view_mode.get()
        
        needed_documents = []
        completed_documents = []
        
        if view_mode == "All" or view_mode == "Needed":
            needed_documents = [doc for doc in self.documents if not doc.get("Completed", False)]
        
        if view_mode == "All" or view_mode == "Completed":
            completed_documents = [doc for doc in self.documents if doc.get("Completed", False)]
        
        # Current date for date checking
        current_date = datetime.date.today()
        
        # Create document sections with collapsible categories
        if needed_documents:
            # Add the "Needed Documents" header as a parent item
            needed_header = self.tree.insert("", "end", text="Needed Documents", 
                                           open=True, tags=("section",))
            
            for doc in needed_documents:
                # Check if expected date has passed
                date_passed = False
                if doc.get("expectedDate"):
                    try:
                        expected_date = datetime.datetime.strptime(doc.get("expectedDate"), "%Y-%m-%d").date()
                        date_passed = expected_date < current_date
                    except (ValueError, TypeError):
                        date_passed = False
                
                # Insert the treeview item with "□  Pending" in status column
                item_id = self.tree.insert(
                    needed_header, 
                    "end", 
                    text="□  Pending",  # Status in tree column
                    values=(
                        doc.get("name", ""),
                        self.format_date(doc.get("expectedDate", "")),
                        self.format_date(doc.get("previousYearDate", "")),
                        doc.get("website", "")
                    ),
                    tags=(f"index:{self.documents.index(doc)}", "date_passed" if date_passed else "")
                )
                
                # Update column widths based on content
                self.adjust_column_widths(doc)
        
        # Add completed documents section if there are any
        if completed_documents:
            completed_header = self.tree.insert("", "end", text="Completed Documents", 
                                              open=True, tags=("section",))
            
            for doc in completed_documents:
                # Insert the treeview item with "✓ Completed" in status column
                item_id = self.tree.insert(
                    completed_header, 
                    "end", 
                    text="✓ Completed",  # Status in tree column
                    values=(
                        doc.get("name", ""),
                        self.format_date(doc.get("expectedDate", "")),
                        self.format_date(doc.get("previousYearDate", "")),
                        doc.get("website", "")
                    ),
                    tags=(f"index:{self.documents.index(doc)}", "Completed")
                )
                
                # Update column widths based on content
                self.adjust_column_widths(doc)
        
        # Show message if no documents found
        if not self.documents:
            self.set_status(f"No documents found for tax year {self.current_tax_year}")
        else:
            total = len(self.documents)
            completed = len(completed_documents)
            self.set_status(f"Loaded {total} documents ({completed} completed) for tax year {self.current_tax_year}")
            
        # Apply tag colors
        self.apply_tag_colors()

    def adjust_column_widths(self, doc):
        """Adjust column widths based on content"""
        # Status column (tree column #0)
        status_width = 150  # Fixed width for status
        current_width = self.tree.column("#0", "width")
        if status_width > current_width:
            self.tree.column("#0", width=status_width)
            
        # Name column
        name_width = len(doc.get("name", "")) * 7  # Approximate width based on text length
        current_width = self.tree.column("name", "width")
        if name_width > current_width:
            self.tree.column("name", width=name_width)
        
        # Website column
        website = doc.get("website", "")
        if website:
            website_width = len(website) * 7  # Approximate width based on text length
            current_width = self.tree.column("website", "width")
            if website_width > current_width:
                self.tree.column("website", width=website_width)

    def on_item_double_click(self, event):
        """Handle double click on an item"""
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
            
        # Get the item's parent to check if it's a section header
        parent = self.tree.parent(item)
        
        # If it's a section header (has no parent), expand/collapse it
        if not parent:
            if self.tree.item(item, "open"):
                self.tree.item(item, open=False)
            else:
                self.tree.item(item, open=True)
            return
            
        # For regular items (documents)
        values = self.tree.item(item, "values")
        if not values:
            return
            
        # Get document index
        tags = self.tree.item(item, "tags")
        if not tags:
            return
            
        tag = tags[0]
        if not tag.startswith("index:"):
            return
            
        index = int(tag.split(":")[1])
        
        # Determine which column was clicked
        region = self.tree.identify_region(event.x, event.y)
        col = self.tree.identify_column(event.x)
        
        # If tree column (#0) was clicked, toggle status
        if col == "#0" or region == "tree":
            self.toggle_document_status(item)
        # If last column (website) was clicked and has a value, open website 
        elif col == "#4" and values[3]:  # Website is now at index 3
            self.open_website(index)
        # Otherwise, toggle status as default action
        else:
            self.toggle_document_status(item)

    def show_context_menu(self, event):
        """Show context menu on right click"""
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
        
        # Check if it's a section header (has no parent)
        parent = self.tree.parent(item)
        if not parent:
            # Section header context menu
            self.tree.selection_set(item)
            section_menu = tk.Menu(
                self.root, 
                tearoff=0,
                background=self.theme_data.get("background"),
                foreground=self.theme_data.get("foreground"),
                activebackground=self.theme_data.get("hover"),
                activeforeground=self.theme_data.get("foreground")
            )
            is_open = self.tree.item(item, "open")
            
            section_menu.add_command(
                label="Collapse Section" if is_open else "Expand Section",
                command=lambda: self.tree.item(item, open=not is_open)
            )
            
            section_menu.tk_popup(event.x_root, event.y_root)
            return
            
        # Regular item context menu
        self.tree.selection_set(item)
        
        # Create context menu
        context_menu = tk.Menu(
            self.root, 
            tearoff=0,
            background=self.theme_data.get("background"),
            foreground=self.theme_data.get("foreground"),
            activebackground=self.theme_data.get("hover"),
            activeforeground=self.theme_data.get("foreground")
        )
        
        # Get document index
        tags = self.tree.item(item, "tags")
        if tags:
            tag = tags[0]
            if tag.startswith("index:"):
                index = int(tag.split(":")[1])
                
                # Add menu items
                context_menu.add_command(label="Edit", command=lambda: self.edit_document(index))
                context_menu.add_command(label="Delete", command=lambda: self.delete_document(index))
                context_menu.add_separator()
                context_menu.add_command(
                    label="Toggle Status", 
                    command=lambda: self.toggle_document_status(item)
                )
                
                # If the document has a website, add open website option
                if self.documents[index].get("website"):
                    context_menu.add_separator()
                    context_menu.add_command(
                        label="Open Website", 
                        command=lambda: self.open_website(index)
                    )
                
                # Display the context menu
                context_menu.tk_popup(event.x_root, event.y_root)

    def toggle_document_status(self, item):
        """Toggle the completed status of a document"""
        # Get document index
        tags = self.tree.item(item, "tags")
        if not tags:
            return
            
        tag = tags[0]
        if not tag.startswith("index:"):
            return
            
        index = int(tag.split(":")[1])
        
        # Toggle status
        was_completed = self.documents[index].get("Completed", False)
        self.documents[index]["Completed"] = not was_completed
        
        # If completed, set actual date to today if not already set
        if self.documents[index]["Completed"] and not self.documents[index].get("actualDate"):
            today = datetime.date.today().isoformat()
            self.documents[index]["actualDate"] = today
            
            # Update status message
            doc_name = self.documents[index].get("name", "Document")
            self.set_status(f"Marked '{doc_name}' as completed")
        else:
            # Update status message
            doc_name = self.documents[index].get("name", "Document")
            self.set_status(f"Marked '{doc_name}' as not completed")
        
        # Update the display for this item
        if self.documents[index]["Completed"]:
            self.tree.item(item, text="✓ Completed")
        else:
            self.tree.item(item, text="□  Pending")
            
        # Save and reload to ensure proper section placement
        save_documents_for_year(self.current_tax_year, self.documents)
        self.load_documents()

    def edit_document(self, index):
        """Open dialog to edit a document"""
        doc = self.documents[index]
        
        def save_callback(updated_doc):
            # Update document at specified index
            self.documents[index] = updated_doc
            
            # Save and reload
            save_documents_for_year(self.current_tax_year, self.documents)
            self.load_documents()
            self.set_status(f"Document '{updated_doc['name']}' updated")
        
        # Open document editor dialog
        DocumentEditor(self.root, doc, save_callback)
    
    def open_add_document_dialog(self):
        """Open dialog to add a new document"""
        def save_callback(new_doc):
            # Add document to list
            self.documents.append(new_doc)
            
            # Save and reload
            save_documents_for_year(self.current_tax_year, self.documents)
            self.load_documents()
            self.set_status(f"Document '{new_doc['name']}' added")
        
        # Open document editor dialog (with no document)
        DocumentEditor(self.root, None, save_callback)

    def delete_document(self, index):
        """Delete a document after confirmation"""
        doc = self.documents[index]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{doc.get('name')}'?"):
            doc_name = doc.get('name', 'Document')
            del self.documents[index]
            save_documents_for_year(self.current_tax_year, self.documents)
            self.load_documents()
            self.set_status(f"Deleted document '{doc_name}'")
    
    def go_to_previous_year(self):
        """Navigate to previous tax year"""
        self.current_tax_year -= 1
        self.update_year_display()
        self.load_documents()
    
    def go_to_next_year(self):
        """Navigate to next tax year"""
        self.current_tax_year += 1
        self.update_year_display()
        self.load_documents()
    
    def update_year_display(self):
        """Update the year display in the UI"""
        self.year_banner.config(text=f"Tax Year: {self.current_tax_year} (Due {self.current_tax_year + 1})")
        self.current_year_label.config(text=f"Tax Year {self.current_tax_year}")
    
    def import_last_year_documents(self):
        """Import documents from previous year"""
        count, message = import_from_last_year(self.current_tax_year)
        
        if count > 0:
            messagebox.showinfo("Import", message)
            self.load_documents()
            self.set_status(message)
        else:
            messagebox.showinfo("Import", message)
    
    def open_website(self, index):
        """Open document website in browser"""
        website = self.documents[index].get("website", "")
        if website:
            if not website.startswith(("http://", "https://")):
                website = "https://" + website
            webbrowser.open(website)
            self.set_status(f"Opening website: {website}")
        else:
            doc_name = self.documents[index].get("name", "Document")
            self.set_status(f"No website defined for '{doc_name}'")
    
    def set_status(self, message):
        """Set status bar message"""
        self.status_message.set(message)
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        # Ctrl+N for new document
        self.root.bind("<Control-n>", lambda e: self.open_add_document_dialog())
        
        # Delete key to delete selected document
        self.root.bind("<Delete>", self.delete_selected_document)
        
        # F5 to refresh
        self.root.bind("<F5>", lambda e: self.load_documents())
    
    def delete_selected_document(self, event=None):
        """Delete the selected document"""
        selection = self.tree.selection()
        if not selection:
            return
            
        item = selection[0]
        
        # Ignore section headers
        if not self.tree.parent(item):
            return
            
        # Get document index
        tags = self.tree.item(item, "tags")
        if tags:
            tag = tags[0]
            if tag.startswith("index:"):
                index = int(tag.split(":")[1])
                self.delete_document(index)
    
    def format_date(self, date_string):
        """Format date for display"""
        if not date_string:
            return "No date set"
        try:
            date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
            return date.strftime("%b %d, %Y")
        except ValueError:
            return date_string
    
    def configure_basic_styles(self):
        """Configure basic ttk styles based on theme data"""
        # Basic frame style
        self.style.configure("TFrame", background=self.theme_data.get("background"))
        
        # Basic label style
        self.style.configure("TLabel", 
                          background=self.theme_data.get("background"), 
                          foreground=self.theme_data.get("foreground"))
        
        # Basic button style
        self.style.configure("TButton", 
                          background=self.theme_data.get("accent"), 
                          foreground=self.theme_data.get("accent_fg"))
        
        # Basic entry style
        self.style.configure("TEntry", 
                          fieldbackground=self.theme_data.get("entry_bg"), 
                          foreground=self.theme_data.get("entry_fg"))
        
        # Primary button style
        self.style.configure("Primary.TButton", 
                           background=self.theme_data.get("accent"), 
                           foreground=self.theme_data.get("accent_fg"))
        
        # Header label style
        self.style.configure("Header.TLabel", 
                           font=("Segoe UI", 16, "bold"), 
                           foreground=self.theme_data.get("header_fg"),
                           background=self.theme_data.get("background"))
        
        # Year banner style
        self.style.configure("YearBanner.TLabel", 
                           font=("Segoe UI", 14, "bold"), 
                           background=self.theme_data.get("accent"), 
                           foreground=self.theme_data.get("accent_fg"),
                           padding=10)
        
        # Treeview styles
        self.style.configure("Treeview", 
                           background=self.theme_data.get("entry_bg"),
                           foreground=self.theme_data.get("entry_fg"),
                           fieldbackground=self.theme_data.get("entry_bg"))
        
        self.style.configure("Treeview.Heading", 
                           background=self.theme_data.get("header_bg"),
                           foreground=self.theme_data.get("header_fg"),
                           font=("Segoe UI", 9, "bold"))

    def apply_theme_to_widget(self, widget, widget_type="frame"):
        """Apply theme colors to a specific widget"""
        try:
            if widget_type == "background" or widget_type == "frame":
                widget.configure(background=self.theme_data.get("background"))
            elif widget_type == "button":
                widget.configure(background=self.theme_data.get("accent"))
                widget.configure(foreground=self.theme_data.get("accent_fg"))
            elif widget_type == "entry":
                widget.configure(background=self.theme_data.get("entry_bg"))
                widget.configure(foreground=self.theme_data.get("entry_fg"))
            elif widget_type == "combobox":
                # For ttk.Combobox, apply theme to underlying tk parts
                widget.configure(background=self.theme_data.get("entry_bg"))
                widget.configure(foreground=self.theme_data.get("entry_fg"))
                # Try direct access to the dropdown (may not work on all platforms)
                try:
                    widget_name = str(widget)
                    self.root.tk.eval(f"{widget_name} configure -background {self.theme_data.get('entry_bg')}")
                    # Handle special elements if possible
                    self.root.tk.eval(f"{widget_name} configure -foreground {self.theme_data.get('entry_fg')}")
                except:
                    pass
        except (tk.TclError, AttributeError) as e:
            # Some widgets might not support all configurations
            print(f"Could not apply theme to widget: {e}")

    def apply_theme_to_all_widgets(self):
        # Apply theme to the main window
        self.root.configure(bg=self.theme_data.get("background"))

        # Update ttk styles
        style = ttk.Style()
        style.theme_use('clam')

        # Configure Treeview
        style.configure("Treeview",
                        background=self.theme_data.get("entry_bg"),
                        fieldbackground=self.theme_data.get("entry_bg"),
                        foreground=self.theme_data.get("entry_fg"))
        style.configure("Treeview.Heading",
                        background=self.theme_data.get("header_bg"),
                        foreground=self.theme_data.get("header_fg"),
                        relief="flat")
        style.map("Treeview",
                  background=[("selected", self.theme_data.get("selected"))],
                  foreground=[("selected", self.theme_data.get("selected_fg"))])

        # Configure other ttk widgets
        style.configure("TFrame", background=self.theme_data.get("background"))
        style.configure("TLabel", background=self.theme_data.get("background"), foreground=self.theme_data.get("foreground"))
        style.configure("TButton", background=self.theme_data.get("button_bg"), foreground=self.theme_data.get("button_fg"))
        style.configure("TEntry", fieldbackground=self.theme_data.get("entry_bg"), foreground=self.theme_data.get("entry_fg"))

        # Configure header styles
        style.configure("Header.TLabel",
                        font=('Helvetica', 16, 'bold'),
                        background=self.theme_data.get("background"),
                        foreground=self.theme_data.get("foreground"))

        style.configure("YearBanner.TLabel",
                        font=('Helvetica', 14, 'bold'),
                        background=self.theme_data.get("accent"),
                        foreground=self.theme_data.get("foreground"))

        # Update specific widgets
        if hasattr(self, 'tree'):
            self.tree.tag_configure('even', background=self.theme_data.get("even_row"))
            self.tree.tag_configure('odd', background=self.theme_data.get("odd_row"))

        if hasattr(self, 'status_bar'):
            self.status_bar.config(bg=self.theme_data.get("status_bg"), fg=self.theme_data.get("status_fg"))

        # Update year banner
        if hasattr(self, 'year_banner'):
            self.year_banner.configure(style="YearBanner.TLabel")

        # Update menu colors
        if hasattr(self, 'menu_bar'):
            self.menu_bar.config(bg=self.theme_data.get("menu_bg"), fg=self.theme_data.get("menu_fg"))
            for menu_name in ['file_menu', 'edit_menu', 'view_menu', 'help_menu']:
                if hasattr(self, menu_name):
                    menu = getattr(self, menu_name)
                    menu.config(bg=self.theme_data.get("menu_bg"), fg=self.theme_data.get("menu_fg"))

        # Force update of all widgets
        self.root.update_idletasks()



