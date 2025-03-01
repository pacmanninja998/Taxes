import json
import os
from pathlib import Path

# Get user's Documents folder and create our app directory
USER_DOCS = Path.home() / "Documents" / "Tax Doc Helper"
if not USER_DOCS.exists():
    USER_DOCS.mkdir(parents=True)

# Constants
DATA_FILE = USER_DOCS / 'tax_documents_data.json'

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

def import_from_last_year(current_year):
    """Import documents from the previous tax year"""
    prev_year = current_year - 1
    prev_year_documents = get_documents_for_year(prev_year)
    
    if not prev_year_documents:
        return 0, "No documents found for the previous year"
    
    # Get current year documents
    current_documents = get_documents_for_year(current_year)
    current_doc_names = [doc.get("name") for doc in current_documents]
    
    # Only add documents that don't already exist
    new_docs_count = 0
    
    for doc in prev_year_documents:
        if doc.get("name") not in current_doc_names:
            new_docs_count += 1
            new_doc = {
                "name": doc.get("name"),
                "website": doc.get("website", ""),
                "expectedDate": doc.get("expectedDate", ""),
                "actualDate": "",
                "previousYearDate": doc.get("actualDate") or doc.get("expectedDate", ""),
                "completed": False
            }
            current_documents.append(new_doc)
    
    if new_docs_count > 0:
        save_documents_for_year(current_year, current_documents)
        return new_docs_count, f"Imported {new_docs_count} documents from tax year {prev_year}"
    else:
        return 0, "No new documents to import"