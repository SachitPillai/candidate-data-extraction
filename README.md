# Candidate Data Extraction System

This project is a Flask-based web application that extracts and organizes candidate information from uploaded PDF or image files using Optical Character Recognition (OCR) and stores the results in a database.



---

## Features

- Upload PDF or image files containing candidate data.
- Extracts structured information:
  - Name
  - Date of Birth
  - Email
  - Phone
  - Address
  - Training Details
  - Certifications
  - Family Details
- Displays extracted data in a clean, user-friendly table.
- PDF Preview functionality on the upload page.
- Stores extracted data into a **SQLite database**.
- Supports viewing extracted records in the web interface.

---

## Technologies Used

- **Backend**: Flask (Python)
- **OCR**: Tesseract OCR
- **PDF Processing**: pdf2image
- **Database**: SQLite
- **Frontend**: HTML, CSS, Bootstrap 5
- **Dependencies**:
  - Flask
  - pytesseract
  - pdf2image
  - OpenCV
  - SQLite3

---

## Setup Instructions

Follow these steps to set up and run the project locally:

### 1. Prerequisites

- Python 3.8 or above
- Tesseract OCR (install via Brew or package manager):
  ```bash
  brew install tesseract
