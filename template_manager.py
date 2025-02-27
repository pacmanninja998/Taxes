import os

# Path to the template file
TEMPLATE_PATH = os.path.join('templates', 'tax_tracker.html')

# HTML template with ASCII symbols instead of Unicode
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tax Document Tracker</title>
    <link rel="icon" href="/static/favicon.ico">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        
        h1, h2 {
            color: #2c3e50;
            text-align: center;
        }
        
        .tax-year {
            font-size: 1.8rem;
            background-color: #3498db;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .view-selector {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .view-selector label {
            margin-right: 10px;
            font-weight: bold;
        }
        
        .view-selector select {
            padding: 8px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }
        
        .document-list {
            max-height: 400px;
            overflow-y: auto;
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
        }
        
        .add-form {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr auto;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        input, button, select {
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        button {
            background-color: #3498db;
            color: white;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        button:hover {
            background-color: #2980b9;
        }
        
        .action-buttons {
            display: flex;
            gap: 5px;
        }
        
        .edit-btn {
            background-color: #f39c12;
        }
        
        .delete-btn {
            background-color: #e74c3c;
        }
        
        a {
            color: #3498db;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        .year-selector {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .year-selector button {
            padding: 8px 15px;
        }
        
        #currentTaxYear {
            font-size: 1.2rem;
            font-weight: bold;
        }
        
        .checkbox {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        .header-row {
            display: flex;
            background-color: #f2f2f2;
            font-weight: bold;
            padding: 12px 15px;
            border-bottom: 1px solid #ddd;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .section-header {
            background-color: #e0e0e0;
            padding: 10px;
            margin-top: 10px;
            font-weight: bold;
            border-top: 1px solid #ddd;
            border-bottom: 1px solid #ddd;
        }
        
        .document-row {
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            align-items: center;
        }
        
        .document-row:hover {
            background-color: #f5f5f5;
        }
        
        .document-completed {
            text-decoration: line-through;
            color: #7f8c8d;
        }
        
        .checkbox-container {
            width: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .document-name {
            flex: 2;
        }
        
        .document-date {
            flex: 1;
            min-width: 120px;
        }
        
        .document-prev-date {
            flex: 1;
            min-width: 120px;
        }
        
        .document-actions {
            width: 120px;
            text-align: right;
        }
        
        .date-passed {
            color: #27ae60;
            font-weight: bold;
        }
        
        .notification {
            background-color: #d4edda;
            color: #155724;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 15px;
            display: none;
        }
        
        .shutdown-btn {
            background-color: #e74c3c;
            color: white;
            padding: 8px 15px;
            margin-top: 20px;
        }
        
        .footer {
            text-align: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <h1>Tax Document Tracker</h1>
    
    <div class="container">
        <div class="tax-year" id="taxYearBanner">
            Tax Year: <span id="displayTaxYear">2024</span> (Due 2025)
        </div>
        
        <div class="year-selector">
            <button id="prevYear">&larr; Previous Year</button>
            <span id="currentTaxYear">Tax Year 2024</span>
            <button id="nextYear">Next Year &rarr;</button>
        </div>
        
        <div class="data-management">
            <button id="importLastYearBtn">Import Last Year's Documents</button>
        </div>
        
        <div id="notification" class="notification"></div>
        
        <h2>Add New Document</h2>
        <form id="addDocumentForm" class="add-form">
            <input type="text" id="documentName" placeholder="Document Name" required>
            <input type="text" id="website" placeholder="Website URL (optional)">
            <input type="date" id="expectedDate" placeholder="Expected Date">
            <button type="submit">Add Document</button>
        </form>
        
        <div class="view-selector">
            <label for="viewMode">View Mode:</label>
            <select id="viewMode">
                <option value="all">All Documents</option>
                <option value="needed">Needed Documents</option>
                <option value="completed">Completed Documents</option>
            </select>
        </div>
        
        <div id="documentListContainer" class="document-list">
            <div class="header-row">
                <div class="checkbox-container"></div>
                <div class="document-name">Document</div>
                <div class="document-date">Expected Date</div>
                <div class="document-prev-date">Last Year's Date</div>
                <div class="document-actions">Actions</div>
            </div>
            <!-- Documents will be added here dynamically -->
        </div>
    </div>
    
    <div class="footer">
        <form action="/shutdown" method="post" onsubmit="return confirm('Are you sure you want to shut down the server?');">
            <button type="submit" class="shutdown-btn">Shutdown Server</button>
        </form>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Initialize with current tax year (previous calendar year)
            let currentTaxYear;
            let currentViewMode = 'all';
            const notification = document.getElementById('notification');
            
            // Show notification
            function showNotification(message, isSuccess = true) {
                notification.textContent = message;
                notification.style.display = 'block';
                notification.style.backgroundColor = isSuccess ? '#d4edda' : '#f8d7da';
                notification.style.color = isSuccess ? '#155724' : '#721c24';
                
                setTimeout(() => {
                    notification.style.display = 'none';
                }, 3000);
            }
            
            // API Functions
            
            // Get the current tax year from server
            async function fetchCurrentTaxYear() {
                try {
                    const response = await fetch('/api/current-year');
                    const data = await response.json();
                    return data.year;
                } catch (error) {
                    console.error('Error fetching current tax year:', error);
                    // Default to previous calendar year
                    const currentDate = new Date();
                    return currentDate.getMonth() < 3 ? 
                          currentDate.getFullYear() - 1 : 
                          currentDate.getFullYear();
                }
            }
            
            // Get documents for a specific tax year
            async function fetchDocumentsForYear(year) {
                try {
                    const response = await fetch(`/api/documents/${year}`);
                    return await response.json();
                } catch (error) {
                    console.error(`Error fetching documents for ${year}:`, error);
                    showNotification(`Error loading documents for ${year}`, false);
                    return [];
                }
            }
            
            // Save documents for a specific tax year
            async function saveDocumentsForYear(year, documents) {
                try {
                    const response = await fetch(`/api/documents/${year}`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(documents),
                    });
                    const result = await response.json();
                    if (result.success) {
                        showNotification(`Data for ${year} saved successfully`);
                    }
                    return documents;
                } catch (error) {
                    console.error(`Error saving documents for ${year}:`, error);
                    showNotification('Error saving data', false);
                    return documents;
                }
            }
            
            // Update the tax year display
            function updateTaxYearDisplay() {
                document.getElementById('displayTaxYear').textContent = currentTaxYear;
                document.getElementById('currentTaxYear').textContent = `Tax Year ${currentTaxYear}`;
            }
            
            // Data Management Functions
            
            // Import documents from previous year
            async function importLastYearDocuments() {
                const prevYear = currentTaxYear - 1;
                const prevYearDocuments = await fetchDocumentsForYear(prevYear);
                
                if (!prevYearDocuments || prevYearDocuments.length === 0) {
                    showNotification(`No documents found for ${prevYear}`, false);
                    return;
                }
                
                // Get current year documents
                let currentDocuments = await fetchDocumentsForYear(currentTaxYear);
                const currentDocNames = currentDocuments.map(doc => doc.name);
                
                // Only add documents that don't already exist
                let newDocsCount = 0;
                
                prevYearDocuments.forEach(doc => {
                    if (!currentDocNames.includes(doc.name)) {
                        newDocsCount++;
                        currentDocuments.push({
                            name: doc.name,
                            website: doc.website,
                            expectedDate: doc.expectedDate,
                            actualDate: '',
                            previousYearDate: doc.actualDate || doc.expectedDate,
                            completed: false
                        });
                    }
                });
                
                if (newDocsCount > 0) {
                    await saveDocumentsForYear(currentTaxYear, currentDocuments);
                    showNotification(`Imported ${newDocsCount} documents from ${prevYear}`);
                    loadDocuments();
                } else {
                    showNotification('No new documents to import');
                }
            }
            
            // UI Functions
            
            // Add a new document
            async function addDocument(e) {
                e.preventDefault();
                
                const documentName = document.getElementById('documentName').value;
                const website = document.getElementById('website').value;
                const expectedDate = document.getElementById('expectedDate').value;
                
                // Get existing documents for the current tax year
                let documents = await fetchDocumentsForYear(currentTaxYear);
                
                // Add new document
                documents.push({
                    name: documentName,
                    website: website,
                    expectedDate: expectedDate,
                    actualDate: '',
                    previousYearDate: '',
                    completed: false
                });
                
                // Save updated documents
                await saveDocumentsForYear(currentTaxYear, documents);
                
                // Reset form and refresh the list
                document.getElementById('addDocumentForm').reset();
                loadDocuments();
            }
            
            // Load documents for the current tax year
            async function loadDocuments() {
                const documentListContainer = document.getElementById('documentListContainer');
                
                // Preserve the header row
                const headerRow = documentListContainer.querySelector('.header-row');
                documentListContainer.innerHTML = '';
                documentListContainer.appendChild(headerRow);
                
                const documents = await fetchDocumentsForYear(currentTaxYear);
                const prevYearDocuments = await fetchDocumentsForYear(currentTaxYear - 1);
                
                // Update previous year dates if available
                let documentsUpdated = false;
                documents.forEach((doc, index) => {
                    // Look for matching document from previous year
                    const prevYearDoc = prevYearDocuments.find(prevDoc => prevDoc.name === doc.name);
                    
                    // If current doc doesn't have previousYearDate but we found a match, add it
                    if (!doc.previousYearDate && prevYearDoc && (prevYearDoc.actualDate || prevYearDoc.expectedDate)) {
                        doc.previousYearDate = prevYearDoc.actualDate || prevYearDoc.expectedDate;
                        // Save the updated document
                        documents[index] = doc;
                        documentsUpdated = true;
                    }
                });
                
                // Save any updates
                if (documentsUpdated) {
                    await saveDocumentsForYear(currentTaxYear, documents);
                }
                
                // Filter documents based on view mode
                let neededDocuments = [];
                let completedDocuments = [];
                
                if (currentViewMode === 'all' || currentViewMode === 'needed') {
                    neededDocuments = documents.filter(doc => !doc.completed);
                }
                
                if (currentViewMode === 'all' || currentViewMode === 'completed') {
                    completedDocuments = documents.filter(doc => doc.completed);
                }
                
                // Create the needed documents section if applicable
                if (neededDocuments.length > 0 && (currentViewMode === 'all' || currentViewMode === 'needed')) {
                    const neededHeader = document.createElement('div');
                    neededHeader.className = 'section-header';
                    neededHeader.textContent = 'Needed Documents';
                    documentListContainer.appendChild(neededHeader);
                    
                    neededDocuments.forEach((doc, index) => {
                        createDocumentElement(doc, documents.indexOf(doc), false);
                    });
                }
                
                // Create the completed documents section if applicable
                if (completedDocuments.length > 0 && (currentViewMode === 'all' || currentViewMode === 'completed')) {
                    const completedHeader = document.createElement('div');
                    completedHeader.className = 'section-header';
                    completedHeader.textContent = 'Completed Documents';
                    documentListContainer.appendChild(completedHeader);
                    
                    completedDocuments.forEach((doc, index) => {
                        createDocumentElement(doc, documents.indexOf(doc), true);
                    });
                }
                
                // If no documents found, show a message
                if (documents.length === 0) {
                    const noDocsMessage = document.createElement('div');
                    noDocsMessage.textContent = 'No documents found for this tax year.';
                    noDocsMessage.style.padding = '15px';
                    noDocsMessage.style.textAlign = 'center';
                    documentListContainer.appendChild(noDocsMessage);
                }
            }
            
            // Create a document element
            function createDocumentElement(doc, index, isCompletedSection) {
                const documentRow = document.createElement('div');
                documentRow.className = 'document-row';
                if (doc.completed && !isCompletedSection) {
                    documentRow.classList.add('document-completed');
                }
                
                // Create checkbox
                const checkboxContainer = document.createElement('div');
                checkboxContainer.className = 'checkbox-container';
                
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'checkbox';
                checkbox.checked = doc.completed;
                checkbox.dataset.index = index;
                checkbox.addEventListener('change', toggleDocumentStatus);
                
                checkboxContainer.appendChild(checkbox);
                
                // Create document name/link
                const documentName = document.createElement('div');
                documentName.className = 'document-name';
                
                if (doc.website) {
                    const link = document.createElement('a');
                    link.href = doc.website.startsWith('http') ? doc.website : `https://${doc.website}`;
                    link.textContent = doc.name;
                    link.target = '_blank';
                    documentName.appendChild(link);
                } else {
                    documentName.textContent = doc.name;
                }
                
                // Create expected date display
                const dateElement = document.createElement('div');
                dateElement.className = 'document-date';
                
                // Check if the expected date has passed
                const expectedDatePassed = doc.expectedDate && new Date(doc.expectedDate) < new Date();
                
                if (expectedDatePassed) {
                    dateElement.classList.add('date-passed');
                }
                
                const expectedDateFormatted = doc.expectedDate ? formatDate(doc.expectedDate) : 'No date set';
                dateElement.textContent = expectedDateFormatted;
                
                // Create previous year date display
                const prevDateElement = document.createElement('div');
                prevDateElement.className = 'document-prev-date';
                
                const prevYearDateFormatted = doc.previousYearDate ? formatDate(doc.previousYearDate) : 'No data';
                prevDateElement.textContent = prevYearDateFormatted;
                
                // Create action buttons
                const actionButtons = document.createElement('div');
                actionButtons.className = 'document-actions';
                
                const editButton = document.createElement('button');
                editButton.className = 'edit-btn';
                editButton.textContent = 'Edit';
                editButton.dataset.index = index;
                editButton.addEventListener('click', editDocument);
                
                const deleteButton = document.createElement('button');
                deleteButton.className = 'delete-btn';
                deleteButton.textContent = 'Delete';
                deleteButton.dataset.index = index;
                deleteButton.addEventListener('click', deleteDocument);
                
                actionButtons.appendChild(editButton);
                actionButtons.appendChild(deleteButton);
                
                // Add all elements to document row
                documentRow.appendChild(checkboxContainer);
                documentRow.appendChild(documentName);
                documentRow.appendChild(dateElement);
                documentRow.appendChild(prevDateElement);
                documentRow.appendChild(actionButtons);
                
                // Make the entire row clickable to toggle status (except buttons)
                documentRow.addEventListener('click', function(e) {
                    // Avoid toggling when clicking on the checkbox or buttons
                    if (e.target !== checkbox && 
                        e.target !== editButton && 
                        e.target !== deleteButton && 
                        !editButton.contains(e.target) &&
                        !deleteButton.contains(e.target)) {
                        checkbox.checked = !checkbox.checked;
                        const event = new Event('change');
                        checkbox.dispatchEvent(event);
                    }
                });
                
                // Add to document list
                document.getElementById('documentListContainer').appendChild(documentRow);
            }
            
            // Toggle document status (completed/needed)
            async function toggleDocumentStatus(e) {
                const index = parseInt(e.target.dataset.index);
                const documents = await fetchDocumentsForYear(currentTaxYear);
                
                // Toggle completion status
                documents[index].completed = e.target.checked;
                
                // If completed, set actual date to today if not already set
                if (e.target.checked && !documents[index].actualDate) {
                    const today = new Date();
                    const formattedDate = today.toISOString().split('T')[0];
                    documents[index].actualDate = formattedDate;
                }
                
                // Save updated documents
                await saveDocumentsForYear(currentTaxYear, documents);
                
                // Refresh the list
                loadDocuments();
            }
            
            // Format date for display
            function formatDate(dateString) {
                if (!dateString) return 'No date set';
                const date = new Date(dateString);
                return date.toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric'
                });
            }
            
            // Edit a document
            async function editDocument(e) {
                e.stopPropagation(); // Prevent row click event
                const index = e.target.dataset.index;
                const documents = await fetchDocumentsForYear(currentTaxYear);
                const doc = documents[index];
                
                // Populate form with document data
                document.getElementById('documentName').value = doc.name;
                document.getElementById('website').value = doc.website || '';
                document.getElementById('expectedDate').value = doc.expectedDate || '';
                
                // Remove the document from the list
                documents.splice(index, 1);
                await saveDocumentsForYear(currentTaxYear, documents);
                
                // Refresh the list
                loadDocuments();
                
                // Focus on the form
                document.getElementById('documentName').focus();
            }
            
            // Delete a document
            async function deleteDocument(e) {
                e.stopPropagation(); // Prevent row click event
                if (confirm('Are you sure you want to delete this document?')) {
                    const index = e.target.dataset.index;
                    const documents = await fetchDocumentsForYear(currentTaxYear);
                    
                    // Remove the document from the list
                    documents.splice(index, 1);
                    await saveDocumentsForYear(currentTaxYear, documents);
                    
                    // Refresh the list
                    loadDocuments();
                }
            }
            
            // Add event listeners
            document.getElementById('addDocumentForm').addEventListener('submit', addDocument);
            document.getElementById('prevYear').addEventListener('click', async () => {
                currentTaxYear--;
                updateTaxYearDisplay();
                await loadDocuments();
            });
            document.getElementById('nextYear').addEventListener('click', async () => {
                currentTaxYear++;
                updateTaxYearDisplay();
                await loadDocuments();
            });
            document.getElementById('viewMode').addEventListener('change', (e) => {
                currentViewMode = e.target.value;
                loadDocuments();
            });
            document.getElementById('importLastYearBtn').addEventListener('click', importLastYearDocuments);
            
            // Initialize the application
            async function initApp() {
                // Get current tax year from server
                currentTaxYear = await fetchCurrentTaxYear();
                updateTaxYearDisplay();
                await loadDocuments();
            }
            
            initApp();
        });
    </script>
</body>
</html>"""

def create_template_if_needed():
    """Create the HTML template file if it doesn't exist"""
    if not os.path.exists(TEMPLATE_PATH):
        print(f"Creating initial HTML template at {TEMPLATE_PATH}")
        with open(TEMPLATE_PATH, 'w', encoding='utf-8') as f:
            f.write(HTML_TEMPLATE)
        return True
    return False