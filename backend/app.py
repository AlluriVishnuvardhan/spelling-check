from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import re
import io
import PyPDF2
import zipfile
from bs4 import BeautifulSoup

app = Flask(__name__, 
            template_folder='../frontend/templates', 
            static_folder='../frontend/static')
CORS(app)


class SpellCheckerAPI:
    def __init__(self):
        self.corrections = {
            'laptp': 'laptop',
            'compter': 'computer',
            'mobil': 'mobile',
            'hellow': 'hello',
            'wrold': 'world',
            'teh': 'the',
            'adn': 'and',
            'recieve': 'receive',
            'seperate': 'separate',
            'definately': 'definitely',
            'occured': 'occurred',
            'begining': 'beginning',
            'untill': 'until',
            'wich': 'which',
            'thier': 'their',
            'freind': 'friend',
            'beleive': 'believe',
            'programing': 'programming',
            'sofware': 'software'
        }

    def check_with_api(self, text):
        try:
            url = "https://api.languagetool.org/v2/check"
            data = {
                'text': text,
                'language': 'en-US'
            }

            response = requests.post(url, data=data, timeout=10)

            if response.status_code == 200:
                result = response.json()
                mistakes = []

                for match in result['matches']:
                    word = text[match['offset']:match['offset'] + match['length']]
                    suggestions = match.get('replacements', [])

                    if suggestions:
                        mistakes.append({
                            'word': word,
                            'suggestion': suggestions[0]['value'],
                            'context': match.get('message', 'Spelling error')
                        })

                return mistakes

        except Exception:
            return self.offline_check(text)

    def offline_check(self, text):
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        mistakes = []

        for word in words:
            if word.lower() in self.corrections:
                mistakes.append({
                    'word': word,
                    'suggestion': self.corrections[word.lower()],
                    'context': 'Offline spelling correction'
                })

        return mistakes


spell_checker = SpellCheckerAPI()


# ======================
# PAGES
# ======================

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/results')
def results():
    return render_template('results.html')


# ======================
# TEXT CHECK (FORM)
# ======================

@app.route('/check-text', methods=['POST'])
def check_text_form():
    text = request.form.get('text', '')

    if not text:
        return render_template('index.html', error='Please enter some text')

    mistakes = spell_checker.check_with_api(text)

    return render_template(
        'results.html',
        original_text=text,
        mistakes=mistakes
    )


# ======================
# TEXT CHECK (API)
# ======================

@app.route('/api/check-text', methods=['POST'])
def check_text():
    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    mistakes = spell_checker.check_with_api(text)

    return jsonify({
        'original_text': text,
        'mistakes': mistakes
    })


# ======================
# PDF EXTRACTION
# ======================

@app.route('/api/extract-pdf', methods=['POST'])
def extract_pdf():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No PDF file provided'}), 400

    pdf_file = request.files['pdf']
    pdf_bytes = pdf_file.read()
    text = ''

    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + ' '

        text = ' '.join(text.split())

        if not text:
            return jsonify({'error': 'No extractable text found in PDF'}), 400

        return jsonify({'text': text})

    except Exception:
        return jsonify({'error': 'Cannot read PDF file'}), 400


# ======================
# WEBSITE ZIP CHECK
# ======================

@app.route('/api/check-website-zip', methods=['POST'])
def check_website_zip():
    if 'zip' not in request.files:
        return jsonify({'error': 'No ZIP file provided'}), 400

    zip_file = request.files['zip']
    zip_bytes = zip_file.read()
    all_text = ''

    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            for file_name in zf.namelist():
                if file_name.endswith(('.html', '.htm', '.txt')):
                    file_content = zf.read(file_name).decode('utf-8', errors='ignore')

                    if file_name.endswith(('.html', '.htm')):
                        soup = BeautifulSoup(file_content, 'html.parser')
                        for script in soup(["script", "style"]):
                            script.decompose()
                        text = soup.get_text(separator=' ', strip=True)
                    else:
                        text = file_content

                    all_text += text + ' '

        all_text = ' '.join(all_text.split())

        if not all_text:
            return jsonify({'error': 'No text found in ZIP'}), 400

        mistakes = spell_checker.check_with_api(all_text)

        return jsonify({
            'text': all_text[:5000],
            'mistakes': mistakes
        })

    except Exception:
        return jsonify({'error': 'Error processing ZIP file'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
