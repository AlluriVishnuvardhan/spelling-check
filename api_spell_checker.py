import cv2
import pytesseract
from PIL import Image
import numpy as np
import re
import requests
import json

class APISpellChecker:
    def __init__(self):
        print("API Spell Checker initialized - can handle ANY word!")
    
    def check_with_api(self, word):
        """Check spelling using online API"""
        try:
            # Using LanguageTool API for spell checking
            url = "https://api.languagetool.org/v2/check"
            data = {
                'text': word,
                'language': 'en-US'
            }
            
            response = requests.post(url, data=data, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result['matches']:
                    # Get the first suggestion
                    suggestions = result['matches'][0].get('replacements', [])
                    if suggestions:
                        return suggestions[0]['value']
            
            # Fallback to another API if first fails
            return self.check_with_textgears(word)
            
        except Exception as e:
            print(f"API error: {e}")
            return self.offline_suggestion(word)
    
    def check_with_textgears(self, word):
        """Fallback API using TextGears"""
        try:
            url = "https://api.textgears.com/spelling"
            params = {
                'text': word,
                'language': 'en-US',
                'key': 'free'  # Free tier
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                result = response.json()
                if result.get('response') and result['response'].get('errors'):
                    errors = result['response']['errors']
                    if errors and errors[0].get('better'):
                        return errors[0]['better'][0]
            
            return self.offline_suggestion(word)
            
        except Exception as e:
            return self.offline_suggestion(word)
    
    def offline_suggestion(self, word):
        """Offline fallback with common corrections"""
        corrections = {
            'laptp': 'laptop', 'compter': 'computer', 'mobil': 'mobile',
            'hellow': 'hello', 'wrold': 'world', 'teh': 'the', 'adn': 'and',
            'recieve': 'receive', 'seperate': 'separate', 'definately': 'definitely',
            'occured': 'occurred', 'begining': 'beginning', 'untill': 'until',
            'wich': 'which', 'thier': 'their', 'freind': 'friend', 'beleive': 'believe',
            'achive': 'achieve', 'wierd': 'weird', 'neccessary': 'necessary',
            'embarass': 'embarrass', 'accomodate': 'accommodate', 'existance': 'existence',
            'maintainance': 'maintenance', 'occassion': 'occasion', 'priviledge': 'privilege',
            'recomend': 'recommend', 'succesful': 'successful', 'tommorrow': 'tomorrow',
            'truely': 'truly', 'usefull': 'useful', 'wether': 'whether',
            'programing': 'programming', 'sofware': 'software', 'hardwar': 'hardware',
            'keyborad': 'keyboard', 'mous': 'mouse', 'scren': 'screen', 'moniter': 'monitor',
            'camra': 'camera', 'phon': 'phone', 'tabl': 'table', 'char': 'chair',
            'buk': 'book', 'pen': 'pen', 'papr': 'paper', 'wat': 'water',
            'fd': 'food', 'hous': 'house', 'car': 'car', 'tre': 'tree',
            'flwr': 'flower', 'bir': 'bird', 'ca': 'cat', 'do': 'dog'
        }
        
        return corrections.get(word.lower(), f"No suggestion for '{word}'")
    
    def is_word_correct(self, word):
        """Check if word is spelled correctly using API"""
        try:
            url = "https://api.languagetool.org/v2/check"
            data = {
                'text': word,
                'language': 'en-US'
            }
            
            response = requests.post(url, data=data, timeout=3)
            if response.status_code == 200:
                result = response.json()
                return len(result['matches']) == 0  # No matches means correct spelling
            
            return True  # Assume correct if API fails
            
        except:
            return True  # Assume correct if API fails
    
    def check_text(self, text):
        """Check entire text for spelling mistakes"""
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        mistakes = []
        
        print("Checking spelling using online APIs...")
        
        for word in words:
            if not self.is_word_correct(word):
                suggestion = self.check_with_api(word)
                if suggestion and suggestion != word.lower():
                    mistakes.append(f"'{word}' -> '{suggestion}'")
        
        if not mistakes:
            return "No spelling mistakes found!"
        
        return f"Spelling mistakes: {', '.join(mistakes)}"
    
    def check_from_camera(self):
        """Check spelling from camera input"""
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            cv2.putText(frame, "Press 's' to scan text, 'q' to quit", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('API Spell Checker Camera', frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('s'):
                text = pytesseract.image_to_string(frame)
                if text.strip():
                    result = self.check_text(text.strip())
                    print(f"Detected text: {text.strip()}")
                    print(result)
                else:
                    print("No text detected")
            
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

def main():
    print("Starting API-based Spell Checker...")
    checker = APISpellChecker()
    
    while True:
        print("\n1. Check text spelling (API-powered)")
        print("2. Use camera to detect and check spelling")
        print("3. Exit")
        
        choice = input("Choose option: ")
        
        if choice == '1':
            text = input("Enter text to check: ")
            result = checker.check_text(text)
            print(result)
        
        elif choice == '2':
            print("Camera mode - Press 's' to scan, 'q' to quit")
            checker.check_from_camera()
        
        elif choice == '3':
            break

if __name__ == "__main__":
    main()