from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import re
import base64
import cv2
import numpy as np
from PIL import Image
import pytesseract
import io
import PyPDF2
import os

# Try to set tesseract path
tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Tesseract-OCR\tesseract.exe'
]
for path in tesseract_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        print(f"Tesseract found at: {path}")
        break

app = Flask(__name__, template_folder='../frontend/templates', static_folder='../frontend/static')
CORS(app)

class SpellCheckerAPI:
    def __init__(self):
        self.corrections = {
            'laptp': 'laptop', 'compter': 'computer', 'mobil': 'mobile',
            'hellow': 'hello', 'wrold': 'world', 'teh': 'the', 'adn': 'and',
            'recieve': 'receive', 'seperate': 'separate', 'definately': 'definitely',
            'occured': 'occurred', 'begining': 'beginning', 'untill': 'until',
            'wich': 'which', 'thier': 'their', 'freind': 'friend', 'beleive': 'believe',
            'achive': 'achieve', 'wierd': 'weird', 'neccessary': 'necessary',
            'programing': 'programming', 'sofware': 'software', 'hardwar': 'hardware',
            'keyborad': 'keyboard', 'mous': 'mouse', 'scren': 'screen', 'moniter': 'monitor',
            'telanagana': 'telangana', 'telagana': 'telangana', 'telengana': 'telangana'
        }
        
        # Common names that shouldn't be corrected
        self.names = {
            'vishnu', 'vishu', 'ram', 'krishna', 'shiva', 'lakshmi', 'saraswati',
            'arjun', 'bharat', 'india', 'telangana', 'hyderabad', 'bangalore',
            'mumbai', 'delhi', 'chennai', 'kolkata', 'pune', 'ahmedabad',
            'john', 'mary', 'david', 'sarah', 'michael', 'jennifer', 'robert',
            'lisa', 'william', 'karen', 'james', 'susan', 'christopher', 'jessica',
            'agneyra'
        }
        
        # Known correct spellings (proper nouns) that should never be changed
        self.known_correct = {
            'telangana', 'maharashtra', 'karnataka', 'tamilnadu', 'kerala', 'gujarat',
            'rajasthan', 'punjab', 'haryana', 'uttarpradesh', 'madhyapradesh',
            'andhrapradesh', 'westbengal', 'bihar', 'odisha', 'assam', 'jharkhand',
            'india', 'america', 'england', 'australia', 'canada', 'germany', 'france',
            'china', 'japan', 'russia', 'brazil', 'mexico', 'italy', 'spain'
        }
    
    def check_with_api(self, text):
        try:
            # First, find most common spelling variants
            word_frequencies = self.find_spelling_variants(text)
            
            url = "https://api.languagetool.org/v2/check"
            data = {
                'text': text, 
                'language': 'en-US',
                'enabledRules': 'MORFOLOGIK_RULE_EN_US,HUNSPELL_RULE,TYPOS,WORD_REPEAT_RULE',
                'disabledRules': 'WHITESPACE_RULE,EN_QUOTES'
            }
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                mistakes = []
                
                for match in result['matches']:
                    # Skip capitalization, punctuation, and typography errors
                    rule_category = match['rule']['category']['id']
                    if rule_category in ['CASING', 'PUNCTUATION', 'TYPOGRAPHY', 'WHITESPACE']:
                        continue
                    
                    # Skip uppercase/lowercase suggestions
                    word = text[match['offset']:match['offset'] + match['length']]
                    suggestions = match.get('replacements', [])
                    
                    if suggestions:
                        suggestion = suggestions[0]['value']
                        
                        # Skip if only difference is capitalization
                        if word.lower() == suggestion.lower():
                            continue
                        
                        # Check if it's a name before correcting
                        if self.is_likely_name(word, text):
                            continue
                        
                        # Check if there's a more common variant in the document
                        word_lower = word.lower()
                        if word_lower in word_frequencies:
                            most_common = word_frequencies[word_lower]
                            if most_common != word:
                                suggestion = most_common
                        
                        # Focus on spelling and word choice errors only
                        if rule_category in ['TYPOS', 'CONFUSED_WORDS', 'GRAMMAR']:
                            # Get the best suggestion based on context
                            best_suggestion = self.get_best_suggestion(word, suggestions, text, match)
                            
                            # Add context-aware description
                            description = match.get('message', 'Spelling error')
                            
                            mistakes.append({
                                'word': word,
                                'suggestion': best_suggestion,
                                'context': description,
                                'rule_type': rule_category
                            })
                
                # Check for frequency-based noun variants (even if not flagged by API)
                word_lower = word.lower()
                if word_lower in word_frequencies:
                    most_common = word_frequencies[word_lower]
                    if most_common != word and word_lower not in self.known_correct:
                        # This variant appears less frequently than another spelling
                        mistakes.append({
                            'word': word,
                            'suggestion': most_common,
                            'context': f'Use consistent spelling: "{most_common}" appears more frequently',
                            'rule_type': 'TYPOS'
                        })
                
                return mistakes
        except Exception as e:
            print(f"API Error: {e}")
            return self.contextual_offline_check(text)
    
    def find_spelling_variants(self, text):
        """Find most common spelling for similar words (nouns with same meaning)"""
        from collections import Counter
        from difflib import SequenceMatcher
        
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        word_groups = {}
        
        # Group similar words (nouns with different spellings but same meaning)
        for word in words:
            word_lower = word.lower()
            
            # Skip if it's a known correct spelling
            if word_lower in self.known_correct:
                continue
            
            found_group = False
            
            for key in list(word_groups.keys()):
                # Check similarity (80% match for same noun with different spelling)
                similarity = SequenceMatcher(None, word_lower, key).ratio()
                if similarity > 0.8:
                    word_groups[key].append(word)
                    found_group = True
                    break
            
            if not found_group:
                word_groups[word_lower] = [word]
        
        # Find most common variant in each group and map ALL variants to it
        variant_map = {}
        for key, variants in word_groups.items():
            if len(variants) > 1:
                counter = Counter(variants)
                # Get the variant that appears most frequently
                most_common_word, most_common_count = counter.most_common(1)[0]
                
                # Check if any variant is a known correct spelling
                known_variant = None
                for variant in set(variants):
                    if variant.lower() in self.known_correct:
                        known_variant = variant
                        break
                
                # Use known correct spelling if exists, otherwise use most frequent
                correct_spelling = known_variant if known_variant else most_common_word
                
                # Map ALL less frequent variants to the correct spelling
                for variant in set(variants):
                    if variant != correct_spelling:
                        variant_map[variant.lower()] = correct_spelling
        
        return variant_map
    
    def get_best_suggestion(self, word, suggestions, full_text, match):
        """Select the best suggestion based on sentence context"""
        
        # Check if it's likely a name (after "my name is", "I am", etc.)
        if self.is_likely_name(word, full_text):
            return word  # Don't correct names
        
        if len(suggestions) == 1:
            return suggestions[0]['value']
        
        # Context-aware selection for common words
        word_lower = word.lower()
        
        # Smart corrections based on context
        if word_lower == 'hellow':
            return 'hello'  # Always correct to hello, not held
        
        # Get surrounding words for context
        words = full_text.split()
        word_index = -1
        
        for i, w in enumerate(words):
            if word.lower() in w.lower():
                word_index = i
                break
        
        # Context-based selection
        context_before = words[max(0, word_index-2):word_index] if word_index > 0 else []
        context_after = words[word_index+1:min(len(words), word_index+3)] if word_index < len(words)-1 else []
        
        # Greeting context
        if context_before and any(greeting in ' '.join(context_before).lower() for greeting in ['hi', 'hey', 'good']):
            if word_lower in ['hellow', 'helo', 'hllo']:
                return 'hello'
        
        # Name context
        if context_before and any(name_word in ' '.join(context_before).lower() for name_word in ['name', 'am', 'called']):
            # Don't correct if it's likely a name
            if word_lower in self.names:
                return word
        
        # Location context
        if context_before and any(loc_word in ' '.join(context_before).lower() for loc_word in ['from', 'in', 'at', 'live']):
            # Don't correct place names
            if word_lower in ['telangana', 'hyderabad', 'bangalore', 'mumbai', 'delhi']:
                return word
        
        # Return best contextual suggestion
        return suggestions[0]['value']
    
    def is_likely_name(self, word, full_text):
        """Check if word is likely a proper name based on context"""
        text_lower = full_text.lower()
        word_lower = word.lower()
        
        # Check if it's in our names database first
        if word_lower in self.names:
            return True
        
        # Name context patterns - more flexible matching
        name_indicators = [
            'my name is',
            'i am',
            'called',
            'name is',
            'hi i am',
            'hello i am',
            'this is'
        ]
        
        # Split text into words for better context checking
        words = text_lower.split()
        
        # Find the position of the current word
        word_position = -1
        for i, w in enumerate(words):
            if word_lower in w.lower():
                word_position = i
                break
        
        if word_position > 0:
            # Check the words before this word
            context_before = ' '.join(words[max(0, word_position-4):word_position])
            
            # Check if any name indicator appears before this word
            for indicator in name_indicators:
                if indicator in context_before:
                    return True
        
        # Check if word appears right after common name patterns
        for indicator in name_indicators:
            pattern = indicator + ' ' + word_lower
            if pattern in text_lower:
                return True
        
        return False
    
    def contextual_offline_check(self, text):
        """Enhanced offline checking with context awareness"""
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        mistakes = []
        
        # Enhanced corrections with context
        enhanced_corrections = {
            **self.corrections,
            # Context-aware corrections
            'there': {'their': 'possessive', 'they\'re': 'contraction'},
            'your': {'you\'re': 'contraction'},
            'its': {'it\'s': 'contraction'},
            'to': {'too': 'excessive', 'two': 'number'},
            'then': {'than': 'comparison'},
            'affect': {'effect': 'noun form'},
            'loose': {'lose': 'verb form'},
            'breath': {'breathe': 'verb form'},
            'advice': {'advise': 'verb form'}
        }
        
        for i, word in enumerate(words):
            word_lower = word.lower()
            
            # Skip if it's a name
            if self.is_likely_name(word, text):
                continue
            
            if word_lower in self.corrections:
                mistakes.append({
                    'word': word,
                    'suggestion': self.corrections[word_lower],
                    'context': 'Spelling correction',
                    'rule_type': 'TYPOS'
                })
            
            # Context-aware word choice corrections
            elif word_lower in enhanced_corrections and isinstance(enhanced_corrections[word_lower], dict):
                context_words = words[max(0, i-2):i] + words[i+1:min(len(words), i+3)]
                context_text = ' '.join(context_words).lower()
                
                # Simple context rules
                if word_lower == 'there':
                    if any(possessive in context_text for possessive in ['house', 'car', 'book', 'phone']):
                        mistakes.append({
                            'word': word,
                            'suggestion': 'their',
                            'context': 'Use "their" for possession',
                            'rule_type': 'CONFUSED_WORDS'
                        })
                elif word_lower == 'your' and ('are' in context_text or 'not' in context_text):
                    mistakes.append({
                        'word': word,
                        'suggestion': 'you\'re',
                        'context': 'Use "you\'re" for "you are"',
                        'rule_type': 'CONFUSED_WORDS'
                    })
        
        return mistakes
    
    def offline_check(self, text):
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        mistakes = []
        
        for word in words:
            if word.lower() in self.corrections:
                mistakes.append({
                    'word': word,
                    'suggestion': self.corrections[word.lower()]
                })
        
        return mistakes
    
    def process_image(self, image_data):
        try:
            print("Starting image processing...")
            
            # Check tesseract
            try:
                pytesseract.get_tesseract_version()
            except:
                return "TESSERACT_NOT_INSTALLED"
            
            # Decode image
            image_bytes = base64.b64decode(image_data.split(',')[1])
            image = Image.open(io.BytesIO(image_bytes))
            print(f"Image size: {image.size}")
            
            # Convert to grayscale
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # OCR
            text = pytesseract.image_to_string(gray).strip()
            print(f"OCR: '{text}' ({len(text)} chars)")
            
            return ' '.join(text.split()) if text else ""
            
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

spell_checker = SpellCheckerAPI()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/check-text', methods=['POST'])
def check_text_form():
    text = request.form.get('text', '')
    
    if not text:
        return render_template('index.html', error='Please enter some text')
    
    mistakes = spell_checker.check_with_api(text)
    
    return render_template('results.html', 
                         original_text=text, 
                         mistakes=mistakes)

@app.route('/api/check-text', methods=['POST'])
def check_text():
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    mistakes = spell_checker.check_with_api(text)
    
    return jsonify({
        'original_text': text,
        'mistakes': mistakes,
        'corrected_text': text if not mistakes else None
    })

@app.route('/api/check-image', methods=['POST'])
def check_image():
    try:
        data = request.json
        image_data = data.get('image', '')
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        print("\n=== Image OCR ===")
        extracted_text = spell_checker.process_image(image_data)
        
        if extracted_text == "TESSERACT_NOT_INSTALLED":
            return jsonify({'error': 'Tesseract OCR is not installed. Download from: https://github.com/UB-Mannheim/tesseract/wiki and add to PATH'}), 400
        
        if not extracted_text:
            return jsonify({'error': 'No text found in image'}), 400
        
        return jsonify({'extracted_text': extracted_text, 'mistakes': []})
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/extract-pdf', methods=['POST'])
def extract_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file provided'}), 400
        
        pdf_file = request.files['pdf']
        if pdf_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        pdf_bytes = pdf_file.read()
        text = ''
        
        print(f"\n=== PDF Extraction ===")
        print(f"File: {pdf_file.filename}, Size: {len(pdf_bytes)} bytes")
        
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            num_pages = len(pdf_reader.pages)
            print(f"Total pages: {num_pages}")
            
            for i, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        clean_text = page_text.strip()
                        if clean_text:
                            text += clean_text + ' '
                            print(f"Page {i+1}: Extracted {len(clean_text)} chars")
                        else:
                            print(f"Page {i+1}: Empty")
                    else:
                        print(f"Page {i+1}: No text")
                except Exception as page_err:
                    print(f"Page {i+1} error: {page_err}")
            
            text = ' '.join(text.split())
            print(f"\nFinal: {len(text)} chars")
            
            if text:
                print(f"Preview: {text[:200]}")
                return jsonify({'text': text})
            else:
                print("No text extracted - PDF may be scanned/image-based")
                return jsonify({'error': 'This PDF contains no extractable text. It may be a scanned document or image-based PDF. Please try typing the text manually or use the camera feature.'}), 400
            
        except Exception as pdf_err:
            print(f"PDF error: {pdf_err}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Cannot read PDF. File may be corrupted or password-protected.'}), 400
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to process PDF'}), 500

@app.route('/api/check-website-zip', methods=['POST'])
def check_website_zip():
    try:
        if 'zip' not in request.files:
            return jsonify({'error': 'No ZIP file provided'}), 400
        
        zip_file = request.files['zip']
        if zip_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        import zipfile
        from bs4 import BeautifulSoup
        
        print(f"\n=== Website ZIP Processing ===")
        
        zip_bytes = zip_file.read()
        all_text = ''
        files_processed = []
        
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
            for file_info in zf.namelist():
                if file_info.endswith(('.html', '.htm', '.txt', '.css', '.js')):
                    try:
                        file_content = zf.read(file_info).decode('utf-8', errors='ignore')
                        
                        if file_info.endswith(('.html', '.htm')):
                            soup = BeautifulSoup(file_content, 'html.parser')
                            # Remove script and style tags
                            for script in soup(["script", "style"]):
                                script.decompose()
                            text = soup.get_text(separator=' ', strip=True)
                        else:
                            text = file_content
                        
                        if text and len(text.strip()) > 10:
                            all_text += text + ' '
                            files_processed.append(file_info)
                            print(f"Processed: {file_info} ({len(text)} chars)")
                    except Exception as e:
                        print(f"Error processing {file_info}: {e}")
        
        all_text = ' '.join(all_text.split())
        print(f"\nTotal text extracted: {len(all_text)} chars from {len(files_processed)} files")
        
        if len(all_text.strip()) < 10:
            return jsonify({'error': 'No text found in ZIP file'}), 400
        
        # Check spelling
        mistakes = spell_checker.check_with_api(all_text)
        
        return jsonify({
            'text': all_text[:5000],  # Return first 5000 chars
            'mistakes': mistakes,
            'files_processed': files_processed,
            'total_files': len(files_processed)
        })
        
    except Exception as e:
        print(f"\n=== ZIP Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error processing ZIP: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)