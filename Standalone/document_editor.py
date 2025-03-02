import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import datetime

class DocumentEditor:
    def __init__(self, parent, document=None, callback=None):
        """Initialize document editor dialog
        
        Args:
            parent: Parent window
            document: Document to edit (None for new document)
            callback: Function to call with document data when saved
        """
        self.parent = parent
        self.document = document or {}  # Empty dict for new document
        self.callback = callback
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Document" if document else "Add Document")
        self.dialog.geometry("500x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Make dialog modal
        self.dialog.focus_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        
        # Create widgets
        self.create_widgets()
        
        # Center dialog on parent
        self.center_on_parent()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Main frame with padding
        main_frame = ttk.Frame(self.dialog, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid
        main_frame.columnconfigure(1, weight=1)
        
        # Form fields
        row = 0
        
        # Document name
        ttk.Label(main_frame, text="Document Name:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.name_var = tk.StringVar(value=self.document.get("name", ""))
        ttk.Entry(main_frame, textvariable=self.name_var).grid(
            row=row, column=1, sticky=tk.EW, pady=5
        )
        
        row += 1
        
        # Website URL
        ttk.Label(main_frame, text="Website URL:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        self.website_var = tk.StringVar(value=self.document.get("website", ""))
        ttk.Entry(main_frame, textvariable=self.website_var).grid(
            row=row, column=1, sticky=tk.EW, pady=5
        )
        
        row += 1
        
        # Expected date
        ttk.Label(main_frame, text="Expected Date:").grid(
            row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
        )
        date_frame = ttk.Frame(main_frame)
        date_frame.grid(row=row, column=1, sticky=tk.W, pady=5)
        
        # Date entry enabled checkbox
        self.use_date_var = tk.BooleanVar(
            value=bool(self.document.get("expectedDate", ""))
        )
        date_check = ttk.Checkbutton(
            date_frame, 
            text="Set expected date", 
            variable=self.use_date_var,
            command=self.toggle_date_entry
        )
        date_check.pack(side=tk.LEFT, padx=(0, 10))
        
        # Date entry widget
        self.expected_date = DateEntry(
            date_frame, 
            width=12, 
            background='darkblue',
            foreground='white', 
            borderwidth=2, 
            date_pattern='yyyy-mm-dd'
        )
        
        # Set date if it exists in document
        if self.document.get("expectedDate"):
            try:
                self.expected_date.set_date(self.document.get("expectedDate"))
                self.expected_date.pack(side=tk.LEFT)
            except:
                # Default to today if date format is invalid
                self.expected_date.set_date(datetime.date.today())
                self.expected_date.pack(side=tk.LEFT)
        else:
            # No date set
            self.expected_date.set_date(datetime.date.today())
            # Don't pack initially if no date
            if self.use_date_var.get():
                self.expected_date.pack(side=tk.LEFT)
        
        row += 1
        
        # Previous year date (display only if editing)
        if self.document:
            ttk.Label(main_frame, text="Previous Year:").grid(
                row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
            )
            prev_date = self.document.get("previousYearDate", "")
            prev_date_str = self.format_date(prev_date) if prev_date else "None"
            ttk.Label(main_frame, text=prev_date_str).grid(
                row=row, column=1, sticky=tk.W, pady=5
            )
            
            row += 1
        
        # Completed checkbox (only show if editing existing document)
        if self.document:
            ttk.Label(main_frame, text="Completed:").grid(
                row=row, column=0, sticky=tk.W, padx=(0, 10), pady=5
            )
            self.completed_var = tk.BooleanVar(value=self.document.get("completed", False))
            ttk.Checkbutton(main_frame, variable=self.completed_var).grid(
                row=row, column=1, sticky=tk.W, pady=5
            )
            
            row += 1
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ttk.Button(
            button_frame, 
            text="Save",
            command=self.save
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Cancel",
            command=self.cancel
        ).pack(side=tk.LEFT, padx=5)
    
    def toggle_date_entry(self):
        """Toggle date entry widget"""
        if self.use_date_var.get():
            # Enable date entry
            self.expected_date.pack(side=tk.LEFT)
        else:
            # Disable date entry
            self.expected_date.pack_forget()
    
    def clear_expected_date(self):
        """Clear the expected date field"""
        self.expected_date.set_date("")
    
    def save(self):
        """Save the document and close the dialog"""
        name = self.name_var.get().strip()
        
        if not name:
            self.show_error("Document name cannot be empty")
            return
        
        # Get date as string (or empty string if not using)
        if self.use_date_var.get():
            try:
                date_str = self.expected_date.get_date().isoformat()
            except:
                date_str = ""
        else:
            date_str = ""
        
        # Create document data
        document = {
            "name": name,
            "website": self.website_var.get().strip(),
            "expectedDate": date_str,
        }
        
        # Add completed field if it exists (editing mode)
        if hasattr(self, 'completed_var'):
            document["completed"] = self.completed_var.get()
            
            # If marked as completed and no actual date, set to today
            if document["completed"] and not self.document.get("actualDate"):
                document["actualDate"] = datetime.date.today().isoformat()
            else:
                document["actualDate"] = self.document.get("actualDate", "")
        else:
            # New document is not completed by default
            document["completed"] = False
            document["actualDate"] = ""
        
        # Previous year date remains unchanged if editing
        document["previousYearDate"] = self.document.get("previousYearDate", "")
        
        # Call the callback with the document data
        if self.callback:
            self.callback(document)
        
        # Close the dialog
        self.dialog.destroy()
    
    def cancel(self):
        """Close the dialog without saving"""
        self.dialog.destroy()
    
    def show_error(self, message):
        """Show error message"""
        from tkinter import messagebox
        messagebox.showerror("Error", message, parent=self.dialog)
    
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
    
    def format_date(self, date_string):
        """Format date for display"""
        if not date_string:
            return ""
        try:
            date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
            return date.strftime("%b %d, %Y")
        except ValueError:
            return date_string