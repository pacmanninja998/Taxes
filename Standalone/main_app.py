#!/usr/bin/env python3
import tkinter as tk
import argparse
import sys
import os
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
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icon.ico")
        
        # Try to set an icon based on platform
        if sys.platform == "win32":
            root.iconbitmap(icon_path)
        elif sys.platform == "darwin":  # macOS
            icon_img = tk.PhotoImage(file=icon_path.replace(".ico", ".png"))
            root.iconphoto(True, icon_img)
        else:  # Linux
            icon_img = tk.PhotoImage(file=icon_path.replace(".ico", ".png"))
            root.iconphoto(True, icon_img)
            
        if args.debug:
            print(f"Set application icon from: {icon_path}")
    except Exception as e:
        if args.debug:
            print(f"Could not set application icon: {e}")
    
    # Initialize the application
    app = TaxDocumentTracker(root)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()