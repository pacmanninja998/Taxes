# Tax Document Tracker

A simple, local web application to help you keep track of tax-related documents throughout the year.

[Download](https://github.com/pacmanninja998/Taxes/tree/main/dist "Download")
## Core Features

### Track Documents by Tax Year
- Organize documents by tax year
- Easily navigate between different tax years
- System automatically detects current tax year based on date

### Document Management
- Add new tax documents with name, website link, and expected date
- Mark documents as complete/incomplete with a checkbox
- Edit existing document details
- Delete documents you no longer need to track

### Flexible Views
- Filter to see all documents, only needed documents, or only completed documents
- Documents are automatically organized into sections (Needed/Completed)

### Smart Date Handling
- Visual indicator when expected dates have passed
- Automatic recording of completion dates
- Shows last year's document dates for comparison

### Data Continuity
- Import documents from previous tax years
- Preserves your document history across multiple years
- Automatically links documents across years

### User Experience
- Clean, simple interface
- Status notifications for actions
- Clickable website links to access document sources
- Confirmation prompts for destructive actions

### Local Storage
- All data stored locally in a JSON file
- No internet connection required after initial setup
- Private and secure - your data stays on your computer

### Easy Deployment
- Runs as a standalone application
- Built-in server shutdown option
- Automatically opens in your default web browser

## Technical Details

- Built with Python and Flask
- Uses a JSON file for persistent storage
- Packaged as a standalone executable with PyInstaller
- Requires no installation or external dependencies

## Getting Started

1. Download the Tax Document Tracker executable
2. Run the application - it will automatically open in your web browser
3. Begin adding your tax documents for the current tax year
4. Use the "Import Last Year's Documents" button to bring in previous records
5. Closing the program, just close the broswer and the command window
