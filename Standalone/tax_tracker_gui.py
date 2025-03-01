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

# Get user's Documents folder and create our app directory
USER_DOCS = Path.home() / "Documents" / "Tax Doc Helper"
if not USER_DOCS.exists():
    USER_DOCS.mkdir(parents=True)

# Constants
DATA_FILE = USER_DOCS / 'tax_documents_data.json'

class TaxDocumentTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Tax Document Tracker")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize variables
        self.current_tax_year = self.get_current_tax_year()
        self.current_view_mode = tk.StringVar(value="all")
        self.documents = []
        self.status_message = tk.StringVar()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create and configure styles
        self.configure_styles()
        
        # Create the GUI components
        self.create_header()
        self.create_year_selector()
        self.create_data_management()
        self.create_add_document_button()
        self.create_view_selector()
        self.create_document_list()
        self.create_status_bar()
        
        # Load documents for current year
        self.load_documents()
        
        # Bind keyboard shortcuts
        self.bind_shortcuts()

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

    def create_header(self):
        """Create the application header"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="Tax Document Tracker", style="Header.TLabel")
        title_label.pack(side=tk.LEFT)
        
        # Tax year banner
        self.year_banner = ttk.Label(
            self.main_frame, 
            text=f"Tax Year: {self.current_tax_year} (Due {self.current_tax_year + 1})",
            style="YearBanner.TLabel",
            anchor="center"
        )
        self.year_banner.pack(fill=tk.X, pady=(0, 20))

    def create_year_selector(self):
        """Create the year selector controls"""
        year_frame = ttk.Frame(self.main_frame)
        year_frame.pack(fill=tk.X, pady=(0, 20))
        
        prev_year_btn = ttk.Button(
            year_frame, 
            text="← Previous Year",
            command=self.go_to_previous_year
        )
        prev_year_btn.pack(side=tk.LEFT)
        
        self.current_year_label = ttk.Label(
            year_frame, 
            text=f"Tax Year {self.current_tax_year}",
            font=("Segoe UI", 12, "bold")
        )
        self.current_year_label.pack(side=tk.LEFT, expand=True)
        
        next_year_btn = ttk.Button(
            year_frame, 
            text="Next Year →",
            command=self.go_to_next_year
        )
        next_year_btn.pack(side=tk.RIGHT)

    def create_data_management(self):
        """Create data management controls"""
        data_frame = ttk.Frame(self.main_frame)
        data_frame.pack(fill=tk.X, pady=(0, 20))
        
        import_btn = ttk.Button(
            data_frame, 
            text="Import Last Year's Documents",
            command=self.import_last_year_documents
        )
        import_btn.pack(side=tk.LEFT)

    def create_add_document_button(self):
        """Create button to add new documents"""
        # Button frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add document button
        add_btn = ttk.Button(
            button_frame, 
            text="Add New Document",
            command=self.open_add_document_dialog,
            style="Primary.TButton"
        )
        add_btn.pack(side=tk.LEFT)

    def create_view_selector(self):
        """Create view mode selector"""
        view_frame = ttk.Frame(self.main_frame)
        view_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(view_frame, text="View Mode:").pack(side=tk.LEFT, padx=(0, 10))
        
        view_combo = ttk.Combobox(
            view_frame, 
            textvariable=self.current_view_mode,
            values=["all", "needed", "completed"],
            state="readonly",
            width=15
        )
        view_combo.pack(side=tk.LEFT)
        view_combo.bind("<<ComboboxSelected>>", lambda e: self.load_documents())

    def create_document_list(self):
        """Create the document list area"""
        # Container frame for the list
        list_container = ttk.Frame(self.main_frame, relief=tk.GROOVE, borderwidth=1)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # Create Treeview widget
        columns = ("completed", "name", "expected_date", "previous_date", "website")
        self.tree = ttk.Treeview(list_container, columns=columns, show="headings", selectmode="browse")
        
        # Define headings
        self.tree.heading("completed", text="✓")
        self.tree.heading("name", text="Document")
        self.tree.heading("expected_date", text="Expected Date")
        self.tree.heading("previous_date", text="Last Year's Date")
        self.tree.heading("website", text="Website")
        
        # Define columns
        self.tree.column("completed", width=40, anchor=tk.CENTER)
        self.tree.column("name", width=250, anchor=tk.W)
        self.tree.column("expected_date", width=120, anchor=tk.CENTER)
        self.tree.column("previous_date", width=120, anchor=tk.CENTER)
        self.tree.column("website", width=200, anchor=tk.W)
        
        # Create scrollbars
        vsb = ttk.Scrollbar(list_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(list_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)  # Right click

    def load_documents(self):
        """Load documents for current tax year and update the display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Load documents
        self.documents = self.get_documents_for_year(self.current_tax_year)
        
        # Filter documents based on view mode
        view_mode = self.current_view_mode.get()
        
        needed_documents = []
        completed_documents = []
        
        if view_mode == "all" or view_mode == "needed":
            needed_documents = [doc for doc in self.documents if not doc.get("completed", False)]
        
        if view_mode == "all" or view_mode == "completed":
            completed_documents = [doc for doc in self.documents if doc.get("completed", False)]
        
        # Add needed documents section
        if needed_documents:
            needed_header = self.tree.insert("", "end", text="Needed Documents", 
                                          open=True, tags=("section",))
            
            for i, doc in enumerate(needed_documents):
                item_id = self.tree.insert(
                    needed_header, 
                    "end", 
                    values=(
                        "✓" if doc.get("completed", False) else "",
                        doc.get("name", ""),
                        self.format_date(doc.get("expectedDate", "")),
                        self.format_date(doc.get("previousYearDate", "")),
                        doc.get("website", "")
                    ),
                    tags=("completed" if doc.get("completed", False) else "needed",)
                )
                # Store the document index in the item
                self.tree.item(item_id, tags=(f"index:{self.documents.index(doc)}",))
        
        # Add completed documents section
        if completed_documents:
            completed_header = self.tree.insert("", "end", text="Completed Documents", 
                                             open=True, tags=("section",))
            
            for i, doc in enumerate(completed_documents):
                item_id = self.tree.insert(
                    completed_header, 
                    "end", 
                    values=(
                        "✓",
                        doc.get("name", ""),
                        self.format_date(doc.get("expectedDate", "")),
                        self.format_date(doc.get("previousYearDate", "")),
                        doc.get("website", "")
                    ),
                    tags=("completed",)
                )
                # Store the document index in the item
                self.tree.item(item_id, tags=(f"index:{self.documents.index(doc)}",))
    
    def on_item_double_click(self, event):
        """Handle double click on an item"""
        item = self.tree.identify('item', event.x, event.y)
        if not item or self.tree.parent(item) == "":  # Ignore clicks on headers
            return
            
        # Toggle document status
        self.toggle_document_status(item)
    
    def show_context_menu(self, event):
        """Show context menu on right click"""
        item = self.tree.identify('item', event.x, event.y)
        if not item or self.tree.parent(item) == "":  # Ignore clicks on headers
            return
            
        # Select the item that was right-clicked
        self.tree.selection_set(item)
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        
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
        self.documents[index]["completed"] = not self.documents[index].get("completed", False)
        
        # If completed, set actual date to today if not already set
        if self.documents[index]["completed"] and not self.documents[index].get("actualDate"):
            today = datetime.date.today().isoformat()
            self.documents[index]["actualDate"] = today
            
            # Update status message
            doc_name = self.documents[index].get("name", "Document")
            self.set_status(f"Marked '{doc_name}' as completed")
        else:
            # Update status message
            doc_name = self.documents[index].get("name", "Document")
            self.set_status(f"Marked '{doc_name}' as not completed")
        
        # Save and reload
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
    
    def open_website(self, index):
        """Open document website in browser"""
        website = self.documents[index].get("website", "")
        if website:
            if not website.startswith(("http://", "https://")):
                website = "https://" + website
            webbrowser.open(website)
            self.set_status(f"Opening website: {website}")
    
    def format_date(self, date_string):
        """Format date for display"""
        if not date_string:
            return "No date set"
        try:
            date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
            return date.strftime("%b %d, %Y")
        except ValueError:
            return date_string
    
    def open_website(self, index):
        """Open document website in browser"""
        website = self.documents[index].get("website", "")
        if website:
            if not website.startswith(("http://", "https://")):
                website = "https://" + website
            webbrowser.open(website)
    
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
        
        if view_mode == "all" or view_mode == "needed":
            needed_documents = [doc for doc in self.documents if not doc.get("completed", False)]
        
        if view_mode == "all" or view_mode == "completed":
            completed_documents = [doc for doc in self.documents if doc.get("completed", False)]
        
        # Add needed documents section
        if needed_documents:
            needed_header = self.tree.insert("", "end", text="Needed Documents", 
                                          open=True, tags=("section",))
            
            for i, doc in enumerate(needed_documents):
                item_id = self.tree.insert(
                    needed_header, 
                    "end", 
                    values=(
                        "✓" if doc.get("completed", False) else "",
                        doc.get("name", ""),
                        self.format_date(doc.get("expectedDate", "")),
                        self.format_date(doc.get("previousYearDate", "")),
                        doc.get("website", "")
                    ),
                    tags=("needed",)
                )
                # Store the document index in the item
                self.tree.item(item_id, tags=(f"index:{self.documents.index(doc)}",))
        
        # Add completed documents section
        if completed_documents:
            completed_header = self.tree.insert("", "end", text="Completed Documents", 
                                             open=True, tags=("section",))
            
            for i, doc in enumerate(completed_documents):
                item_id = self.tree.insert(
                    completed_header, 
                    "end", 
                    values=(
                        "✓",
                        doc.get("name", ""),
                        self.format_date(doc.get("expectedDate", "")),
                        self.format_date(doc.get("previousYearDate", "")),
                        doc.get("website", "")
                    ),
                    tags=("completed",)
                )
                # Store the document index in the item
                self.tree.item(item_id, tags=(f"index:{self.documents.index(doc)}",))
        
        # Show message if no documents found
        if not self.documents:
            self.set_status(f"No documents found for tax year {self.current_tax_year}")
        else:
            total = len(self.documents)
            completed = len(completed_documents)
            self.set_status(f"Loaded {total} documents ({completed} completed) for tax year {self.current_tax_year}")
    
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
    
    def create_status_bar(self):
        """Create status bar at the bottom of the window"""
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, padding=(5, 2))
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        status_label = ttk.Label(status_frame, textvariable=self.status_message, anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X)
        
        # Initial status message
        self.set_status(f"Ready - Documents folder: {USER_DOCS}")
    
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
        if self.tree.parent(item) == "":
            return
            
        # Get document index
        tags = self.tree.item(item, "tags")
        if tags:
            tag = tags[0]
            if tag.startswith("index:"):
                index = int(tag.split(":")[1])
                self.delete_document(index)
    
    # Data management functions
    def get_current_tax_year(self):
        """Get the current tax year (previous calendar year if before April)"""
        current_date = datetime.datetime.now()
        return current_date.year - 1 if current_date.month < 4 else current_date.year
    
    def format_date(self, date_string):
        """Format date for display"""
        if not date_string:
            return "No date set"
        try:
            date = datetime.datetime.strptime(date_string, "%Y-%m-%d").date()
            return date.strftime("%b %d, %Y")
        except ValueError:
            return date_string


def main():
    root = tk.Tk()
    app = TaxDocumentTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()