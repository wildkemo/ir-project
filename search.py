import json

def search(query, data):
    query_tokens = query.lower().split()
    results = []
    for item in data:
        score = 0
        # Simple IR: count matching tokens in content and title
        combined_tokens = item['tokens'] + item['title_tokens']
        for qt in query_tokens:
            if qt in combined_tokens:
                score += 1
        if score > 0:
            results.append((score, item))
            
    # Sort by score descending
    results.sort(key=lambda x: x[0], reverse=True)
    return [r[1] for r in results]
