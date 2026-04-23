import json
from collections import Counter

def run_analysis():
    try:
        with open('processed.json', 'r') as f:
            data = json.load(f)
        
        all_tokens = []
        for item in data:
            all_tokens.extend(item['tokens'])
        
        counts = Counter(all_tokens)
        common = counts.most_common(10)
        
        print("--- Data Analysis ---")
        print(f"Total Records: {len(data)}")
        print(f"Total Tokens: {len(all_tokens)}")
        print("Top Keywords:")
        for word, count in common:
            print(f"- {word}: {count}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_analysis()
