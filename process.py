import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

# Ensure necessary NLTK resources are downloaded
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    nltk.download('punkt', quiet=True)
except Exception as e:
    print(f"NLTK download error: {e}")

def clean_text(text):
    if not text: return []
    
    # Normalization: Lowercase and remove punctuation
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    
    # Tokenization
    tokens = text.split()
    
    # Improved Stopwords removal
    stop_words = set(stopwords.words('english'))
    # Adding extra words identified as "invalid" or noisy for this specific context
    extra_stop_words = {'that', 'about', 'is', 'it', 'to', 'in', 'on', 'of', 'at', 'by', 'for', 'with', 'from', 'was', 'were', 'has', 'have', 'had', 'been', 'be', 'an', 'and', 'the', 'a', 'software', 'open', 'source', 'project', 'repository', 'application', 'tool'}
    stop_words.update(extra_stop_words)
    
    # Initialize Stemmer and Lemmatizer
    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    
    # Process tokens: Lemmatize -> Stem -> Filter Stopwords
    processed_tokens = []
    for token in tokens:
        if len(token) <= 2: continue
        
        # Lemmatize and Stem
        lemma = lemmatizer.lemmatize(token)
        stem = stemmer.stem(lemma)
        
        # Filter against stop_words (including processed versions of noisy words)
        if stem not in stop_words and lemma not in stop_words and token not in stop_words:
            processed_tokens.append(stem)
        
    return processed_tokens

def process_data():
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
        processed = []
        for item in data:
            item['tokens'] = clean_text(item['content'])
            item['title_tokens'] = clean_text(item['title'])
            processed.append(item)
        with open('processed.json', 'w') as f:
            json.dump(processed, f, indent=4)
        print(f"Processed {len(processed)} records with Stemming and Lemmatization.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_data()
