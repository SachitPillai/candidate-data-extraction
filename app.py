from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pytesseract
from pdf2image import convert_from_path
import sqlite3
import cv2
import re

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure uploads folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DB_NAME = "extracted_data.db"

# Initialize database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            dob TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            training TEXT,
            certifications TEXT,
            family TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Preprocess image for better OCR
def preprocess_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    img = cv2.medianBlur(img, 3)
    return img

# Extract field based on pattern
def parse_field(text, field_name):
    pattern = rf"{field_name}[:\-]?\s*([^\n]+)"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else "Not Found"

# Extract table section cleanly
def extract_section(text, start_marker, end_marker):
    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker, start_idx)
    if start_idx != -1 and end_idx != -1:
        return text[start_idx + len(start_marker):end_idx].strip()
    elif start_idx != -1:
        return text[start_idx + len(start_marker):].strip()
    return ""

# Extract data from file
def extract_data(file_path):
    text = ""
    extracted_data = {}

    # Convert PDF to images or process image file
    if file_path.endswith(".pdf"):
        images = convert_from_path(file_path)
        for image in images:
            img_path = "temp.png"
            image.save(img_path, "PNG")
            img = preprocess_image(img_path)
            text += pytesseract.image_to_string(img, config="--oem 3 --psm 6")
    else:
        img = preprocess_image(file_path)
        text = pytesseract.image_to_string(img, config="--oem 3 --psm 6")

    # Extract fields
    extracted_data['name'] = parse_field(text, "Name")
    extracted_data['dob'] = parse_field(text, "Date of Birth")
    extracted_data['email'] = parse_field(text, "Email")
    extracted_data['phone'] = parse_field(text, "Phone|Mobile")
    extracted_data['address'] = parse_field(text, "Address")

    # Extract specific table data
    extracted_data['training'] = extract_section(text, "15. Details of any important training undergone:", "16.")
    extracted_data['certifications'] = extract_section(text, "16. Please list the technical or professional certification you completed", "17.")
    extracted_data['family'] = extract_section(text, "17. Details of Family Members:", "18.")

    return extracted_data

# Save data to database
def save_to_db(data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO candidates (name, dob, email, phone, address, training, certifications, family)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (data['name'], data['dob'], data['email'], data['phone'], data['address'], data['training'], data['certifications'], data['family']))
    conn.commit()
    conn.close()

@app.route('/')
def upload_page():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No file selected", 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Extract and save data
    extracted_data = extract_data(file_path)
    save_to_db(extracted_data)

    return redirect(url_for('view_records'))

@app.route('/records')
def view_records():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates")
    records = cursor.fetchall()
    conn.close()
    return render_template('view.html', records=records)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5432)
