import cv2
import pytesseract
from PIL import Image
import numpy as np
import re

class SpellCheckerApp:
    def __init__(self):
        # Common English words dictionary
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
            'power', 'hour', 'game', 'line', 'end', 'member', 'law', 'car', 'city', 'community',
            'name', 'president', 'team', 'minute', 'idea', 'kid', 'body', 'information', 'nothing',
            'ago', 'right', 'lead', 'social', 'understand', 'whether', 'back', 'watch', 'together',
            'follow', 'around', 'parent', 'only', 'stop', 'face', 'anything', 'create', 'public',
            'already', 'speak', 'others', 'read', 'level', 'allow', 'add', 'office', 'spend',
            'door', 'health', 'person', 'art', 'sure', 'such', 'war', 'history', 'party', 'within',
            'grow', 'result', 'open', 'morning', 'walk', 'reason', 'low', 'win', 'research',
            'girl', 'guy', 'early', 'food', 'before', 'moment', 'himself', 'air', 'teacher',
            'force', 'offer', 'enough', 'both', 'education', 'across', 'although', 'remember',
            'foot', 'second', 'boy', 'maybe', 'toward', 'able', 'age', 'policy', 'everything',
            'love', 'process', 'music', 'including', 'consider', 'appear', 'actually', 'buy',
            'probably', 'human', 'wait', 'serve', 'market', 'die', 'send', 'expect', 'home',
            'sense', 'build', 'stay', 'fall', 'oh', 'nation', 'plan', 'cut', 'college', 'interest',
            'death', 'course', 'someone', 'experience', 'behind', 'reach', 'local', 'kill',
            'six', 'remain', 'effect', 'use', 'yeah', 'suggest', 'class', 'control', 'raise',
            'care', 'perhaps', 'little', 'late', 'hard', 'field', 'else', 'pass', 'former',
            'sell', 'major', 'sometimes', 'require', 'along', 'development', 'themselves',
            'report', 'role', 'better', 'economic', 'effort', 'up', 'decide', 'rate', 'strong',
            'possible', 'heart', 'drug', 'show', 'leader', 'light', 'voice', 'wife', 'whole',
            'police', 'mind', 'finally', 'pull', 'return', 'free', 'military', 'price', 'report',
            'less', 'according', 'decision', 'explain', 'son', 'hope', 'even', 'develop',
            'view', 'relationship', 'carry', 'town', 'road', 'drive', 'arm', 'true', 'federal',
            'break', 'better', 'difference', 'thank', 'receive', 'value', 'international',
            'building', 'action', 'full', 'model', 'join', 'season', 'society', 'because',
            'tax', 'director', 'early', 'position', 'player', 'agree', 'especially', 'record',
            'pick', 'wear', 'paper', 'special', 'space', 'ground', 'form', 'support', 'event',
            'official', 'whose', 'matter', 'everyone', 'center', 'couple', 'site', 'project',
            'hit', 'base', 'activity', 'star', 'table', 'need', 'court', 'produce', 'eat',
            'american', 'teach', 'oil', 'half', 'situation', 'easy', 'cost', 'industry',
            'figure', 'street', 'image', 'itself', 'phone', 'either', 'data', 'cover',
            'quite', 'picture', 'clear', 'practice', 'piece', 'land', 'recent', 'describe',
            'product', 'doctor', 'wall', 'patient', 'worker', 'news', 'test', 'movie',
            'certain', 'north', 'personal', 'open', 'support', 'simply', 'third', 'technology',
            'catch', 'step', 'baby', 'computer', 'type', 'attention', 'draw', 'film', 'republican',
            'tree', 'source', 'red', 'nearly', 'organization', 'choose', 'cause', 'hair',
            'look', 'point', 'century', 'evidence', 'window', 'difficult', 'listen', 'soon',
            'culture', 'billion', 'chance', 'brother', 'energy', 'period', 'course', 'summer',
            'less', 'realize', 'hundred', 'available', 'plant', 'likely', 'opportunity',
            'term', 'short', 'letter', 'condition', 'choice', 'place', 'single', 'rule',
            'daughter', 'administration', 'south', 'husband', 'congress', 'floor', 'campaign',
            'material', 'population', 'well', 'call', 'economy', 'medical', 'hospital',
            'church', 'close', 'thousand', 'risk', 'current', 'fire', 'future', 'wrong',
            'involve', 'defense', 'anyone', 'increase', 'security', 'bank', 'myself',
            'certainly', 'west', 'sport', 'board', 'seek', 'per', 'subject', 'officer',
            'private', 'rest', 'behavior', 'deal', 'performance', 'fight', 'throw', 'top',
            'quickly', 'past', 'goal', 'second', 'bed', 'order', 'author', 'fill', 'represent',
            'focus', 'foreign', 'drop', 'plan', 'blood', 'upon', 'agency', 'push', 'nature',
            'color', 'no', 'recently', 'store', 'reduce', 'sound', 'note', 'fine', 'before',
            'near', 'movement', 'page', 'enter', 'share', 'than', 'common', 'poor', 'other',
            'natural', 'race', 'concern', 'series', 'significant', 'similar', 'hot', 'language',
            'each', 'usually', 'response', 'dead', 'rise', 'animal', 'factor', 'decade',
            'article', 'shoot', 'east', 'save', 'seven', 'artist', 'away', 'scene', 'stock',
            'career', 'despite', 'central', 'eight', 'thus', 'treatment', 'beyond', 'happy',
            'exactly', 'protect', 'approach', 'lie', 'size', 'dog', 'fund', 'serious', 'occur',
            'media', 'ready', 'sign', 'thought', 'list', 'individual', 'simple', 'quality',
            'pressure', 'accept', 'answer', 'resource', 'identify', 'left', 'meeting', 'determine',
            'prepare', 'disease', 'whatever', 'success', 'argue', 'cup', 'particularly',
            'amount', 'ability', 'staff', 'recognize', 'indicate', 'character', 'growth',
            'loss', 'degree', 'wonder', 'attack', 'herself', 'region', 'television', 'box',
            'tv', 'training', 'pretty', 'trade', 'deal', 'election', 'everybody', 'physical',
            'lay', 'general', 'feeling', 'standard', 'bill', 'message', 'fail', 'outside',
            'arrive', 'analysis', 'benefit', 'name', 'sex', 'forward', 'lawyer', 'present',
            'section', 'environmental', 'glass', 'answer', 'skill', 'sister', 'pm', 'professor',
            'operation', 'financial', 'crime', 'stage', 'ok', 'compare', 'authority', 'miss',
            'design', 'sort', 'one', 'act', 'ten', 'knowledge', 'gun', 'station', 'blue',
            'state', 'strategy', 'little', 'clearly', 'discuss', 'indeed', 'force', 'truth',
            'song', 'example', 'democratic', 'check', 'environment', 'leg', 'dark', 'public',
            'various', 'rather', 'laugh', 'guess', 'executive', 'set', 'study', 'prove',
            'hang', 'entire', 'rock', 'forget', 'claim', 'remove', 'manager', 'help',
            'close', 'sound', 'enjoy', 'network', 'legal', 'religious', 'cold', 'form',
            'final', 'main', 'science', 'green', 'memory', 'card', 'above', 'seat', 'cell',
            'establish', 'nice', 'trial', 'expert', 'that', 'spring', 'firm', 'democratic',
            'radio', 'visit', 'management', 'care', 'avoid', 'imagine', 'tonight', 'huge',
            'ball', 'no', 'close', 'finish', 'yourself', 'talk', 'theory', 'impact', 'respond',
            'statement', 'maintain', 'charge', 'popular', 'traditional', 'onto', 'reveal',
            'direction', 'weapon', 'employee', 'cultural', 'contain', 'peace', 'head',
            'control', 'base', 'pain', 'apply', 'play', 'measure', 'wide', 'shake', 'fly',
            'interview', 'manage', 'chair', 'fish', 'particular', 'camera', 'structure',
            'politics', 'perform', 'bit', 'weight', 'suddenly', 'discover', 'candidate',
            'top', 'production', 'treat', 'trip', 'evening', 'affect', 'inside', 'conference',
            'unit', 'best', 'style', 'adult', 'worry', 'range', 'mention', 'rather', 'far',
            'deep', 'front', 'edge', 'individual', 'specific', 'writer', 'trouble', 'necessary',
            'throughout', 'challenge', 'fear', 'shoulder', 'institution', 'middle', 'sea',
            'dream', 'bar', 'beautiful', 'property', 'instead', 'improve', 'stuff', 'claim'
        }
        
        # Common corrections
        self.corrections = {
            'hellow': 'hello', 'wrold': 'world', 'teh': 'the', 'adn': 'and',
            'recieve': 'receive', 'seperate': 'separate', 'definately': 'definitely',
            'occured': 'occurred', 'begining': 'beginning', 'untill': 'until',
            'wich': 'which', 'thier': 'their', 'freind': 'friend', 'beleive': 'believe',
            'achive': 'achieve', 'wierd': 'weird', 'neccessary': 'necessary',
            'embarass': 'embarrass', 'accomodate': 'accommodate', 'existance': 'existence',
            'maintainance': 'maintenance', 'occassion': 'occasion', 'priviledge': 'privilege',
            'recomend': 'recommend', 'succesful': 'successful', 'tommorrow': 'tomorrow',
            'truely': 'truly', 'usefull': 'useful', 'wether': 'whether',
            'youre': 'you are', 'its': 'it is', 'dont': 'do not', 'cant': 'cannot',
            'wont': 'will not', 'shouldnt': 'should not', 'couldnt': 'could not',
            'wouldnt': 'would not', 'isnt': 'is not', 'arent': 'are not',
            'wasnt': 'was not', 'werent': 'were not', 'hasnt': 'has not',
            'havent': 'have not', 'hadnt': 'had not', 'doesnt': 'does not',
            'didnt': 'did not', 'im': 'I am', 'ive': 'I have', 'ill': 'I will',
            'id': 'I would', 'youll': 'you will', 'youd': 'you would',
            'youve': 'you have', 'hes': 'he is', 'hed': 'he would',
            'hell': 'he will', 'shes': 'she is', 'shed': 'she would',
            'shell': 'she will', 'were': 'we are', 'wed': 'we would',
            'well': 'we will', 'weve': 'we have', 'theyre': 'they are',
            'theyd': 'they would', 'theyll': 'they will', 'theyve': 'they have'
        }
    
    def check_text(self, text):
        words = re.findall(r'\b\w+\b', text.lower())
        mistakes = []
        
        for word in words:
            if word not in self.dictionary:
                if word in self.corrections:
                    mistakes.append(f"'{word}' -> '{self.corrections[word]}'")
                else:
                    # Simple suggestion based on common patterns
                    suggestion = self.get_suggestion(word)
                    mistakes.append(f"'{word}' -> '{suggestion}'")
        
        if not mistakes:
            return "No spelling mistakes found!"
        
        return f"Spelling mistakes: {', '.join(mistakes)}"
    
    def get_suggestion(self, word):
        # Simple suggestion logic
        if word in self.corrections:
            return self.corrections[word]
        
        # Check for common patterns
        for correct_word in self.dictionary:
            if len(word) == len(correct_word):
                diff_count = sum(1 for a, b in zip(word, correct_word) if a != b)
                if diff_count == 1:  # Only one character different
                    return correct_word
        
        return "No suggestion"
    
    def check_from_camera(self):
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            cv2.putText(frame, "Press 's' to scan text, 'q' to quit", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow('Spell Checker Camera', frame)
            
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
    checker = SpellCheckerApp()
    
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