from flask import Flask
import os
import sys
import webbrowser
import threading
import time
import argparse
from pathlib import Path

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from routes import register_routes
from template_manager import create_template_if_needed, USER_DOCS, force_update_template

def open_browser():
    """Opens the web browser to the app's URL after a short delay."""
    time.sleep(1)  # Give the server a moment to start
    webbrowser.open("http://127.0.0.1:5000")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Tax Document Tracker')
    parser.add_argument('-d', '--debug', action='store_true', help='Run in debug mode with console window')
    parser.add_argument('--update-template', action='store_true', help='Force update the HTML template')
    parser.add_argument('--no-browser', action='store_true', help='Do not automatically open browser')
    args = parser.parse_args()

    # Create the Flask application
    app = Flask(__name__, template_folder=str(USER_DOCS))

    # Register routes
    register_routes(app)

    # Create the HTML template file if it doesn't exist
    create_template_if_needed()
    
    # Force update template if requested
    if args.update_template:
        force_update_template()

    print("Starting Tax Document Tracker server on http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")
    print(f'Document Folder: {USER_DOCS}')
    
    # Start the browser in a separate thread unless --no-browser flag is used
    if not args.no_browser:
        threading.Thread(target=open_browser, daemon=True).start()

    # Run the Flask app
    app.run(debug=args.debug)

if __name__ == '__main__':
    main()