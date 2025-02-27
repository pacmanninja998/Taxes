from flask import render_template, request, jsonify, send_from_directory
import datetime
import os
from data_manager import get_documents_for_year, save_documents_for_year, load_all_data

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
        """Shutdown the server"""
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return 'Server shutting down...'