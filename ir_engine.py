import json
import math
import numpy as np
from collections import defaultdict, Counter
from sentence_transformers import SentenceTransformer
#pip instasll sentence-transformers



class IREngine:
    def __init__(self, data_path="processed.json"):
        self.data_path = data_path
        self.documents = []
        self.inverted_index = defaultdict(list)
        self.doc_lengths = {}
        self.avg_doc_length = 0
        self.N = 0

        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.doc_embeddings = None

        self.load_data()
        self.build_inverted_index()
        self.build_embeddings()

    def load_data(self):
        with open(self.data_path, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        self.N = len(self.documents)

        total_length = 0
        for i, doc in enumerate(self.documents):
            tokens = doc.get("tokens", [])
            self.doc_lengths[i] = len(tokens)
            total_length += len(tokens)

        self.avg_doc_length = total_length / self.N if self.N > 0 else 0

    def build_inverted_index(self):
        for doc_id, doc in enumerate(self.documents):
            tokens = doc.get("tokens", [])
            term_freq = Counter(tokens)

            for term, freq in term_freq.items():
                self.inverted_index[term].append({
                    "doc_id": doc_id,
                    "freq": freq
                })

    def bm25_score(self, query_tokens, doc_id, k1=1.5, b=0.75):
        score = 0
        doc_len = self.doc_lengths.get(doc_id, 0)

        for term in query_tokens:
            postings = self.inverted_index.get(term, [])
            df = len(postings)

            if df == 0:
                continue

            idf = math.log(1 + (self.N - df + 0.5) / (df + 0.5))

            freq = 0
            for posting in postings:
                if posting["doc_id"] == doc_id:
                    freq = posting["freq"]
                    break

            numerator = freq * (k1 + 1)
            denominator = freq + k1 * (1 - b + b * doc_len / self.avg_doc_length)

            score += idf * (numerator / denominator)

        return score

    def lexical_search(self, query, top_k=10):
        query_tokens = self.process_query(query)
        candidate_docs = set()

        for term in query_tokens:
            for posting in self.inverted_index.get(term, []):
                candidate_docs.add(posting["doc_id"])

        results = []

        for doc_id in candidate_docs:
            score = self.bm25_score(query_tokens, doc_id)
            results.append((doc_id, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def build_embeddings(self):
        texts = []

        for doc in self.documents:
            text_parts = [
                doc.get("title", ""),
                doc.get("description", ""),
                doc.get("readme", ""),
                " ".join(doc.get("tokens", []))
            ]
            texts.append(" ".join(text_parts))

        self.doc_embeddings = self.embedding_model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

    def semantic_search(self, query, top_k=10):
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )[0]

        similarities = np.dot(self.doc_embeddings, query_embedding)

        ranked = sorted(
            enumerate(similarities),
            key=lambda x: x[1],
            reverse=True
        )

        return ranked[:top_k]

    def hybrid_search(self, query, top_k=10, alpha=0.6):
        bm25_results = self.lexical_search(query, top_k=50)
        semantic_results = self.semantic_search(query, top_k=50)

        scores = defaultdict(lambda: {
            "bm25": 0,
            "semantic": 0
        })

        max_bm25 = max([score for _, score in bm25_results], default=1)

        for doc_id, score in bm25_results:
            scores[doc_id]["bm25"] = score / max_bm25 if max_bm25 > 0 else 0

        for doc_id, score in semantic_results:
            scores[doc_id]["semantic"] = float(score)

        final_results = []

        for doc_id, score_data in scores.items():
            final_score = (
                alpha * score_data["bm25"]
                + (1 - alpha) * score_data["semantic"]
            )

            doc = self.documents[doc_id]

            final_results.append({
                "id": doc_id,
                "title": doc.get("title", "No title"),
                "url": doc.get("url", ""),
                "description": doc.get("description", ""),
                "stars": doc.get("stars", 0),
                "language": doc.get("language", ""),
                "bm25_score": round(score_data["bm25"], 4),
                "semantic_score": round(score_data["semantic"], 4),
                "final_score": round(final_score, 4)
            })

        final_results.sort(key=lambda x: x["final_score"], reverse=True)
        return final_results[:top_k]

    def process_query(self, query):
        return query.lower().split()


if __name__ == "__main__":
    engine = IREngine("processed.json")

    while True:
        query = input("\nSearch GitHub repos: ")

        if query.lower() in ["exit", "quit"]:
            break

        results = engine.hybrid_search(query)

        for i, result in enumerate(results, 1):
            print(f"\n{i}. {result['title']}")
            print(f"URL: {result['url']}")
            print(f"Description: {result['description']}")
            print(f"BM25 Score: {result['bm25_score']}")
            print(f"Semantic Score: {result['semantic_score']}")
            print(f"Final Score: {result['final_score']}")