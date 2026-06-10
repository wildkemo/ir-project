from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np


# ============================================================
# Utilities
# ============================================================

_WORD_RE = re.compile(r"[a-zA-Z0-9_#+.\-]+")
_GITHUB_URL_RE = re.compile(r"https?://github\.com/([^/\s]+)/([^/\s#?]+)", re.I)

DEFAULT_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in",
    "into", "is", "it", "of", "on", "or", "that", "the", "this", "to", "with",
    "your", "you", "using", "use", "repo", "repository", "github", "project",
}


def normalize_text(value: Any) -> str:
 
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return " ".join(normalize_text(v) for v in value)
    if isinstance(value, dict):
        return " ".join(f"{k} {normalize_text(v)}" for k, v in value.items())
    text = str(value)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str, stopwords: Optional[set[str]] = None) -> List[str]:
    
    stopwords = stopwords if stopwords is not None else DEFAULT_STOPWORDS
    tokens = [m.group(0).lower().strip(".-_") for m in _WORD_RE.finditer(text)]
    return [t for t in tokens if t and t not in stopwords and len(t) > 1]


def min_max_normalize(values: np.ndarray) -> np.ndarray:
    
    if values.size == 0:
        return values
    v_min = float(np.min(values))
    v_max = float(np.max(values))
    if math.isclose(v_min, v_max):
        return np.zeros_like(values, dtype=np.float32)
    return ((values - v_min) / (v_max - v_min)).astype(np.float32)


def safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def dataset_fingerprint(docs: Sequence[Dict[str, Any]]) -> str:
    
    lightweight = []
    for doc in docs:
        lightweight.append(
            {
                "id": doc.get("id"),
                "full_name": doc.get("full_name"),
                "url": doc.get("url") or doc.get("html_url"),
                "title": doc.get("title") or doc.get("name"),
                "description": doc.get("description"),
                "stars": doc.get("stars") or doc.get("stargazers_count"),
                "updated_at": doc.get("updated_at"),
            }
        )
    payload = json.dumps(lightweight, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def is_github_repository(doc: Dict[str, Any]) -> bool:
    """Best-effort check for records that represent GitHub repositories."""
    url = normalize_text(doc.get("url") or doc.get("html_url") or doc.get("github_url"))
    full_name = normalize_text(doc.get("full_name"))
    owner = normalize_text(doc.get("owner"))
    name = normalize_text(doc.get("name") or doc.get("repo") or doc.get("title"))

    if "github.com" in url.lower():
        return True
    if full_name and "/" in full_name and not full_name.startswith("/"):
        return True
    if owner and name:
        return True
    return bool(name and (doc.get("description") or doc.get("readme") or doc.get("topics")))


def resolve_full_name(doc: Dict[str, Any]) -> str:
    """Resolve owner/repo when possible."""
    for key in ("full_name", "repo_full_name", "repository", "slug"):
        value = normalize_text(doc.get(key))
        if value and "/" in value:
            return value.strip("/")

    url = normalize_text(doc.get("url") or doc.get("html_url") or doc.get("github_url"))
    match = _GITHUB_URL_RE.search(url)
    if match:
        owner, repo = match.groups()
        return f"{owner}/{repo.removesuffix('.git')}"

    owner_value = doc.get("owner")
    if isinstance(owner_value, dict):
        owner = normalize_text(owner_value.get("login") or owner_value.get("name"))
    else:
        owner = normalize_text(owner_value)

    repo = normalize_text(doc.get("repo") or doc.get("name") or doc.get("title"))
    if owner and repo:
        return f"{owner}/{repo}"
    return repo or normalize_text(doc.get("title")) or "unknown/repository"


def repo_url(doc: Dict[str, Any]) -> str:
    url = normalize_text(doc.get("url") or doc.get("html_url") or doc.get("github_url"))
    if url:
        return url
    full_name = resolve_full_name(doc)
    if full_name and full_name != "unknown/repository":
        return f"https://github.com/{full_name}"
    return ""


# ============================================================
# BM25
# ============================================================

@dataclass
class BM25Index:
    """Small standalone BM25 index."""

    tokenized_docs: List[List[str]] = field(default_factory=list)
    idf: Dict[str, float] = field(default_factory=dict)
    doc_lengths: List[int] = field(default_factory=list)
    avgdl: float = 0.0
    k1: float = 1.5
    b: float = 0.75

    @classmethod
    def build(
        cls,
        texts: Sequence[str],
        *,
        k1: float = 1.5,
        b: float = 0.75,
        stopwords: Optional[set[str]] = None,
    ) -> "BM25Index":
        tokenized_docs = [tokenize(text, stopwords=stopwords) for text in texts]
        doc_lengths = [len(tokens) for tokens in tokenized_docs]
        avgdl = float(sum(doc_lengths) / max(len(doc_lengths), 1))

        df: Dict[str, int] = {}
        for tokens in tokenized_docs:
            for term in set(tokens):
                df[term] = df.get(term, 0) + 1

        n_docs = len(tokenized_docs)
        idf = {
            term: math.log(1.0 + ((n_docs - freq + 0.5) / (freq + 0.5)))
            for term, freq in df.items()
        }

        return cls(
            tokenized_docs=tokenized_docs,
            idf=idf,
            doc_lengths=doc_lengths,
            avgdl=avgdl,
            k1=k1,
            b=b,
        )

    def score(self, query: str) -> np.ndarray:
        query_terms = tokenize(query)
        scores = np.zeros(len(self.tokenized_docs), dtype=np.float32)
        if not query_terms or not self.tokenized_docs:
            return scores

        query_terms = list(dict.fromkeys(query_terms))

        for doc_idx, doc_tokens in enumerate(self.tokenized_docs):
            if not doc_tokens:
                continue
            term_counts: Dict[str, int] = {}
            for token in doc_tokens:
                term_counts[token] = term_counts.get(token, 0) + 1

            doc_len = self.doc_lengths[doc_idx]
            denom_norm = self.k1 * (1.0 - self.b + self.b * (doc_len / max(self.avgdl, 1e-9)))

            score = 0.0
            for term in query_terms:
                freq = term_counts.get(term, 0)
                if freq == 0:
                    continue
                idf = self.idf.get(term, 0.0)
                score += idf * ((freq * (self.k1 + 1.0)) / (freq + denom_norm))
            scores[doc_idx] = score
        return scores

    def to_json(self) -> Dict[str, Any]:
        return {
            "tokenized_docs": self.tokenized_docs,
            "idf": self.idf,
            "doc_lengths": self.doc_lengths,
            "avgdl": self.avgdl,
            "k1": self.k1,
            "b": self.b,
        }

    @classmethod
    def from_json(cls, payload: Dict[str, Any]) -> "BM25Index":
        return cls(
            tokenized_docs=payload["tokenized_docs"],
            idf={str(k): float(v) for k, v in payload["idf"].items()},
            doc_lengths=[int(v) for v in payload["doc_lengths"]],
            avgdl=float(payload["avgdl"]),
            k1=float(payload.get("k1", 1.5)),
            b=float(payload.get("b", 0.75)),
        )


# ============================================================
# Search engine
# ============================================================

class GitHubRepoSearchEngine:
    """Hybrid GitHub repository search engine."""

    def __init__(
        self,
        data_path: str = "processed.json",
        vector_db_path: str = "vector_db",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        bm25_weight: float = 0.45,
        semantic_weight: float = 0.45,
        popularity_weight: float = 0.10,
        rebuild: bool = False,
    ) -> None:
        self.data_path = Path(data_path)
        self.vector_db_path = Path(vector_db_path)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)

        self.model_name = model_name
        self.bm25_weight = bm25_weight
        self.semantic_weight = semantic_weight
        self.popularity_weight = popularity_weight

        self.embeddings_file = self.vector_db_path / "repo_embeddings.npy"
        self.metadata_file = self.vector_db_path / "repo_metadata.json"
        self.bm25_file = self.vector_db_path / "bm25_index.json"

        self.docs = self._load_docs(self.data_path)
        self.docs = [doc for doc in self.docs if is_github_repository(doc)]
        self.fingerprint = dataset_fingerprint(self.docs)

        self.model = self._load_embedding_model()
        self.repo_texts = [self._repo_text(doc) for doc in self.docs]
        self.bm25 = self._load_or_build_bm25(rebuild=rebuild)
        self.embeddings = self._load_or_build_embeddings(rebuild=rebuild)

    # ------------------------------
    # Loading and indexing
    # ------------------------------

    def _load_docs(self, data_path: Path) -> List[Dict[str, Any]]:
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")

        with data_path.open("r", encoding="utf-8") as f:
            payload = json.load(f)

        if isinstance(payload, list):
            docs = payload
        elif isinstance(payload, dict):
            for key in ("repositories", "repos", "items", "data", "documents", "docs"):
                if isinstance(payload.get(key), list):
                    docs = payload[key]
                    break
            else:
                raise ValueError(
                    "JSON file must be a list of repositories or a dict containing one of: "
                    "repositories, repos, items, data, documents, docs"
                )
        else:
            raise ValueError("Unsupported JSON format. Expected list or dict.")

        clean_docs = [doc for doc in docs if isinstance(doc, dict)]
        if not clean_docs:
            raise ValueError("No repository records found in the dataset.")
        return clean_docs

    def _load_embedding_model(self):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for semantic search.\n"
                "Install it with: pip install sentence-transformers numpy"
            ) from exc
        return SentenceTransformer(self.model_name)

    def _repo_text(self, doc: Dict[str, Any]) -> str:
        """Text used by both BM25 and embeddings."""
        title = normalize_text(doc.get("title") or doc.get("name") or doc.get("repo"))
        full_name = resolve_full_name(doc)
        description = normalize_text(doc.get("description"))
        language = normalize_text(doc.get("language"))
        topics = normalize_text(doc.get("topics"))
        license_name = normalize_text(doc.get("license") or doc.get("license_name"))
        readme = normalize_text(doc.get("readme") or doc.get("README") or doc.get("readme_text"))
        tokens = normalize_text(doc.get("tokens") or doc.get("keywords"))

        # Limit huge fields so embeddings stay fast while still retaining meaning.
        text = f"""
        Repository: {full_name}
        Title: {title}
        Description: {description}
        Language: {language}
        Topics: {topics}
        License: {license_name}
        README: {readme[:4000]}
        Tokens: {tokens[:2500]}
        """
        return re.sub(r"\s+", " ", text).strip()

    def _metadata_is_current(self) -> bool:
        if not self.metadata_file.exists():
            return False
        try:
            with self.metadata_file.open("r", encoding="utf-8") as f:
                metadata = json.load(f)
        except (OSError, json.JSONDecodeError):
            return False
        return (
            metadata.get("fingerprint") == self.fingerprint
            and metadata.get("doc_count") == len(self.docs)
            and metadata.get("model_name") == self.model_name
        )

    def _write_metadata(self) -> None:
        metadata = {
            "fingerprint": self.fingerprint,
            "doc_count": len(self.docs),
            "model_name": self.model_name,
            "data_path": str(self.data_path),
        }
        with self.metadata_file.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def _load_or_build_bm25(self, rebuild: bool = False) -> BM25Index:
        if not rebuild and self.bm25_file.exists() and self._metadata_is_current():
            try:
                with self.bm25_file.open("r", encoding="utf-8") as f:
                    return BM25Index.from_json(json.load(f))
            except (OSError, json.JSONDecodeError, KeyError, ValueError):
                pass

        bm25 = BM25Index.build(self.repo_texts)
        with self.bm25_file.open("w", encoding="utf-8") as f:
            json.dump(bm25.to_json(), f, ensure_ascii=False)
        self._write_metadata()
        return bm25

    def _load_or_build_embeddings(self, rebuild: bool = False) -> np.ndarray:
        if not rebuild and self.embeddings_file.exists() and self._metadata_is_current():
            embeddings = np.load(self.embeddings_file)
            if embeddings.shape[0] == len(self.docs):
                return embeddings.astype(np.float32)

        embeddings = self.model.encode(
            self.repo_texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype(np.float32)
        np.save(self.embeddings_file, embeddings)
        self._write_metadata()
        return embeddings

    # ------------------------------
    # Scoring
    # ------------------------------

    def _encode_query(self, query: str) -> np.ndarray:
        return self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0].astype(np.float32)

    def semantic_scores(self, query: str) -> np.ndarray:
        """
        Cosine similarity between the query embedding and repo embeddings.
        Since all vectors are normalized, dot product = cosine similarity.
        Returned values are normalized to [0, 1].
        """
        query_vector = self._encode_query(query)
        raw_cosine = np.dot(self.embeddings, query_vector)
        return ((raw_cosine + 1.0) / 2.0).astype(np.float32)

    def bm25_scores(self, query: str) -> np.ndarray:
        """BM25 lexical relevance normalized to [0, 1]."""
        raw = self.bm25.score(query)
        return min_max_normalize(raw)

    def popularity_scores(self) -> np.ndarray:
        """Small tie-breaker based on stars/forks."""
        popularity = []
        for doc in self.docs:
            stars = safe_int(doc.get("stars") or doc.get("stargazers_count"))
            forks = safe_int(doc.get("forks") or doc.get("forks_count"))
            popularity.append(math.log1p(stars) + 0.35 * math.log1p(forks))
        return min_max_normalize(np.array(popularity, dtype=np.float32))

    def _passes_filters(
        self,
        doc: Dict[str, Any],
        *,
        language: Optional[str] = None,
        topic: Optional[str] = None,
        license_name: Optional[str] = None,
        min_stars: Optional[int] = None,
    ) -> bool:
        if language and normalize_text(doc.get("language")).lower() != language.lower():
            return False

        if topic:
            wanted = topic.lower().replace(" ", "-")
            topics = {normalize_text(t).lower().replace(" ", "-") for t in doc.get("topics", []) or []}
            searchable = self._repo_text(doc).lower().replace(" ", "-")
            if wanted not in topics and wanted not in searchable:
                return False

        if license_name:
            current_license = normalize_text(doc.get("license") or doc.get("license_name")).lower()
            if license_name.lower() not in current_license:
                return False

        if min_stars is not None:
            stars = safe_int(doc.get("stars") or doc.get("stargazers_count"))
            if stars < min_stars:
                return False

        return True

    def _result_item(
        self,
        doc_idx: int,
        query: str,
        final_score: float,
        bm25_score: float,
        semantic_score: float,
        popularity_score: float,
    ) -> Dict[str, Any]:
        doc = self.docs[doc_idx]
        full_name = resolve_full_name(doc)
        return {
            "rank": None,
            "doc_id": doc_idx,
            "full_name": full_name,
            "title": normalize_text(doc.get("title") or doc.get("name") or full_name),
            "url": repo_url(doc),
            "description": normalize_text(doc.get("description")),
            "language": doc.get("language"),
            "topics": doc.get("topics", []) or [],
            "stars": safe_int(doc.get("stars") or doc.get("stargazers_count")),
            "forks": safe_int(doc.get("forks") or doc.get("forks_count")),
            "score": round(float(final_score), 6),
            "score_breakdown": {
                "bm25": round(float(bm25_score), 6),
                "semantic_cosine": round(float(semantic_score), 6),
                "popularity": round(float(popularity_score), 6),
                "weights": {
                    "bm25": self.bm25_weight,
                    "semantic": self.semantic_weight,
                    "popularity": self.popularity_weight,
                },
            },
            "why_recommended": self.explain_match(
                query=query,
                doc=doc,
                bm25_score=bm25_score,
                semantic_score=semantic_score,
                popularity_score=popularity_score,
            ),
        }

    # ------------------------------
    # Public API
    # ------------------------------

    def search(
        self,
        query: str,
        *,
        top_k: int = 10,
        language: Optional[str] = None,
        topic: Optional[str] = None,
        license_name: Optional[str] = None,
        min_stars: Optional[int] = None,
        candidate_pool: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return GitHub repositories for a user query.

        Final score:
            bm25_weight * BM25(query, repo_text)
          + semantic_weight * cosine(query_embedding, repo_embedding)
          + popularity_weight * popularity(stars, forks)
        """
        query = normalize_text(query)
        if not query:
            return []

        bm25 = self.bm25_scores(query)
        semantic = self.semantic_scores(query)
        popularity = self.popularity_scores()

        final = (
            self.bm25_weight * bm25
            + self.semantic_weight * semantic
            + self.popularity_weight * popularity
        )

        order = np.argsort(final)[::-1]
        if candidate_pool is not None:
            order = order[: max(candidate_pool, top_k)]

        results: List[Dict[str, Any]] = []
        for doc_idx in order:
            doc_idx = int(doc_idx)
            doc = self.docs[doc_idx]
            if not self._passes_filters(
                doc,
                language=language,
                topic=topic,
                license_name=license_name,
                min_stars=min_stars,
            ):
                continue

            # Avoid returning very weak semantic-only matches for unrelated queries.
            if bm25[doc_idx] <= 0.0 and semantic[doc_idx] < 0.52:
                continue

            item = self._result_item(
                doc_idx=doc_idx,
                query=query,
                final_score=float(final[doc_idx]),
                bm25_score=float(bm25[doc_idx]),
                semantic_score=float(semantic[doc_idx]),
                popularity_score=float(popularity[doc_idx]),
            )
            item["rank"] = len(results) + 1
            results.append(item)
            if len(results) >= top_k:
                break

        return results

    def explain_match(
        self,
        *,
        query: str,
        doc: Dict[str, Any],
        bm25_score: float,
        semantic_score: float,
        popularity_score: float,
    ) -> List[str]:
        reasons: List[str] = []
        repo_text = self._repo_text(doc).lower()
        query_terms = tokenize(query)
        matched_terms = [term for term in query_terms if term in repo_text]

        if bm25_score > 0 and matched_terms:
            reasons.append("BM25 matched query terms: " + ", ".join(matched_terms[:6]))
        elif bm25_score > 0:
            reasons.append("BM25 found lexical overlap with the repository text")

        if semantic_score >= 0.65:
            reasons.append("High semantic cosine similarity to the query meaning")
        elif semantic_score >= 0.55:
            reasons.append("Moderate semantic similarity to the query meaning")

        if popularity_score >= 0.70:
            reasons.append("Strong popularity signal from stars/forks")

        language = normalize_text(doc.get("language"))
        if language and language.lower() in {t.lower() for t in query_terms}:
            reasons.append(f"Language matches the query: {language}")

        if not reasons:
            reasons.append("Ranked by the combined BM25 + semantic cosine score")
        return reasons[:5]

    def find_repo_index(self, repo_identifier: str) -> Optional[int]:
        target = normalize_text(repo_identifier).lower()
        if not target:
            return None

        for idx, doc in enumerate(self.docs):
            candidates = {
                normalize_text(resolve_full_name(doc)).lower(),
                normalize_text(doc.get("full_name")).lower(),
                normalize_text(doc.get("name")).lower(),
                normalize_text(doc.get("title")).lower(),
                normalize_text(repo_url(doc)).lower(),
            }
            if target in candidates:
                return idx

        for idx, doc in enumerate(self.docs):
            haystack = " ".join(
                [
                    normalize_text(resolve_full_name(doc)),
                    normalize_text(doc.get("title")),
                    normalize_text(doc.get("name")),
                    normalize_text(repo_url(doc)),
                ]
            ).lower()
            if target in haystack:
                return idx
        return None

    def similar_repositories(
        self,
        repo_identifier: str,
        *,
        top_k: int = 10,
        same_language_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Find repositories similar to another repository using cosine similarity."""
        idx = self.find_repo_index(repo_identifier)
        if idx is None:
            raise ValueError(f"Repository not found: {repo_identifier}")

        target_doc = self.docs[idx]
        target_lang = normalize_text(target_doc.get("language")).lower()
        target_vector = self.embeddings[idx]
        similarities = np.dot(self.embeddings, target_vector).astype(np.float32)
        similarities[idx] = -1.0

        order = np.argsort(similarities)[::-1]
        results: List[Dict[str, Any]] = []
        for doc_idx in order:
            doc_idx = int(doc_idx)
            doc = self.docs[doc_idx]
            if same_language_only and normalize_text(doc.get("language")).lower() != target_lang:
                continue

            results.append(
                {
                    "rank": len(results) + 1,
                    "doc_id": doc_idx,
                    "full_name": resolve_full_name(doc),
                    "title": normalize_text(doc.get("title") or doc.get("name") or resolve_full_name(doc)),
                    "url": repo_url(doc),
                    "description": normalize_text(doc.get("description")),
                    "language": doc.get("language"),
                    "topics": doc.get("topics", []) or [],
                    "stars": safe_int(doc.get("stars") or doc.get("stargazers_count")),
                    "forks": safe_int(doc.get("forks") or doc.get("forks_count")),
                    "semantic_cosine": round(float(similarities[doc_idx]), 6),
                }
            )
            if len(results) >= top_k:
                break
        return results

    def rebuild_index(self) -> None:
        """Force-rebuild BM25 and vector index after scraping new data."""
        self.bm25 = self._load_or_build_bm25(rebuild=True)
        self.embeddings = self._load_or_build_embeddings(rebuild=True)


# Backwards-compatible name for older code that imported SemanticHybridRecommender.
SemanticHybridRecommender = GitHubRepoSearchEngine


# ============================================================
# CLI
# ============================================================

def print_results(results: Sequence[Dict[str, Any]]) -> None:
    if not results:
        print("No matching repositories found.")
        return

    for item in results:
        print(f"\n#{item['rank']} {item['full_name']}")
        print(f"URL: {item['url']}")
        print(f"Score: {item['score']}")
        print(
            "Breakdown: "
            f"BM25={item['score_breakdown']['bm25']}, "
            f"Semantic={item['score_breakdown']['semantic_cosine']}, "
            f"Popularity={item['score_breakdown']['popularity']}"
        )
        if item.get("language"):
            print(f"Language: {item['language']}")
        if item.get("description"):
            print(f"Description: {item['description']}")
        reasons = item.get("why_recommended") or []
        if reasons:
            print("Why: " + " | ".join(reasons))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hybrid GitHub repository search engine")
    parser.add_argument("--data", default="processed.json", help="Path to scraped repository JSON")
    parser.add_argument("--vector-db", default="vector_db", help="Path to local vector DB folder")
    parser.add_argument("--model", default="sentence-transformers/all-MiniLM-L6-v2", help="SentenceTransformer model")
    parser.add_argument("--query", "-q", required=True, help="Search query")
    parser.add_argument("--top-k", type=int, default=10, help="Number of results")
    parser.add_argument("--language", help="Filter by programming language")
    parser.add_argument("--topic", help="Filter by topic")
    parser.add_argument("--license", dest="license_name", help="Filter by license")
    parser.add_argument("--min-stars", type=int, help="Minimum stars")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild BM25 and vectors")
    parser.add_argument("--json", action="store_true", help="Print raw JSON results")
    parser.add_argument("--bm25-weight", type=float, default=0.45)
    parser.add_argument("--semantic-weight", type=float, default=0.45)
    parser.add_argument("--popularity-weight", type=float, default=0.10)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    engine = GitHubRepoSearchEngine(
        data_path=args.data,
        vector_db_path=args.vector_db,
        model_name=args.model,
        bm25_weight=args.bm25_weight,
        semantic_weight=args.semantic_weight,
        popularity_weight=args.popularity_weight,
        rebuild=args.rebuild,
    )

    results = engine.search(
        args.query,
        top_k=args.top_k,
        language=args.language,
        topic=args.topic,
        license_name=args.license_name,
        min_stars=args.min_stars,
    )

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_results(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
