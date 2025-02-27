import json
import os

# Constants
DATA_FILE = 'tax_documents_data.json'

def load_all_data():
    """Load all document data from file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding {DATA_FILE}, returning empty data")
    return {}

def save_all_data(data):
    """Save all document data to file"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def get_documents_for_year(year):
    """Get documents for a specific tax year"""
    all_data = load_all_data()
    year_str = str(year)
    if year_str in all_data:
        return all_data[year_str]
    return []

def save_documents_for_year(year, documents):
    """Save documents for a specific tax year"""
    all_data = load_all_data()
    all_data[str(year)] = documents
    save_all_data(all_data)
    return True
