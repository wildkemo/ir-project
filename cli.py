import json
from search import search
from sentiment import get_sentiment

def main():
    print("Welcome to Entertainment Analytics Dashboard")
    try:
        with open('processed.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Data not processed. Run scraper.py and process.py first.")
        return

    while True:
        print("\nCommands: [s] Search, [a] Analysis, [q] Quit")
        cmd = input("Choice: ").lower()
        
        if cmd == 'q':
            break
        elif cmd == 'a':
            import analysis
            analysis.run_analysis()
        elif cmd == 's':
            query = input("Enter search query: ")
            results = search(query, data)
            print(f"\nFound {len(results)} results:")
            for r in results[:5]: # Show top 5
                sentiment = get_sentiment(r['content'])
                print(f"- {r['title']} | Sentiment: {sentiment}")
                print(f"  Snippet: {r['content'][:100]}...")
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()
