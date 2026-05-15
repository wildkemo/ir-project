from ir_engine import IREngine


def print_results(results):
    if not results:
        print("\nNo results found.")
        return

    print("\nTop Results:\n")

    for i, r in enumerate(results, 1):
        print(f"Rank #{i}")
        print("-" * 40)
        print(f"Title   : {r['title']}")
        print(f"URL     : {r['url']}")
        print(f"Score   : {r['score']}")
        print(f"Stars   : {r['stars']}")
        print(f"Forks   : {r['forks']}")
        print(f"Language: {r['language']}")
        print(f"Topics  : {', '.join(r['topics']) if r['topics'] else 'N/A'}")
        print("-" * 40)


def main():
    print("===================================")
    print("   GitHub Code IR Search Engine")
    print("===================================\n")

    print("[Loading IR Engine...]")
    engine = IREngine("processed.json")
    print("[Ready]\n")

    print("Type your query below (or type 'exit' to quit)\n")

    while True:
        query = input("Search > ").strip()

        if query.lower() == "exit":
            print("\nGoodbye!")
            break

        if not query:
            continue

        results = engine.search(query, top_k=10)
        print_results(results)


if __name__ == "__main__":
    main()