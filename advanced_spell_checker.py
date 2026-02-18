import cv2
import pytesseract
from PIL import Image
import numpy as np
import re
import requests
import json

class AdvancedSpellChecker:
    def __init__(self):
        # Load comprehensive English word list
        self.load_word_list()
    
    def load_word_list(self):
        # Try to load from online source, fallback to basic set
        try:
            # Download word list from online source
            url = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                self.dictionary = set(response.text.strip().split('\n'))
                print(f"Loaded {len(self.dictionary)} words from online dictionary")
            else:
                self.use_fallback_dictionary()
        except:
            self.use_fallback_dictionary()
    
    def use_fallback_dictionary(self):
        # Fallback to basic word set
        self.dictionary = {
            'hello', 'world', 'the', 'and', 'is', 'are', 'was', 'were', 'have', 'has', 'had',
            'this', 'that', 'these', 'those', 'with', 'from', 'they', 'them', 'their',
            'there', 'where', 'when', 'what', 'who', 'how', 'why', 'can', 'could', 'would',
            'should', 'will', 'shall', 'may', 'might', 'must', 'do', 'does', 'did', 'done',
            'make', 'made', 'take', 'took', 'taken', 'get', 'got', 'give', 'gave', 'given',
            'go', 'went', 'gone', 'come', 'came', 'see', 'saw', 'seen', 'know', 'knew', 'known',
            'think', 'thought', 'say', 'said', 'tell', 'told', 'ask', 'asked', 'work', 'worked',
            'play', 'played', 'run', 'ran', 'walk', 'walked', 'look', 'looked', 'find', 'found',
            'use', 'used', 'want', 'wanted', 'need', 'needed', 'like', 'liked', 'love', 'loved',
            'help', 'helped', 'try', 'tried', 'keep', 'kept', 'let', 'put', 'end', 'turn',
            'start', 'stop', 'move', 'show', 'follow', 'live', 'believe', 'hold', 'bring',
            'happen', 'write', 'provide', 'sit', 'stand', 'lose', 'add', 'hear', 'read',
            'include', 'continue', 'set', 'learn', 'change', 'lead', 'understand', 'watch',
            'back', 'list', 'feel', 'fact', 'hand', 'high', 'eye', 'week', 'point', 'group',
            'problem', 'complete', 'room', 'money', 'story', 'lot', 'study', 'book', 'word',
            'business', 'issue', 'side', 'kind', 'head', 'house', 'service', 'friend', 'father',
            'power', 'hour', 'game', 'line', 'member', 'law', 'car', 'city', 'community',
            'name', 'president', 'team', 'minute', 'idea', 'kid', 'body', 'information', 'nothing',
            'ago', 'right', 'social', 'whether', 'together', 'around', 'parent', 'only',
            'face', 'anything', 'create', 'public', 'already', 'speak', 'others', 'level',
            'allow', 'office', 'spend', 'door', 'health', 'person', 'art', 'sure', 'such',
            'war', 'history', 'party', 'within', 'grow', 'result', 'open', 'morning',
            'reason', 'low', 'win', 'research', 'girl', 'guy', 'early', 'food', 'before',
            'moment', 'himself', 'air', 'teacher', 'force', 'offer', 'enough', 'both',
            'education', 'across', 'although', 'remember', 'foot', 'second', 'boy', 'maybe',
            'toward', 'able', 'age', 'policy', 'everything', 'process', 'music', 'including',
            'consider', 'appear', 'actually', 'buy', 'probably', 'human', 'wait', 'serve',
            'market', 'die', 'send', 'expect', 'home', 'sense', 'build', 'stay', 'fall',
            'nation', 'plan', 'cut', 'college', 'interest', 'death', 'course', 'someone',
            'experience', 'behind', 'reach', 'local', 'kill', 'six', 'remain', 'effect',
            nm,.
            'yeah', 'suggest', 'class', 'control', 'raise', 'care', 'perhaps', 'little',
            'late', 'hard', 'field', 'else', 'pass', 'former', 'sell', 'major', 'sometimes',
            'require', 'along', 'development', 'themselves', 'report', 'role', 'better',
            'economic', 'effort', 'up', 'decide', 'rate', 'strong', 'possible', 'heart',
            'drug', 'leader', 'light', 'voice', 'wife', 'whole', 'police', 'mind', 'finally',
            'pull', 'return', 'free', 'military', 'price', 'less', 'according', 'decision',
            'explain', 'son', 'hope', 'even', 'develop', 'view', 'relationship', 'carry',
            'town', 'road', 'drive', 'arm', 'true', 'federal', 'break', 'difference', 'thank',
            'receive', 'value', 'international', 'building', 'action', 'full', 'model', 'join',
            'season', 'society', 'because', 'tax', 'director', 'position', 'player', 'agree',
            'especially', 'record', 'pick', 'wear', 'paper', 'special', 'space', 'ground',
            'form', 'support', 'event', 'official', 'whose', 'matter', 'everyone', 'center',
            'couple', 'site', 'project', 'hit', 'base', 'activity', 'star', 'table',
            'court', 'produce', 'eat', 'american', 'teach', 'oil', 'half', 'situation',
            'easy', 'cost', 'industry', 'figure', 'street', 'image', 'itself', 'phone',
            'either', 'data', 'cover', 'quite', 'picture', 'clear', 'practice', 'piece',
            'land', 'recent', 'describe', 'product', 'doctor', 'wall', 'patient', 'worker',
            'news', 'test', 'movie', 'certain', 'north', 'personal', 'simply', 'third',
            'technology', 'catch', 'step', 'baby', 'computer', 'type', 'attention', 'draw',
            'film', 'republican', 'tree', 'source', 'red', 'nearly', 'organization', 'choose',
            'cause', 'hair', 'century', 'evidence', 'window', 'difficult', 'listen', 'soon',
            'culture', 'billion', 'chance', 'brother', 'energy', 'period', 'summer',
            'realize', 'hundred', 'available', 'plant', 'likely', 'opportunity', 'term',
            'short', 'letter', 'condition', 'choice', 'place', 'single', 'rule', 'daughter',
            'administration', 'south', 'husband', 'congress', 'floor', 'campaign', 'material',
            'population', 'well', 'call', 'economy', 'medical', 'hospital', 'church', 'close',
            'thousand', 'risk', 'current', 'fire', 'future', 'wrong', 'involve', 'defense',
            'anyone', 'increase', 'security', 'bank', 'myself', 'certainly', 'west', 'sport',
            'board', 'seek', 'per', 'subject', 'officer', 'private', 'rest', 'behavior',
            'deal', 'performance', 'fight', 'throw', 'top', 'quickly', 'past', 'goal',
            'bed', 'order', 'author', 'fill', 'represent', 'focus', 'foreign', 'drop',
            'blood', 'upon', 'agency', 'push', 'nature', 'color', 'recently', 'store',
            'reduce', 'sound', 'note', 'fine', 'near', 'movement', 'page', 'enter', 'share',
            'than', 'common', 'poor', 'other', 'natural', 'race', 'concern', 'series',
            'significant', 'similar', 'hot', 'language', 'each', 'usually', 'response',
            'dead', 'rise', 'animal', 'factor', 'decade', 'article', 'shoot', 'east',
            'save', 'seven', 'artist', 'away', 'scene', 'stock', 'career', 'despite',
            'central', 'eight', 'thus', 'treatment', 'beyond', 'happy', 'exactly', 'protect',
            'approach', 'lie', 'size', 'dog', 'fund', 'serious', 'occur', 'media', 'ready',
            'sign', 'individual', 'simple', 'quality', 'pressure', 'accept', 'answer',
            'resource', 'identify', 'left', 'meeting', 'determine', 'prepare', 'disease',
            'whatever', 'success', 'argue', 'cup', 'particularly', 'amount', 'ability',
            'staff', 'recognize', 'indicate', 'character', 'growth', 'loss', 'degree',
            'wonder', 'attack', 'herself', 'region', 'television', 'box', 'tv', 'training',
            'pretty', 'trade', 'election', 'everybody', 'physical', 'lay', 'general',
            'feeling', 'standard', 'bill', 'message', 'fail', 'outside', 'arrive', 'analysis',
            'benefit', 'sex', 'forward', 'lawyer', 'present', 'section', 'environmental',
            'glass', 'skill', 'sister', 'professor', 'operation', 'financial', 'crime',
            'stage', 'ok', 'compare', 'authority', 'miss', 'design', 'sort', 'one', 'act',
            'ten', 'knowledge', 'gun', 'station', 'blue', 'state', 'strategy', 'clearly',
            'discuss', 'indeed', 'truth', 'song', 'example', 'democratic', 'check',
            'environment', 'leg', 'dark', 'various', 'rather', 'laugh', 'guess', 'executive',
            'prove', 'hang', 'entire', 'rock', 'forget', 'claim', 'remove', 'manager',
            'enjoy', 'network', 'legal', 'religious', 'cold', 'final', 'main', 'science',
            'green', 'memory', 'card', 'above', 'seat', 'cell', 'establish', 'nice', 'trial',
            'expert', 'spring', 'firm', 'radio', 'visit', 'management', 'avoid', 'imagine',
            'tonight', 'huge', 'ball', 'finish', 'yourself', 'talk', 'theory', 'impact',
            'respond', 'statement', 'maintain', 'charge', 'popular', 'traditional', 'onto',
            'reveal', 'direction', 'weapon', 'employee', 'cultural', 'contain', 'peace',
            'pain', 'apply', 'measure', 'wide', 'shake', 'fly', 'interview', 'manage',
            'chair', 'fish', 'particular', 'camera', 'structure', 'politics', 'perform',
            'bit', 'weight', 'suddenly', 'discover', 'candidate', 'production', 'treat',
            'trip', 'evening', 'affect', 'inside', 'conference', 'unit', 'best', 'style',
            'adult', 'worry', 'range', 'mention', 'far', 'deep', 'front', 'edge', 'specific',
            'writer', 'trouble', 'necessary', 'throughout', 'challenge', 'fear', 'shoulder',
            'institution', 'middle', 'sea', 'dream', 'bar', 'beautiful', 'property', 'instead',
            'improve', 'stuff'
        }
        print(f"Using fallback dictionary with {len(self.dictionary)} words")
    
    def edit_distance(self, s1, s2):
        """Calculate edit distance between two strings"""
        if len(s1) < len(s2):
            return self.edit_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def get_suggestions(self, word, max_suggestions=3):
        """Get spelling suggestions for a word"""
        word = word.lower()
        suggestions = []
        
        # Find words with minimum edit distance
        for dict_word in self.dictionary:
            distance = self.edit_distance(word, dict_word)
            if distance <= 2:  # Allow up to 2 character differences
                suggestions.append((dict_word, distance))
        
        # Sort by edit distance and return top suggestions
        suggestions.sort(key=lambda x: x[1])
        return [word for word, _ in suggestions[:max_suggestions]]
    
    def check_text(self, text):
        """Check text for spelling mistakes"""
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        mistakes = []
        
        for word in words:
            word_lower = word.lower()
            if word_lower not in self.dictionary:
                suggestions = self.get_suggestions(word_lower)
                if suggestions:
                    best_suggestion = suggestions[0]
                    mistakes.append(f"'{word}' -> '{best_suggestion}'")
                else:
                    mistakes.append(f"'{word}' -> No suggestions found")
        
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
            cv2.imshow('Advanced Spell Checker Camera', frame)
            
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
    print("Loading Advanced Spell Checker...")
    checker = AdvancedSpellChecker()
    
    while True:
        print("\n1. Check text spelling")
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