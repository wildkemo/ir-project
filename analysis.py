import json
from collections import Counter


# =========================
# BAR CHART UTILITY
# =========================
def create_bar_chart(data, max_width=30):
    if not data:
        return "  (No data available)"

    max_val = max(v for _, v in data)

    chart = ""
    for label, value in data:
        bar_len = int((value / max_val) * max_width)
        bar = "█" * bar_len
        chart += f"  {label:<12} | {bar} {value}\n"

    return chart


# =========================
# MAIN ANALYSIS
# =========================
def run_analysis():

    try:
        with open("processed.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            print("Empty dataset.")
            return

        # =========================
        # BASIC STATS
        # =========================
        total_docs = len(data)
        all_tokens = []
        doc_lengths = []

        for d in data:
            tokens = d.get("tokens", [])
            all_tokens.extend(tokens)
            doc_lengths.append(len(tokens))

        avg_doc_length = sum(doc_lengths) / total_docs
        unique_tokens = len(set(all_tokens))
        vocab_size = len(all_tokens)
        vocab_density = (unique_tokens / vocab_size) * 100 if vocab_size else 0

        # =========================
        # TOKEN FREQUENCY
        # =========================
        freq = Counter(all_tokens)

        # =========================
        # LANGUAGE ANALYSIS
        # =========================
        languages = Counter([d.get("language") for d in data if d.get("language")])

        # =========================
        # TOPICS ANALYSIS
        # =========================
        topics = []
        for d in data:
            topics.extend(d.get("topics", []))

        topic_counts = Counter(topics)

        # =========================
        # POPULARITY ANALYSIS
        # =========================
        stars = [d.get("stars", 0) for d in data]
        forks = [d.get("forks", 0) for d in data]

        avg_stars = sum(stars) / total_docs
        avg_forks = sum(forks) / total_docs

        top_starred = sorted(data, key=lambda x: x.get("stars", 0), reverse=True)[:5]
        top_forked = sorted(data, key=lambda x: x.get("forks", 0), reverse=True)[:5]

        # =========================
        # REPORT OUTPUT
        # =========================
        print("\n" + "=" * 60)
        print("      🚀 INFORMATION RETRIEVAL SYSTEM ANALYSIS")
        print("=" * 60)

        print("\n[📊 DATASET OVERVIEW]")
        print(f"  • Documents: {total_docs}")
        print(f"  • Avg Document Length: {avg_doc_length:.2f} tokens")
        print(f"  • Total Tokens: {vocab_size}")
        print(f"  • Unique Tokens: {unique_tokens}")
        print(f"  • Vocabulary Density: {vocab_density:.2f}%")

        print("\n[⭐ POPULARITY INSIGHTS]")
        print(f"  • Avg Stars: {avg_stars:.2f}")
        print(f"  • Avg Forks: {avg_forks:.2f}")

        print("\n[🏆 TOP STARRED REPOSITORIES]")
        for i, repo in enumerate(top_starred, 1):
            print(f"  {i}. {repo.get('title')} ({repo.get('stars')} ⭐)")

        print("\n[🍴 TOP FORKED REPOSITORIES]")
        for i, repo in enumerate(top_forked, 1):
            print(f"  {i}. {repo.get('title')} ({repo.get('forks')} forks)")

        print("\n[💻 TOP PROGRAMMING LANGUAGES]")
        print(create_bar_chart(languages.most_common(8)))

        print("\n[🔥 TOP TERMS (IR SIGNALS)]")
        for i, (word, count) in enumerate(freq.most_common(10), 1):
            print(f"  {i}. {word:<15} ({count})")

        print("\n[📚 TOP TOPICS]")
        print(create_bar_chart(topic_counts.most_common(8)))

        print("\n" + "=" * 60)
        print("      Analysis Complete — IR dataset ready")
        print("=" * 60 + "\n")

    except FileNotFoundError:
        print("Error: processed.json not found. Run process.py first.")

    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    run_analysis()