#!/usr/bin/env python3
import tkinter as tk
import argparse
import sys
from pathlib import Path

# Import the GUI application
from tax_tracker_gui import TaxDocumentTracker

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Tax Document Tracker')
    parser.add_argument('-d', '--debug', action='store_true', help='Run in debug mode with additional logging')
    parser.add_argument('--reset', action='store_true', help='Reset all data (use with caution)')
    args = parser.parse_args()
    
    # Handle reset functionality
    if args.reset:
        data_file = Path.home() / "Documents" / "Tax Doc Helper" / 'tax_documents_data.json'
        if data_file.exists():
            import os
            os.remove(data_file)
            print(f"Data file {data_file} has been reset.")
    
    # Configure debug mode
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG, 
                           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logging.debug("Debug mode enabled")
    
    # Initialize the application
    root = tk.Tk()
    
    # Set application icon if available
    try:
        # Try to set an icon (on Windows you'd use .ico, on macOS .icns)
        if sys.platform == "win32":
            root.iconbitmap("tax_icon.ico")
        elif sys.platform == "darwin":  # macOS
            from tkinter.ttk import Frame
            img = tk.Image("photo", file="tax_icon.png")
            root.tk.call('wm', 'iconphoto', root._w, img)
    except Exception as e:
        if args.debug:
            print(f"Could not set application icon: {e}")
    
    # Initialize the application
    app = TaxDocumentTracker(root)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
