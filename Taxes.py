from flask import Flask
import os
import sys
import webbrowser
import threading
import time

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from routes import register_routes
from template_manager import create_template_if_needed

# Create the Flask application
app = Flask(__name__)

# Register routes
register_routes(app)

def open_browser():
    """Opens the web browser to the app's URL after a short delay."""
    time.sleep(1)  # Give the server a moment to start
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == '__main__':
    # Ensure the templates folder exists
    if not os.path.exists('templates'):
        os.makedirs('templates')

    # Create the HTML template file if it doesn't exist
    create_template_if_needed()

    print("Starting Tax Document Tracker server on http://127.0.0.1:5000")
    print("Press Ctrl+C to stop the server")

    # Start the browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()

    app.run(debug=False) #Disable debug mode for production
