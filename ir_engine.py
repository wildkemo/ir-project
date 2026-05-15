import json
import math
from collections import defaultdict, Counter


class IREngine:
    def __init__(self, data_path="processed.json"):
        with open(data_path, "r", encoding="utf-8") as f:
            self.docs = json.load(f)

        self.N = len(self.docs)

        # IR structures
        self.inverted_index = defaultdict(list)
        self.doc_freq = defaultdict(int)

        # build everything
        self.build_index()

    # =========================
    # BUILD INVERTED INDEX
    # =========================
    def build_index(self):
        for doc_id, doc in enumerate(self.docs):
            tokens = doc.get("tokens", [])

            unique_tokens = set(tokens)

            for token in unique_tokens:
                self.inverted_index[token].append(doc_id)
                self.doc_freq[token] += 1

        print(f"[INFO] Indexed {self.N} documents")
        print(f"[INFO] Vocabulary size: {len(self.inverted_index)}")

    # =========================
    # TF (TERM FREQUENCY)
    # =========================
    def tf(self, term, doc_tokens):
        return doc_tokens.count(term) / len(doc_tokens) if doc_tokens else 0

    # =========================
    # IDF (INVERSE DOC FREQ)
    # =========================
    def idf(self, term):
        df = self.doc_freq.get(term, 0)
        return math.log((self.N + 1) / (df + 1)) + 1

    # =========================
    # BM25 SCORE
    # =========================
    def bm25(self, query_terms, doc, k1=1.5, b=0.75):

        doc_tokens = doc.get("tokens", [])
        doc_len = len(doc_tokens)

        avgdl = sum(len(d["tokens"]) for d in self.docs) / self.N

        token_counts = Counter(doc_tokens)

        score = 0

        for term in query_terms:

            if term not in token_counts:
                continue

            df = self.doc_freq.get(term, 0)
            idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1)

            tf = token_counts[term]

            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_len / avgdl))

            score += idf * (numerator / denominator)

        return score

    # =========================
    # POPULARITY SCORE
    # =========================
    def popularity_score(self, doc):
        stars = doc.get("stars", 0)
        forks = doc.get("forks", 0)

        return math.log1p(stars) + math.log1p(forks)

    # =========================
    # MAIN RANKING FUNCTION
    # =========================
    def rank(self, query):
        query_terms = query.lower().split()

        results = []

        for doc_id, doc in enumerate(self.docs):

            bm25_score = self.bm25(query_terms, doc)
            pop_score = self.popularity_score(doc)

            # FINAL HYBRID SCORE
            final_score = (0.7 * bm25_score) + (0.3 * pop_score)

            results.append((final_score, doc))

        results.sort(reverse=True, key=lambda x: x[0])

        return results

    # =========================
    # SEARCH FUNCTION (API)
    # =========================
    def search(self, query, top_k=10):

        ranked = self.rank(query)

        output = []

        for score, doc in ranked[:top_k]:

            output.append({
                "title": doc.get("title"),
                "url": doc.get("url"),
                "score": round(score, 4),
                "stars": doc.get("stars", 0),
                "forks": doc.get("forks", 0),
                "language": doc.get("language"),
                "topics": doc.get("topics", [])
            })

        return output


# =========================
# TEST RUN (OPTIONAL)
# =========================
if __name__ == "__main__":

    engine = IREngine("processed.json")

    while True:
        query = input("\nSearch query (or 'exit'): ")

        if query.lower() == "exit":
            break

        results = engine.search(query)

        print("\nTop Results:\n")

        for r in results:
            print("----------------------------")
            print("Title:", r["title"])
            print("URL:", r["url"])
            print("Score:", r["score"])
            print("Stars:", r["stars"])
            print("Forks:", r["forks"])
            print("Language:", r["language"])