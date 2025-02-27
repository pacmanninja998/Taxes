from flask import render_template, request, jsonify, send_from_directory
import datetime
import os
import sys
import signal
import subprocess
import threading
import time
from data_manager import get_documents_for_year, save_documents_for_year, load_all_data
from pathlib import Path

# Get user's Documents folder path
USER_DOCS = Path.home() / "Documents" / "Tax Doc Helper"

def register_routes(app):
    """Register all application routes"""
    
    @app.route('/')
    def index():
        """Serve the main HTML page"""
        return render_template('tax_tracker.html')

    @app.route('/api/documents/<int:year>', methods=['GET'])
    def get_documents_for_year_api(year):
        """Get documents for a specific tax year"""
        documents = get_documents_for_year(year)
        return jsonify(documents)

    @app.route('/api/documents/all', methods=['GET'])
    def get_all_documents():
        """Get all documents for all years"""
        return jsonify(load_all_data())

    @app.route('/api/documents/<int:year>', methods=['POST'])
    def save_documents_for_year_api(year):
        """Save documents for a specific tax year"""
        success = save_documents_for_year(year, request.json)
        return jsonify({"success": success})

    @app.route('/api/current-year', methods=['GET'])
    def get_current_tax_year():
        """Get the current tax year (previous calendar year if before April)"""
        current_date = datetime.datetime.now()
        current_tax_year = current_date.year - 1 if current_date.month < 4 else current_date.year
        return jsonify({"year": current_tax_year})

    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(os.path.join(app.root_path, 'static'), filename)

    @app.route('/shutdown', methods=['POST'])
    def shutdown():
        """Shutdown the server and kill the process with extreme prejudice"""
        # Return a response immediately
        response = jsonify({"status": "shutting_down"})
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        
        def shutdown_server():
            # Just kill the process directly - as fast as possible
            import os, sys
            # Use os._exit() which doesn't do any cleanup but guarantees termination
            os._exit(0)
        
        # Set an extremely short timer 
        from threading import Timer
        timer = Timer(0.001, shutdown_server)  # 1 millisecond delay
        timer.daemon = True
        timer.start()
        
        return response