
"""
semantic_hybrid_recommender.py

Hybrid Personalized Search:
BM25 / lexical relevance + User Profile + BERT-style embeddings semantic similarity

This file is an ADD-ON layer on top of:
- smart_profile_recommender_v2.py
- processed.json

Put this file in the same folder as:
- processed.json
- smart_profile_recommender_v2.py

Install dependencies:
    pip install sentence-transformers numpy

Run:
    python semantic_hybrid_recommender.py

First run may take time because it builds repo embeddings and saves:
- repo_embeddings.npy

What this adds:
- semantic_similarity(query, repo)
- query meaning matching, not just exact keyword matching
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError(
        "sentence-transformers is not installed.\n"
        "Run: pip install sentence-transformers numpy"
    )

# Import your current recommender code.
# Make sure smart_profile_recommender_v2.py is in the same folder.
from smart_profile_recommender_v2 import (
    UserProfile,
    DatasetOptionsBuilder,
    SmartProfileRecommender,
    PROJECT_TYPE_OPTIONS,
    GOAL_OPTIONS,
    LEVEL_OPTIONS,
    REPO_KIND_OPTIONS,
    COMPLEXITY_OPTIONS,
    choose_one,
    print_results,
)


class SemanticHybridRecommender:
    def __init__(
        self,
        data_path: str = "processed.json",
        model_name: str = "all-MiniLM-L6-v2",
        embeddings_path: str = "repo_embeddings.npy",
    ):
        self.data_path = data_path
        self.embeddings_path = embeddings_path

        with open(data_path, "r", encoding="utf-8") as f:
            self.docs = json.load(f)

        # Existing lexical/profile recommender
        self.base = SmartProfileRecommender(data_path)

        # BERT-style sentence embedding model
        self.model = SentenceTransformer(model_name)

        # Load or build repo embeddings
        self.repo_embeddings = self._load_or_build_embeddings()

    # ============================================================
    # Text representation for each repository
    # ============================================================

    def _normalize(self, value: Optional[Any]) -> str:
        if value is None:
            return ""
        return str(value).strip()

    def _repo_text(self, doc: Dict[str, Any]) -> str:
        """
        This is the text that represents a repo semantically.
        We combine title, description, language, topics, and readme/tokens.
        """

        title = self._normalize(doc.get("title"))
        description = self._normalize(doc.get("description"))
        language = self._normalize(doc.get("language"))
        topics = " ".join([self._normalize(t) for t in doc.get("topics", []) or []])

        # processed.json may or may not keep readme.
        readme = self._normalize(doc.get("readme"))

        # tokens are very useful if readme is missing.
        tokens = " ".join([self._normalize(t) for t in doc.get("tokens", []) or []])

        # Keep text not too huge for faster embedding.
        # Important fields first.
        text = f"""
        Title: {title}
        Description: {description}
        Language: {language}
        Topics: {topics}
        README: {readme[:3000]}
        Tokens: {tokens[:2000]}
        """

        return re.sub(r"\s+", " ", text).strip()

    def _profile_text(self, profile: UserProfile) -> str:
        """
        Converts the selected user profile into a natural language sentence.
        This lets embeddings understand the user's long-term preferences.
        """
        profile.expand_topics_from_project_type()

        parts = []

        if profile.project_type:
            parts.append(f"Project type: {profile.project_type}")

        if profile.language:
            parts.append(f"Preferred programming language: {profile.language}")

        if profile.goal:
            parts.append(f"User goal: {profile.goal}")

        if profile.level:
            parts.append(f"Skill level: {profile.level}")

        if profile.repo_kind:
            parts.append(f"Preferred repository kind: {profile.repo_kind}")

        if profile.complexity:
            parts.append(f"Preferred complexity: {profile.complexity}")

        if profile.topics:
            parts.append(f"Interested topics: {', '.join(profile.topics)}")

        return ". ".join(parts)

    # ============================================================
    # Embeddings
    # ============================================================

    def _load_or_build_embeddings(self) -> np.ndarray:
        """
        Loads cached embeddings if available.
        Otherwise, builds embeddings for all repositories and saves them.
        """
        if Path(self.embeddings_path).exists():
            embeddings = np.load(self.embeddings_path)

            if len(embeddings) == len(self.docs):
                print(f"[INFO] Loaded cached embeddings from {self.embeddings_path}")
                return embeddings

            print("[WARN] Embeddings cache size does not match dataset. Rebuilding...")

        print("[INFO] Building repository embeddings. This may take a while on first run...")

        repo_texts = [self._repo_text(doc) for doc in self.docs]

        embeddings = self.model.encode(
            repo_texts,
            batch_size=32,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        np.save(self.embeddings_path, embeddings)

        print(f"[INFO] Saved embeddings to {self.embeddings_path}")

        return embeddings

    def _encode_text(self, text: str) -> np.ndarray:
        return self.model.encode(
            [text],
            convert_to_numpy=True,
            normalize_embeddings=True,
        )[0]

    def semantic_scores(self, query_text: str) -> np.ndarray:
        """
        Cosine similarity.
        Because embeddings are normalized, dot product = cosine similarity.
        """
        query_embedding = self._encode_text(query_text)
        scores = np.dot(self.repo_embeddings, query_embedding)

        # Convert from roughly [-1, 1] into [0, 1]
        return (scores + 1.0) / 2.0

    # ============================================================
    # Hybrid Search
    # ============================================================

    def search_with_profile_and_semantics(
        self,
        query: str,
        profile: UserProfile,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Query + Profile + Semantic similarity.

        Final Score = 0.55 lexical + 0.30 semantic + 0.15 profile   

        Where:
        - lexical_query_score comes from the existing BM25-like logic
        - semantic_similarity comes from embeddings
        - profile_match comes from project type, language, goal, level, etc.
        """

        profile.expand_topics_from_project_type()

        profile_text = self._profile_text(profile)

        # Make query embedding richer by combining actual query + selected profile.
        semantic_query_text = f"""
        User search query: {query}
        User profile: {profile_text}
        """

        semantic_score_array = self.semantic_scores(semantic_query_text)

        results = []

        for doc_id, doc in enumerate(self.docs):
            # Existing lexical/query score from v2
            lexical_query_score = self.base.query_relevance_score(query, doc)

            # Existing profile-related scores from v2
            project_type = self.base.project_type_score(profile, doc)
            language = self.base.language_score(profile, doc)
            goal = self.base.signal_score(profile.goal, GOAL_OPTIONS, doc)
            level = self.base.signal_score(profile.level, LEVEL_OPTIONS, doc)
            repo_kind = self.base.signal_score(profile.repo_kind, REPO_KIND_OPTIONS, doc)
            complexity = self.base.complexity_score(profile, doc)

            profile_match = (
                0.30 * project_type +
                0.25 * language +
                0.20 * goal +
                0.10 * level +
                0.10 * repo_kind +
                0.05 * complexity
            )

            semantic = float(semantic_score_array[doc_id])

            # Important:
            # We do NOT require exact query matching anymore, because embeddings
            # can retrieve semantically related repos even without exact words.
            # But we still keep lexical score strong when exact terms exist.
            final_score = (
                0.55 * lexical_query_score +
                0.30 * semantic +
                0.15 * profile_match
            )

            # Filter extremely weak results.
            # If both lexical and profile are zero, require decent semantic score.
            if lexical_query_score == 0 and profile_match == 0 and semantic < 0.55:
                continue

            result = {
                "mode": "hybrid_semantic_search",
                "doc_id": doc_id,
                "title": doc.get("title", "Untitled"),
                "url": doc.get("url", ""),
                "description": doc.get("description", ""),
                "language": doc.get("language"),
                "topics": doc.get("topics", []),
                "stars": doc.get("stars", 0),
                "forks": doc.get("forks", 0),
                "score": round(final_score, 4),
                "score_breakdown": {
                    "lexical_query_score": round(lexical_query_score, 4),
                    "semantic_similarity": round(semantic, 4),
                    "profile_match": round(profile_match, 4),
                    "project_type": round(project_type, 4),
                    "language": round(language, 4),
                    "goal": round(goal, 4),
                    "level": round(level, 4),
                    "repo_kind": round(repo_kind, 4),
                    "complexity": round(complexity, 4),
                },
                "why_recommended": self._explain(
                    query=query,
                    profile=profile,
                    lexical_query_score=lexical_query_score,
                    semantic=semantic,
                    profile_match=profile_match,
                    doc=doc,
                )
            }

            results.append(result)

        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:top_k]

    def _explain(
        self,
        query: str,
        profile: UserProfile,
        lexical_query_score: float,
        semantic: float,
        profile_match: float,
        doc: Dict[str, Any],
    ) -> List[str]:
        reasons = []

        if lexical_query_score > 0:
            reasons.append("Matches exact query terms using BM25-style lexical search")

        if semantic >= 0.60:
            reasons.append("Semantically close to the meaning of your query/profile using embeddings")

        if profile_match > 0:
            reasons.append("Re-ranked based on your selected user profile")

        if profile.language and doc.get("language") == profile.language:
            reasons.append(f"Matches your preferred language: {profile.language}")

        if profile.project_type:
            reasons.append(f"Related to your selected project type: {profile.project_type}")

        if not reasons:
            reasons.append("Recommended by hybrid semantic ranking")

        return reasons[:5]


# ============================================================
# CLI
# ============================================================

def main() -> None:
    data_path = "processed.json"

    options_builder = DatasetOptionsBuilder(data_path)
    website_options = options_builder.save_website_options("smart_profile_options.json")

    print("\nSemantic Hybrid Recommender")
    print("This combines BM25/profile ranking with BERT-style embeddings.\n")

    project_type = choose_one("Q1) What type of project are you looking for?", website_options["project_types"], True)
    language = choose_one("Q2) Which programming language do you prefer?", website_options["languages"], True)
    goal = choose_one("Q3) What is your goal?", website_options["goals"], True)
    level = choose_one("Q4) What is your skill level?", website_options["levels"], True)
    repo_kind = choose_one("Q5) What kind of repository do you prefer?", website_options["repo_kinds"], True)
    complexity = choose_one("Q6) How complex should the project be?", website_options["complexities"], True)

    profile = UserProfile(
        project_type=project_type,
        language=language,
        goal=goal,
        level=level,
        repo_kind=repo_kind,
        complexity=complexity,
        top_k=10,
    )

    recommender = SemanticHybridRecommender(data_path)

    query = input("\nNow type your search query: ").strip()

    if not query:
        print("No query entered. Exiting.")
        return

    results = recommender.search_with_profile_and_semantics(
        query=query,
        profile=profile,
        top_k=10,
    )

    print_results(f"Hybrid semantic search results for query: {query}", results)


if __name__ == "__main__":
    main()
