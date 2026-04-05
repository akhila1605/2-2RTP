from flask import Flask, render_template, request
import PyPDF2
import docx
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

def extract_text(file):
    text = ""

    if file.filename.endswith('.pdf'):
        pdf = PyPDF2.PdfReader(file)
        for page in pdf.pages:
            text += page.extract_text()

    elif file.filename.endswith('.docx'):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text

    return text


def match_resume(job_desc, resume):
    cv = CountVectorizer()
    matrix = cv.fit_transform([job_desc, resume])
    similarity = cosine_similarity(matrix)[0][1]
    return round(similarity * 100, 2)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    job_role = request.form['job_role']
    file = request.files['resume']

    # File validation
    if not (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
        return "Upload only PDF or DOCX"

    resume_text = extract_text(file)
    score = match_resume(job_role, resume_text)

    result = "Selected" if score > 50 else "Not Selected"

    return render_template('result.html', score=score, result=result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
