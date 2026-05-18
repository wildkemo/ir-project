"""
Hybrid Search Engine for Open-Source GitHub Repository Search

Features:
- BM25 lexical search
- Sentence-transformer semantic search
- Cosine similarity over dense embeddings
- Phrase/context matching
- Metadata-aware ranking using popularity, activity, and quality scores
- Similar-project recommendation
- Save/load index for faster startup

Expected input:
    processed.json

This file is designed to work with the processed output from your process.py pipeline.
"""

import json
import math
import os
import pickle
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


# ======================================================
# Utility functions
# ======================================================

def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except Exception:
        return default


def min_max_normalize(values: np.ndarray) -> np.ndarray:
    """Normalize an array to [0, 1]."""
    values = np.asarray(values, dtype=np.float32)

    if len(values) == 0:
        return values

    min_val = float(np.min(values))
    max_val = float(np.max(values))

    if math.isclose(min_val, max_val):
        return np.zeros_like(values, dtype=np.float32)

    return (values - min_val) / (max_val - min_val)


def cosine_similarity_matrix(query_vector: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity between one query vector and a matrix of vectors.

    query_vector shape: (dim,)
    matrix shape: (num_docs, dim)
    returns shape: (num_docs,)
    """
    query_vector = np.asarray(query_vector, dtype=np.float32)
    matrix = np.asarray(matrix, dtype=np.float32)

    query_norm = np.linalg.norm(query_vector)
    matrix_norms = np.linalg.norm(matrix, axis=1)

    denominator = matrix_norms * query_norm
    denominator = np.where(denominator == 0, 1e-9, denominator)

    return np.dot(matrix, query_vector) / denominator


def clean_query_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s+#.\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_query(text: str) -> List[str]:
    """
    Lightweight tokenizer for query processing.
    Keep programming-language terms such as c++, c#, node.js, .net.
    """
    text = clean_query_text(text)
    if not text:
        return []
    return text.split()


def build_document_text(repo: Dict[str, Any]) -> str:
    """
    Build a natural-language document representation for semantic search.
    This is different from BM25 tokens because embeddings understand phrases better
    when the text is closer to natural language.
    """
    title = repo.get("title") or repo.get("name") or repo.get("repo") or ""
    full_name = repo.get("full_name") or ""
    description = repo.get("description") or ""
    language = repo.get("language") or ""
    license_name = repo.get("license") or ""
    topics = repo.get("topics") or []

    if isinstance(topics, list):
        topics_text = ", ".join(str(t) for t in topics)
    else:
        topics_text = str(topics)

    # Use processed_text if available, but do not rely only on it because it may be stemmed.
    processed_text = repo.get("processed_text") or ""

    return " ".join([
        f"Repository: {full_name} {title}.",
        f"Description: {description}.",
        f"Programming language: {language}.",
        f"Topics: {topics_text}.",
        f"License: {license_name}.",
        f"Content: {processed_text}"
    ]).strip()


# ======================================================
# Search result data structure
# ======================================================

@dataclass
class SearchResult:
    rank: int
    repo: Dict[str, Any]
    final_score: float
    bm25_score: float
    semantic_score: float
    phrase_score: float
    metadata_score: float

    def to_dict(self) -> Dict[str, Any]:
        repo = self.repo

        return {
            "rank": self.rank,
            "score": round(self.final_score, 6),
            "bm25_score": round(self.bm25_score, 6),
            "semantic_score": round(self.semantic_score, 6),
            "phrase_score": round(self.phrase_score, 6),
            "metadata_score": round(self.metadata_score, 6),
            "id": repo.get("id"),
            "title": repo.get("title") or repo.get("name") or repo.get("repo"),
            "full_name": repo.get("full_name"),
            "url": repo.get("url"),
            "description": repo.get("description"),
            "language": repo.get("language"),
            "topics": repo.get("topics", []),
            "license": repo.get("license"),
            "stars": repo.get("stars", 0),
            "forks": repo.get("forks", 0),
            "watchers": repo.get("watchers", 0),
            "issues": repo.get("issues", repo.get("open_issues", 0)),
            "popularity_score": repo.get("popularity_score", 0),
            "activity_score": repo.get("activity_score", 0),
            "quality_score": repo.get("quality_score", 0),
        }


# ======================================================
# Hybrid search engine
# ======================================================

class HybridSearchEngine:
    """
    A real hybrid IR engine:
    - BM25 handles exact keyword relevance.
    - Sentence embeddings handle meaning/context.
    - Cosine similarity compares the query embedding with repo embeddings.
    - Phrase score boosts exact phrase/context matches.
    - Metadata score boosts useful, active, high-quality repositories.
    """

    def __init__(
        self,
        processed_file: str = "processed.json",
        index_dir: str = "search_index",
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        bm25_weight: float = 0.35,
        semantic_weight: float = 0.45,
        phrase_weight: float = 0.10,
        metadata_weight: float = 0.10,
    ):
        self.processed_file = processed_file
        self.index_dir = index_dir
        self.embedding_model_name = embedding_model_name

        self.bm25_weight = bm25_weight
        self.semantic_weight = semantic_weight
        self.phrase_weight = phrase_weight
        self.metadata_weight = metadata_weight

        self.repos: List[Dict[str, Any]] = []
        self.bm25: Optional[BM25Okapi] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.embeddings: Optional[np.ndarray] = None
        self.document_texts: List[str] = []
        self.bm25_corpus: List[List[str]] = []

    # ==================================================
    # Loading data
    # ==================================================
    def load_processed_data(self) -> None:
        if not os.path.exists(self.processed_file):
            raise FileNotFoundError(f"Could not find {self.processed_file}")

        with open(self.processed_file, "r", encoding="utf-8") as file:
            self.repos = json.load(file)

        if not isinstance(self.repos, list):
            raise ValueError("processed.json must contain a list of repositories")

        self.document_texts = [build_document_text(repo) for repo in self.repos]

        self.bm25_corpus = []
        for repo in self.repos:
            tokens = repo.get("tokens")

            if isinstance(tokens, list) and tokens:
                self.bm25_corpus.append([str(token).lower() for token in tokens])
            else:
                self.bm25_corpus.append(tokenize_query(build_document_text(repo)))

    # ==================================================
    # Building index
    # ==================================================
    def build_index(self, batch_size: int = 64, save: bool = True) -> None:
        print("Loading processed data...")
        self.load_processed_data()

        print(f"Loaded {len(self.repos)} repositories.")

        print("Building BM25 index...")
        self.bm25 = BM25Okapi(self.bm25_corpus)

        print(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)

        print("Encoding repository documents for semantic search...")
        self.embeddings = self.embedding_model.encode(
            self.document_texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype(np.float32)

        if save:
            self.save_index()

        print("Search index is ready.")

    # ==================================================
    # Save / load index
    # ==================================================
    def save_index(self) -> None:
        os.makedirs(self.index_dir, exist_ok=True)

        with open(os.path.join(self.index_dir, "repos.pkl"), "wb") as file:
            pickle.dump(self.repos, file)

        with open(os.path.join(self.index_dir, "document_texts.pkl"), "wb") as file:
            pickle.dump(self.document_texts, file)

        with open(os.path.join(self.index_dir, "bm25_corpus.pkl"), "wb") as file:
            pickle.dump(self.bm25_corpus, file)

        with open(os.path.join(self.index_dir, "bm25.pkl"), "wb") as file:
            pickle.dump(self.bm25, file)

        np.save(os.path.join(self.index_dir, "embeddings.npy"), self.embeddings)

        config = {
            "embedding_model_name": self.embedding_model_name,
            "bm25_weight": self.bm25_weight,
            "semantic_weight": self.semantic_weight,
            "phrase_weight": self.phrase_weight,
            "metadata_weight": self.metadata_weight,
        }

        with open(os.path.join(self.index_dir, "config.json"), "w", encoding="utf-8") as file:
            json.dump(config, file, indent=4)

        print(f"Saved index to {self.index_dir}")

    def load_index(self) -> None:
        required_files = [
            "repos.pkl",
            "document_texts.pkl",
            "bm25_corpus.pkl",
            "bm25.pkl",
            "embeddings.npy",
        ]

        for filename in required_files:
            path = os.path.join(self.index_dir, filename)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing index file: {path}")

        with open(os.path.join(self.index_dir, "repos.pkl"), "rb") as file:
            self.repos = pickle.load(file)

        with open(os.path.join(self.index_dir, "document_texts.pkl"), "rb") as file:
            self.document_texts = pickle.load(file)

        with open(os.path.join(self.index_dir, "bm25_corpus.pkl"), "rb") as file:
            self.bm25_corpus = pickle.load(file)

        with open(os.path.join(self.index_dir, "bm25.pkl"), "rb") as file:
            self.bm25 = pickle.load(file)

        self.embeddings = np.load(os.path.join(self.index_dir, "embeddings.npy")).astype(np.float32)

        config_path = os.path.join(self.index_dir, "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as file:
                config = json.load(file)
            self.embedding_model_name = config.get("embedding_model_name", self.embedding_model_name)

        print(f"Loading embedding model: {self.embedding_model_name}")
        self.embedding_model = SentenceTransformer(self.embedding_model_name)

        print(f"Loaded search index with {len(self.repos)} repositories.")

    # ==================================================
    # Scoring
    # ==================================================
    def compute_bm25_scores(self, query: str) -> np.ndarray:
        if self.bm25 is None:
            raise RuntimeError("BM25 index is not loaded.")

        query_tokens = tokenize_query(query)

        if not query_tokens:
            return np.zeros(len(self.repos), dtype=np.float32)

        scores = self.bm25.get_scores(query_tokens)
        return np.asarray(scores, dtype=np.float32)

    def compute_semantic_scores(self, query: str) -> np.ndarray:
        if self.embedding_model is None or self.embeddings is None:
            raise RuntimeError("Semantic index is not loaded.")

        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0].astype(np.float32)

        # Since embeddings are normalized, dot product is cosine similarity.
        scores = cosine_similarity_matrix(query_embedding, self.embeddings)
        return np.asarray(scores, dtype=np.float32)

    def compute_phrase_scores(self, query: str) -> np.ndarray:
        """
        Phrase score rewards repositories that contain the query phrase or important
        subphrases in title, description, topics, or processed text.
        """
        clean_query = clean_query_text(query)
        query_tokens = tokenize_query(query)

        if not clean_query or not query_tokens:
            return np.zeros(len(self.repos), dtype=np.float32)

        scores = np.zeros(len(self.repos), dtype=np.float32)

        # Important bigrams/trigrams help context such as "web framework", "machine learning".
        query_bigrams = [
            " ".join(query_tokens[i:i + 2])
            for i in range(len(query_tokens) - 1)
        ]
        query_trigrams = [
            " ".join(query_tokens[i:i + 3])
            for i in range(len(query_tokens) - 2)
        ]

        for i, repo in enumerate(self.repos):
            title = str(repo.get("title") or repo.get("name") or repo.get("repo") or "").lower()
            description = str(repo.get("description") or "").lower()
            topics = repo.get("topics") or []
            topics_text = " ".join(str(t).replace("-", " ") for t in topics).lower()
            processed_text = str(repo.get("processed_text") or "").lower()

            field_text = " ".join([title, description, topics_text, processed_text])

            score = 0.0

            # Exact phrase match is strong.
            if clean_query in field_text:
                score += 1.0

            # Title/description phrase match is very strong.
            if clean_query in title:
                score += 1.5
            if clean_query in description:
                score += 1.2

            # Bigrams/trigrams capture query context.
            for phrase in query_bigrams:
                if phrase in title:
                    score += 0.50
                elif phrase in description:
                    score += 0.35
                elif phrase in topics_text:
                    score += 0.30
                elif phrase in processed_text:
                    score += 0.10

            for phrase in query_trigrams:
                if phrase in title:
                    score += 0.75
                elif phrase in description:
                    score += 0.55
                elif phrase in topics_text:
                    score += 0.45
                elif phrase in processed_text:
                    score += 0.15

            scores[i] = score

        return scores

    def compute_metadata_scores(self) -> np.ndarray:
        """
        Metadata score favors useful and healthy repos, but only mildly.
        Relevance should mainly come from BM25 + semantic search.
        """
        scores = []

        for repo in self.repos:
            popularity = safe_float(repo.get("popularity_score"), 0.0)
            activity = safe_float(repo.get("activity_score"), 0.0)
            quality = safe_float(repo.get("quality_score"), 0.0)

            # Fallback if process.py did not compute scores.
            if popularity == 0.0:
                stars = safe_float(repo.get("stars"), 0.0)
                forks = safe_float(repo.get("forks"), 0.0)
                watchers = safe_float(repo.get("watchers"), 0.0)
                popularity = (
                    0.60 * math.log1p(stars) +
                    0.30 * math.log1p(forks) +
                    0.10 * math.log1p(watchers)
                )

            metadata_score = (
                0.50 * popularity +
                0.25 * activity +
                0.25 * quality
            )

            scores.append(metadata_score)

        return np.asarray(scores, dtype=np.float32)

    # ==================================================
    # Filters
    # ==================================================
    def apply_filters(
        self,
        candidate_indices: List[int],
        language: Optional[str] = None,
        license_name: Optional[str] = None,
        min_stars: Optional[int] = None,
        topic: Optional[str] = None,
    ) -> List[int]:
        filtered = []

        for idx in candidate_indices:
            repo = self.repos[idx]

            if language:
                repo_language = str(repo.get("language") or "").lower()
                if repo_language != language.lower():
                    continue

            if license_name:
                repo_license = str(repo.get("license") or "").lower()
                if repo_license != license_name.lower():
                    continue

            if min_stars is not None:
                if safe_float(repo.get("stars"), 0.0) < min_stars:
                    continue

            if topic:
                topics = [str(t).lower() for t in repo.get("topics", []) or []]
                normalized_topic = topic.lower()
                if normalized_topic not in topics:
                    continue

            filtered.append(idx)

        return filtered

    # ==================================================
    # Main search function
    # ==================================================
    def search(
        self,
        query: str,
        top_k: int = 10,
        candidate_pool: int = 200,
        language: Optional[str] = None,
        license_name: Optional[str] = None,
        min_stars: Optional[int] = None,
        topic: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not query or not query.strip():
            return []

        if self.bm25 is None or self.embedding_model is None or self.embeddings is None:
            raise RuntimeError("Index is not loaded. Call build_index() or load_index() first.")

        # 1. Compute scores from different retrieval models.
        raw_bm25_scores = self.compute_bm25_scores(query)
        raw_semantic_scores = self.compute_semantic_scores(query)
        raw_phrase_scores = self.compute_phrase_scores(query)
        raw_metadata_scores = self.compute_metadata_scores()

        # 2. Normalize scores for safe combination.
        bm25_scores = min_max_normalize(raw_bm25_scores)
        semantic_scores = min_max_normalize(raw_semantic_scores)
        phrase_scores = min_max_normalize(raw_phrase_scores)
        metadata_scores = min_max_normalize(raw_metadata_scores)

        # 3. Hybrid ranking.
        final_scores = (
            self.bm25_weight * bm25_scores +
            self.semantic_weight * semantic_scores +
            self.phrase_weight * phrase_scores +
            self.metadata_weight * metadata_scores
        )

        # 4. Candidate selection.
        candidate_pool = min(candidate_pool, len(self.repos))
        candidate_indices = np.argsort(final_scores)[::-1][:candidate_pool].tolist()

        # 5. Metadata filtering after initial retrieval.
        candidate_indices = self.apply_filters(
            candidate_indices,
            language=language,
            license_name=license_name,
            min_stars=min_stars,
            topic=topic,
        )

        # 6. Final top-k.
        candidate_indices = sorted(
            candidate_indices,
            key=lambda idx: float(final_scores[idx]),
            reverse=True,
        )[:top_k]

        results: List[SearchResult] = []

        for rank, idx in enumerate(candidate_indices, start=1):
            results.append(SearchResult(
                rank=rank,
                repo=self.repos[idx],
                final_score=float(final_scores[idx]),
                bm25_score=float(bm25_scores[idx]),
                semantic_score=float(semantic_scores[idx]),
                phrase_score=float(phrase_scores[idx]),
                metadata_score=float(metadata_scores[idx]),
            ))

        return [result.to_dict() for result in results]

    # ==================================================
    # Recommendation: similar repositories
    # ==================================================
    def recommend_similar(
        self,
        repo_identifier: str,
        top_k: int = 10,
        same_language_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Recommend similar repositories using cosine similarity over repo embeddings.

        repo_identifier can be:
        - full_name, e.g. "psf/requests"
        - url
        - title/name
        """
        if self.embeddings is None:
            raise RuntimeError("Semantic index is not loaded.")

        target_idx = self.find_repo_index(repo_identifier)

        if target_idx is None:
            raise ValueError(f"Repository not found: {repo_identifier}")

        target_repo = self.repos[target_idx]
        target_vector = self.embeddings[target_idx]

        similarities = cosine_similarity_matrix(target_vector, self.embeddings)
        similarities[target_idx] = -1.0

        candidate_indices = np.argsort(similarities)[::-1].tolist()

        results = []
        rank = 1

        for idx in candidate_indices:
            repo = self.repos[idx]

            if same_language_only:
                if str(repo.get("language") or "").lower() != str(target_repo.get("language") or "").lower():
                    continue

            results.append({
                "rank": rank,
                "similarity": round(float(similarities[idx]), 6),
                "title": repo.get("title") or repo.get("name") or repo.get("repo"),
                "full_name": repo.get("full_name"),
                "url": repo.get("url"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "topics": repo.get("topics", []),
                "stars": repo.get("stars", 0),
                "forks": repo.get("forks", 0),
            })

            rank += 1

            if len(results) >= top_k:
                break

        return results

    def find_repo_index(self, repo_identifier: str) -> Optional[int]:
        target = repo_identifier.lower().strip()

        for idx, repo in enumerate(self.repos):
            possible_values = [
                repo.get("full_name"),
                repo.get("url"),
                repo.get("title"),
                repo.get("name"),
                repo.get("repo"),
            ]

            for value in possible_values:
                if value and str(value).lower().strip() == target:
                    return idx

        # Fuzzy contains fallback.
        for idx, repo in enumerate(self.repos):
            full_name = str(repo.get("full_name") or "").lower()
            title = str(repo.get("title") or repo.get("name") or "").lower()
            url = str(repo.get("url") or "").lower()

            if target in full_name or target in title or target in url:
                return idx

        return None

    # ==================================================
    # Debug/explain a search result
    # ==================================================
    def explain_result(self, query: str, repo_identifier: str) -> Dict[str, Any]:
        idx = self.find_repo_index(repo_identifier)
        if idx is None:
            raise ValueError(f"Repository not found: {repo_identifier}")

        bm25_scores = min_max_normalize(self.compute_bm25_scores(query))
        semantic_scores = min_max_normalize(self.compute_semantic_scores(query))
        phrase_scores = min_max_normalize(self.compute_phrase_scores(query))
        metadata_scores = min_max_normalize(self.compute_metadata_scores())

        final_score = (
            self.bm25_weight * bm25_scores[idx] +
            self.semantic_weight * semantic_scores[idx] +
            self.phrase_weight * phrase_scores[idx] +
            self.metadata_weight * metadata_scores[idx]
        )

        repo = self.repos[idx]

        return {
            "query": query,
            "repo": repo.get("full_name") or repo.get("title"),
            "final_score": round(float(final_score), 6),
            "bm25_contribution": round(float(self.bm25_weight * bm25_scores[idx]), 6),
            "semantic_contribution": round(float(self.semantic_weight * semantic_scores[idx]), 6),
            "phrase_contribution": round(float(self.phrase_weight * phrase_scores[idx]), 6),
            "metadata_contribution": round(float(self.metadata_weight * metadata_scores[idx]), 6),
            "raw_parts": {
                "bm25_score": round(float(bm25_scores[idx]), 6),
                "semantic_score": round(float(semantic_scores[idx]), 6),
                "phrase_score": round(float(phrase_scores[idx]), 6),
                "metadata_score": round(float(metadata_scores[idx]), 6),
            }
        }


# ======================================================
# CLI demo
# ======================================================

def print_results(results: List[Dict[str, Any]]) -> None:
    if not results:
        print("No results found.")
        return

    for result in results:
        print("=" * 80)
        print(f"#{result['rank']} | Score: {result['score']}")
        print(f"Repo: {result.get('full_name') or result.get('title')}")
        print(f"URL: {result.get('url')}")
        print(f"Language: {result.get('language')} | Stars: {result.get('stars')} | Forks: {result.get('forks')}")
        print(f"Topics: {', '.join(result.get('topics') or [])}")
        print(f"Description: {result.get('description')}")
        print(
            "Scores -> "
            f"BM25: {result['bm25_score']}, "
            f"Semantic: {result['semantic_score']}, "
            f"Phrase: {result['phrase_score']}, "
            f"Metadata: {result['metadata_score']}"
        )


if __name__ == "__main__":
    engine = HybridSearchEngine(
        processed_file="processed.json",
        index_dir="search_index",
        embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
    )

    if os.path.exists("search_index/embeddings.npy"):
        engine.load_index()
    else:
        engine.build_index(save=True)

    while True:
        query = input("\nSearch query, or 'exit': ").strip()

        if query.lower() in {"exit", "quit"}:
            break

        results = engine.search(query, top_k=10)
        print_results(results)
