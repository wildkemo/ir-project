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
    
    # Normalization: Lowercase
    text = text.lower()
    
    # Special preservation for C++ and C# before general punctuation removal
    # We replace them with placeholders or just allow # and + in the regex
    # But C++ uses ++ which might be part of other things. 
    # Let's just allow + and # in the word regex for now.
    text = re.sub(r'[^\w\s+#]', ' ', text)
    
    # Tokenization
    tokens = text.split()
    
    # Improved Stopwords removal
    stop_words = set(stopwords.words('english'))
    
    # Comprehensive Programming Languages list
    languages = {
        'python', 'javascript', 'typescript', 'go', 'rust', 'java', 'cpp', 'c++', 'c#', 'csharp',
        'php', 'ruby', 'swift', 'kotlin', 'sql', 'shell', 'bash', 'perl', 'scala', 'dart', 'lua',
        'html', 'css', 'web', 'react', 'node', 'vue', 'angular', 'docker', 'kubernetes'
    }
    
    # Adding extra words identified as "invalid" or noisy
    extra_stop_words = {
        'that', 'about', 'is', 'it', 'to', 'in', 'on', 'of', 'at', 'by', 'for', 'with', 'from', 'was', 'were', 'has', 'have', 'had', 'been', 'be', 'an', 'and', 'the', 'a', 
        'software', 'open', 'source', 'project', 'repository', 'application', 'tool', 'github', 'readme', 'license', 'contributing', 'contributor', 'star', 'fork', 
        'watching', 'watchers', 'activity', 'report', 'properties', 'custom', 'loading', 'error', 'page', 'please', 'reload', 'oh', 'uh', 'contribution', 'development',
        'create', 'account', 'using', 'build', 'framework', 'library', 'platform', 'system', 'use', 'support', 'version', 'free', 'list', 'resource', 'code', 'data',
        'model', 'learn', 'machine'
    }
    
    stop_words.update(extra_stop_words)
    
    # Initialize Stemmer and Lemmatizer
    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    
    processed_tokens = []
    for token in tokens:
        # Don't stem languages to avoid "python" -> "python" (ok) but "ruby" -> "rubi" (bad)
        if token in languages:
            processed_tokens.append(token)
            continue
            
        if len(token) <= 1: continue # Allow 'c' if needed but maybe 1 is too short
        
        # Lemmatize and Stem others
        lemma = lemmatizer.lemmatize(token)
        stem = stemmer.stem(lemma)
        
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
