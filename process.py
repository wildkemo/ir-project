import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('omw-1.4', quiet=True)
    nltk.download('punkt', quiet=True)
except Exception as e:
    print(f'NLTK download error: {e}')

def clean_text(text):
    if not text:
        return []
    text = text.lower()
    text = re.sub('[^\\w\\s+#]', ' ', text)
    tokens = text.split()
    stop_words = set(stopwords.words('english'))
    languages = {'python', 'javascript', 'typescript', 'go', 'rust', 'java', 'cpp', 'c++', 'c#', 'csharp', 'php', 'ruby', 'swift', 'kotlin', 'sql', 'shell', 'bash', 'perl', 'scala', 'dart', 'lua', 'html', 'css', 'web', 'react', 'node', 'vue', 'angular', 'docker', 'kubernetes'}
    extra_stop_words = {'that', 'about', 'is', 'it', 'to', 'in', 'on', 'of', 'at', 'by', 'for', 'with', 'from', 'was', 'were', 'has', 'have', 'had', 'been', 'be', 'an', 'and', 'the', 'a', 'software', 'open', 'source', 'project', 'repository', 'application', 'tool', 'github', 'readme', 'license', 'contributing', 'contributor', 'star', 'fork', 'watching', 'watchers', 'activity', 'report', 'properties', 'custom', 'loading', 'error', 'page', 'please', 'reload', 'oh', 'uh', 'contribution', 'development', 'create', 'account', 'using', 'build', 'framework', 'library', 'platform', 'system', 'use', 'support', 'version', 'free', 'list', 'resource', 'code', 'data', 'model', 'learn', 'machine'}
    stop_words.update(extra_stop_words)
    stemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()
    processed_tokens = []
    for token in tokens:
        if token in languages:
            processed_tokens.append(token)
            continue
        if len(token) <= 1:
            continue
        lemma = lemmatizer.lemmatize(token)
        stem = stemmer.stem(lemma)
        if stem not in stop_words and lemma not in stop_words and (token not in stop_words):
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
        print(f'Processed {len(processed)} records with Stemming and Lemmatization.')
    except Exception as e:
        print(f'Error: {e}')
if __name__ == '__main__':
    process_data()
