from flask import Flask, render_template, request
import docx
from PyPDF2 import PdfReader

app = Flask(__name__)

# Keywords
job_keywords = {
    "data scientist": ["python", "machine learning", "data"],
    "web developer": ["html", "css", "javascript"],
    "java developer": ["java", "oop"]
}

# Read DOCX
def read_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text
    return text

# Read PDF
def read_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

# Analyze
def analyze_resume(role, text):
    role = role.lower()

    if role not in job_keywords:
        return "Rejected ❌", ["Invalid role"], ["Enter valid role"]

    keywords = job_keywords[role]
    missing = []

    for word in keywords:
        if word not in text.lower():
            missing.append(word)

    if len(missing) == 0:
        return "Selected ✅", [], []
    else:
        return "Rejected ❌", [f"Missing: {', '.join(missing)}"], [f"Add {w}" for w in missing]

# ROUTES

@app.route('/')
def home():
    return render_template('role.html')

@app.route('/upload', methods=['POST'])
def upload():
    role = request.form['role']
    return render_template('upload.html', role=role)

@app.route('/result', methods=['POST'])
def result():
    role = request.form['role']

    file = request.files.get('resume')

    if not file or file.filename == "":
        return "No file selected"

    # File reading
    if file.filename.endswith('.docx'):
        text = read_docx(file)
    elif file.filename.endswith('.pdf'):
        text = read_pdf(file)
    else:
        return "Only PDF or DOCX allowed"

    if text.strip() == "":
        return "File is empty or unreadable"

    result, reasons, suggestions = analyze_resume(role, text)

    return render_template('result.html',
                           result=result,
                           reasons=reasons,
                           suggestions=suggestions,
                           role=role)

if __name__ == '__main__':
    app.run(debug=True)
