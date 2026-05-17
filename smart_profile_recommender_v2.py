
"""
smart_profile_recommender_v2.py

Fixes from v1:
1) Better query handling:
   - removes useless words like "i", "want", "some", "thing"
   - expands domain terms:
        image processing -> computer vision, opencv, image-processing, image-segmentation, object-detection
   - search results must match the query meaning, not only the user profile

2) Better personalized search:
   - query relevance is mandatory in search mode
   - profile only re-ranks query-matching candidates
   - avoids unrelated results such as networking / WhatsApp repos for "image processing"

3) Still supports:
   - profile-only recommendations before search
   - query + profile personalized search after search

Put this file next to:
- processed.json

Run:
    python smart_profile_recommender_v2.py
"""

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ============================================================
# Smart profile questions
# ============================================================

PROJECT_TYPE_OPTIONS = [
    {
        "label": "Web Development",
        "value": "web_dev",
        "topics": ["javascript", "typescript", "react", "nodejs", "html", "css", "frontend", "web"]
    },
    {
        "label": "AI / Machine Learning",
        "value": "ai_ml",
        "topics": [
            "machine-learning", "ai", "artificial-intelligence", "deep-learning",
            "nlp", "computer-vision", "image-processing", "opencv", "pytorch", "tensorflow"
        ]
    },
    {
        "label": "Data Science",
        "value": "data_science",
        "topics": ["data-science", "data-analysis", "analytics", "python", "pandas", "jupyter", "visualization"]
    },
    {
        "label": "Database / Backend",
        "value": "database_backend",
        "topics": ["database", "backend", "api", "postgresql", "sql", "server", "go", "nodejs"]
    },
    {
        "label": "Browser Extension",
        "value": "browser_extension",
        "topics": ["chrome", "firefox", "chrome-extension", "webextension", "browser", "extension"]
    },
    {
        "label": "Game Development",
        "value": "game_dev",
        "topics": ["game", "games", "game-development", "engine", "multiplayer", "opengl"]
    },
    {
        "label": "CLI / Developer Tools",
        "value": "cli_tools",
        "topics": ["cli", "command-line", "developer-tools", "tool", "automation", "terminal"]
    },
    {
        "label": "Project Management / Productivity",
        "value": "productivity",
        "topics": ["project-management", "productivity", "time-tracker", "timetracking", "scheduling"]
    },
    {
        "label": "Security",
        "value": "security",
        "topics": ["security", "cybersecurity", "malware", "vulnerability", "analysis"]
    },
]

GOAL_OPTIONS = [
    {
        "label": "Learn from the project",
        "value": "learning",
        "signals": ["learn", "learning", "tutorial", "guide", "course", "example", "examples", "getting-started"]
    },
    {
        "label": "Contribute to open source",
        "value": "contribution",
        "signals": ["contribute", "contributing", "contribution", "issue", "issues", "pull-request", "community", "good-first-issue"]
    },
    {
        "label": "Use it in my own project",
        "value": "use",
        "signals": ["install", "usage", "api", "documentation", "package", "npm", "pip", "library"]
    },
    {
        "label": "Find production-ready tools",
        "value": "production",
        "signals": ["production", "stable", "scalable", "deploy", "deployment", "docker", "kubernetes"]
    },
    {
        "label": "Build a portfolio project",
        "value": "portfolio",
        "signals": ["starter", "template", "clone", "app", "example", "demo", "project"]
    },
]

LEVEL_OPTIONS = [
    {
        "label": "Beginner",
        "value": "beginner",
        "signals": ["beginner", "tutorial", "simple", "starter", "intro", "example", "examples", "guide"]
    },
    {
        "label": "Intermediate",
        "value": "intermediate",
        "signals": ["framework", "api", "plugin", "integration", "module", "package"]
    },
    {
        "label": "Advanced",
        "value": "advanced",
        "signals": ["advanced", "distributed", "scalable", "engine", "compiler", "kubernetes", "performance", "optimized"]
    },
]

REPO_KIND_OPTIONS = [
    {
        "label": "Tutorial / educational repo",
        "value": "tutorial",
        "signals": ["tutorial", "guide", "course", "learn", "learning", "example", "examples"]
    },
    {
        "label": "Ready-to-use library or tool",
        "value": "library_tool",
        "signals": ["library", "tool", "cli", "package", "npm", "pip", "install", "usage"]
    },
    {
        "label": "Full application",
        "value": "full_app",
        "signals": ["app", "application", "platform", "dashboard", "server", "client"]
    },
    {
        "label": "Framework / infrastructure project",
        "value": "framework_infra",
        "signals": ["framework", "infrastructure", "engine", "scalable", "docker", "kubernetes"]
    },
    {
        "label": "Research / dataset / benchmark",
        "value": "research",
        "signals": ["research", "paper", "dataset", "benchmark", "model", "experiment"]
    },
]

COMPLEXITY_OPTIONS = [
    {"label": "Small and easy to understand", "value": "small"},
    {"label": "Medium-sized with real features", "value": "medium"},
    {"label": "Large real-world project", "value": "large"},
    {"label": "I do not care", "value": "any"},
]


# ============================================================
# Query cleaning and expansion
# ============================================================

QUERY_STOPWORDS = {
    "i", "me", "my", "we", "you", "your", "want", "wanna", "need", "needs",
    "some", "thing", "something", "anything", "for", "to", "a", "an", "the",
    "with", "about", "of", "in", "on", "and", "or", "please", "give", "get",
    "find", "show", "repo", "repos", "repository", "repositories", "project",
    "projects", "good", "best", "using", "use", "used"
}

QUERY_EXPANSIONS = {
    # image processing / CV
    "image": ["image", "images", "vision", "computer-vision", "opencv", "cv", "pillow"],
    "processing": ["processing", "image-processing", "computer-vision", "opencv"],
    "image-processing": ["image-processing", "computer-vision", "opencv", "vision"],
    "vision": ["vision", "computer-vision", "opencv", "image-processing"],
    "cv": ["cv", "computer-vision", "opencv", "image-processing"],
    "opencv": ["opencv", "computer-vision", "image-processing"],

    # common CV tasks
    "detection": ["detection", "object-detection", "yolo", "computer-vision"],
    "segmentation": ["segmentation", "image-segmentation", "computer-vision"],
    "classification": ["classification", "image-classification", "computer-vision"],
    "ocr": ["ocr", "text-recognition", "computer-vision"],

    # AI / ML
    "ai": ["ai", "artificial-intelligence", "machine-learning", "deep-learning"],
    "ml": ["ml", "machine-learning"],
    "machine": ["machine-learning"],
    "learning": ["machine-learning", "deep-learning"],
    "deep": ["deep-learning"],
    "pytorch": ["pytorch", "torch", "deep-learning"],
    "tensorflow": ["tensorflow", "keras", "deep-learning"],
}


def normalize_text(text: Optional[Any]) -> str:
    return "" if text is None else str(text).strip().lower()


def simple_tokenize(text: str) -> List[str]:
    text = normalize_text(text)
    text = re.sub(r"[^\w\s+#-]", " ", text)
    return [t for t in text.split() if len(t) > 1]


def clean_query_terms(query: str) -> List[str]:
    raw_terms = simple_tokenize(query)

    cleaned = []
    for term in raw_terms:
        term = term.strip().lower()
        if term in QUERY_STOPWORDS:
            continue
        cleaned.append(term)

    # Detect phrase "image processing"
    query_l = normalize_text(query)
    if "image processing" in query_l:
        cleaned.append("image-processing")
        cleaned.append("computer-vision")
        cleaned.append("opencv")

    # Expand important domain terms
    expanded = []
    for term in cleaned:
        expanded.append(term)
        expanded.extend(QUERY_EXPANSIONS.get(term, []))

    # Deduplicate but preserve order
    seen = set()
    result = []
    for term in expanded:
        term = term.lower()
        if term not in seen and term not in QUERY_STOPWORDS:
            seen.add(term)
            result.append(term)

    return result


# ============================================================
# User Profile
# ============================================================

@dataclass
class UserProfile:
    project_type: Optional[str] = None
    language: Optional[str] = None
    goal: Optional[str] = None
    level: Optional[str] = None
    repo_kind: Optional[str] = None
    complexity: Optional[str] = None
    top_k: int = 5
    topics: List[str] = field(default_factory=list)

    def expand_topics_from_project_type(self) -> None:
        if not self.project_type:
            return

        for option in PROJECT_TYPE_OPTIONS:
            if option["value"] == self.project_type:
                self.topics = list(dict.fromkeys(self.topics + option["topics"]))
                return

    def to_profile_query(self) -> str:
        parts = []
        if self.language:
            parts.append(self.language)
        parts.extend(self.topics)
        for value in [self.goal, self.level, self.repo_kind, self.complexity]:
            if value:
                parts.append(value)
        return " ".join(parts).lower()


# ============================================================
# Website options
# ============================================================

class DatasetOptionsBuilder:
    def __init__(self, data_path: str = "processed.json"):
        self.docs = self._load_docs(data_path)

    def _load_docs(self, path: str) -> List[Dict[str, Any]]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def build_language_options(self, top_n: int = 12) -> List[Dict[str, Any]]:
        counts = Counter()
        for doc in self.docs:
            lang = doc.get("language")
            if lang:
                counts[str(lang).strip()] += 1
        return [{"label": lang, "value": lang, "count": count} for lang, count in counts.most_common(top_n)]

    def save_website_options(self, output_path: str = "smart_profile_options.json") -> Dict[str, Any]:
        options = {
            "project_types": PROJECT_TYPE_OPTIONS,
            "languages": self.build_language_options(),
            "goals": GOAL_OPTIONS,
            "levels": LEVEL_OPTIONS,
            "repo_kinds": REPO_KIND_OPTIONS,
            "complexities": COMPLEXITY_OPTIONS,
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(options, f, indent=2, ensure_ascii=False)
        return options


# ============================================================
# Recommender
# ============================================================

class SmartProfileRecommender:
    def __init__(self, data_path: str = "processed.json"):
        self.docs = self._load_docs(data_path)
        self.N = len(self.docs)
        self.doc_freq = Counter()
        self.avg_doc_len = 0.0
        self._build_statistics()

    def _load_docs(self, path: str) -> List[Dict[str, Any]]:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _doc_tokens(self, doc: Dict[str, Any]) -> List[str]:
        return [normalize_text(t) for t in doc.get("tokens", []) if t]

    def _doc_terms(self, doc: Dict[str, Any]) -> set:
        terms = set(self._doc_tokens(doc))
        terms.update(normalize_text(t).replace(" ", "-") for t in doc.get("topics", []) or [])
        terms.add(normalize_text(doc.get("language")))
        terms.update(simple_tokenize(doc.get("title", "")))
        terms.update(simple_tokenize(doc.get("description", "")))
        return {t for t in terms if t}

    def _doc_text_blob(self, doc: Dict[str, Any]) -> str:
        return " ".join([
            normalize_text(doc.get("title")),
            normalize_text(doc.get("description")),
            " ".join(self._doc_tokens(doc)),
            " ".join([normalize_text(t) for t in doc.get("topics", []) or []]),
            normalize_text(doc.get("language")),
        ])

    def _build_statistics(self) -> None:
        total_len = 0
        for doc in self.docs:
            tokens = self._doc_tokens(doc)
            total_len += len(tokens)
            for token in set(tokens):
                self.doc_freq[token] += 1
        self.avg_doc_len = total_len / self.N if self.N else 0.0

    # -----------------------------
    # Scores
    # -----------------------------

    def query_relevance_score(self, query: str, doc: Dict[str, Any]) -> float:
        query_terms = clean_query_terms(query)
        if not query_terms:
            return 0.0

        doc_tokens = self._doc_tokens(doc)
        doc_terms = self._doc_terms(doc)

        if not doc_tokens and not doc_terms:
            return 0.0

        token_counts = Counter(doc_tokens)
        doc_len = len(doc_tokens) or 1

        # BM25 over processed tokens
        k1 = 1.5
        b = 0.75
        bm25 = 0.0

        for term in query_terms:
            if term not in token_counts:
                continue

            df = self.doc_freq.get(term, 0)
            idf = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
            tf = token_counts[term]
            denominator = tf + k1 * (1 - b + b * (doc_len / max(self.avg_doc_len, 1)))
            bm25 += idf * ((tf * (k1 + 1)) / denominator)

        bm25_norm = min(bm25 / 10.0, 1.0)

        # Metadata / topic direct match
        matched_terms = [term for term in query_terms if term in doc_terms]
        coverage = len(matched_terms) / max(len(query_terms), 1)

        # Strong phrase/domain match boosts
        domain_boost = 0.0
        important_cv_terms = {"image-processing", "computer-vision", "opencv", "vision", "cv", "object-detection", "image-segmentation"}
        if any(term in query_terms for term in important_cv_terms):
            if doc_terms.intersection(important_cv_terms):
                domain_boost = 0.4

        return min((0.55 * bm25_norm) + (0.35 * coverage) + domain_boost, 1.0)

    def has_query_match(self, query: str, doc: Dict[str, Any]) -> bool:
        """
        Search mode must return repos that actually match the query meaning.
        Profile match alone is not enough.
        """
        query_terms = set(clean_query_terms(query))
        doc_terms = self._doc_terms(doc)

        if not query_terms:
            return True

        # Direct expanded query match
        if query_terms.intersection(doc_terms):
            return True

        # Extra protection for image processing queries:
        # Require CV-related terms, not just "ai".
        q = normalize_text(query)
        if "image" in q or "vision" in q or "opencv" in q:
            cv_terms = {"image-processing", "computer-vision", "opencv", "vision", "cv", "object-detection", "image-segmentation", "image-classification"}
            return bool(doc_terms.intersection(cv_terms))

        return False

    def project_type_score(self, profile: UserProfile, doc: Dict[str, Any]) -> float:
        if not profile.topics:
            return 0.0
        wanted = {normalize_text(t).replace(" ", "-") for t in profile.topics}
        doc_terms = self._doc_terms(doc)
        matched = wanted.intersection(doc_terms)
        return min(len(matched) / max(len(wanted), 1), 1.0)

    def language_score(self, profile: UserProfile, doc: Dict[str, Any]) -> float:
        if not profile.language:
            return 0.0
        wanted = normalize_text(profile.language)
        main_lang = normalize_text(doc.get("language"))
        if wanted == main_lang:
            return 1.0
        other_langs = {normalize_text(lang) for lang in (doc.get("languages", {}) or {}).keys()}
        return 0.7 if wanted in other_langs else 0.0

    def signal_score(self, selected_value: Optional[str], options: List[Dict[str, Any]], doc: Dict[str, Any]) -> float:
        if not selected_value:
            return 0.0
        selected_option = next((o for o in options if o["value"] == selected_value), None)
        if not selected_option:
            return 0.0
        signals = selected_option.get("signals", [])
        if not signals:
            return 0.0

        doc_terms = self._doc_terms(doc)
        text_blob = self._doc_text_blob(doc)
        matched = 0
        for signal in signals:
            s = normalize_text(signal).replace(" ", "-")
            if s in doc_terms or s in text_blob:
                matched += 1
        return min(matched / max(len(signals), 1), 1.0)

    def complexity_score(self, profile: UserProfile, doc: Dict[str, Any]) -> float:
        if not profile.complexity or profile.complexity == "any":
            return 0.0

        readme_len = len(normalize_text(doc.get("readme")))
        topic_count = len(doc.get("topics", []) or [])
        language_count = len((doc.get("languages", {}) or {}).keys())

        complexity_points = 0
        if readme_len > 4000:
            complexity_points += 1
        if topic_count > 8:
            complexity_points += 1
        if language_count > 3:
            complexity_points += 1

        actual = "small" if complexity_points <= 1 else "medium" if complexity_points == 2 else "large"
        return 1.0 if actual == profile.complexity else 0.0

    def profile_keyword_score(self, profile: UserProfile, doc: Dict[str, Any]) -> float:
        terms = simple_tokenize(profile.to_profile_query())
        terms = [t for t in terms if t not in QUERY_STOPWORDS]
        if not terms:
            return 0.0
        doc_terms = self._doc_terms(doc)
        matched = sum(1 for t in terms if t in doc_terms)
        return matched / len(terms)

    # -----------------------------
    # Recommendation modes
    # -----------------------------

    def recommend_for_profile(self, profile: UserProfile) -> List[Dict[str, Any]]:
        profile.expand_topics_from_project_type()
        results = []

        for doc_id, doc in enumerate(self.docs):
            scores = {
                "project_type": self.project_type_score(profile, doc),
                "language": self.language_score(profile, doc),
                "goal": self.signal_score(profile.goal, GOAL_OPTIONS, doc),
                "level": self.signal_score(profile.level, LEVEL_OPTIONS, doc),
                "repo_kind": self.signal_score(profile.repo_kind, REPO_KIND_OPTIONS, doc),
                "complexity": self.complexity_score(profile, doc),
                "profile_keyword": self.profile_keyword_score(profile, doc),
            }

            final_score = (
                0.25 * scores["project_type"] +
                0.20 * scores["language"] +
                0.20 * scores["goal"] +
                0.15 * scores["level"] +
                0.10 * scores["repo_kind"] +
                0.05 * scores["complexity"] +
                0.05 * scores["profile_keyword"]
            )

            if final_score <= 0:
                continue

            results.append(self._format_result(
                doc_id, doc, final_score, scores,
                self._explain(profile, doc, scores, query=None),
                "profile_recommendation"
            ))

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:profile.top_k]

    def search_with_profile(self, query: str, profile: UserProfile) -> List[Dict[str, Any]]:
        profile.expand_topics_from_project_type()
        results = []

        clean_terms = clean_query_terms(query)
        print(f"\n[DEBUG] Cleaned/expanded query terms: {clean_terms}\n")

        for doc_id, doc in enumerate(self.docs):
            if not self.has_query_match(query, doc):
                continue

            scores = {
                "query_relevance": self.query_relevance_score(query, doc),
                "project_type": self.project_type_score(profile, doc),
                "language": self.language_score(profile, doc),
                "goal": self.signal_score(profile.goal, GOAL_OPTIONS, doc),
                "level": self.signal_score(profile.level, LEVEL_OPTIONS, doc),
                "repo_kind": self.signal_score(profile.repo_kind, REPO_KIND_OPTIONS, doc),
                "complexity": self.complexity_score(profile, doc),
            }

            # In search mode, query must dominate.
            final_score = (
                0.60 * scores["query_relevance"] +
                0.10 * scores["project_type"] +
                0.10 * scores["language"] +
                0.08 * scores["goal"] +
                0.05 * scores["level"] +
                0.04 * scores["repo_kind"] +
                0.03 * scores["complexity"]
            )

            if scores["query_relevance"] <= 0:
                continue

            results.append(self._format_result(
                doc_id, doc, final_score, scores,
                self._explain(profile, doc, scores, query=query),
                "personalized_search"
            ))

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:profile.top_k]

    # -----------------------------
    # Output
    # -----------------------------

    def _explain(self, profile: UserProfile, doc: Dict[str, Any], scores: Dict[str, float], query: Optional[str]) -> List[str]:
        reasons = []
        if query and scores.get("query_relevance", 0) > 0:
            reasons.append(f"Matches your search query meaning: '{query}'")
        if scores.get("project_type", 0) > 0:
            reasons.append("Matches your selected project type")
        if scores.get("language", 0) > 0:
            reasons.append(f"Matches your preferred language: {profile.language}")
        if scores.get("goal", 0) > 0:
            reasons.append(f"Matches your goal: {profile.goal}")
        if scores.get("level", 0) > 0:
            reasons.append(f"Suitable for your level: {profile.level}")
        if scores.get("repo_kind", 0) > 0:
            reasons.append(f"Matches your preferred repository kind: {profile.repo_kind}")
        if scores.get("complexity", 0) > 0:
            reasons.append(f"Matches your preferred complexity: {profile.complexity}")
        if not reasons:
            reasons.append("Recommended based on profile similarity")
        return reasons[:5]

    def _format_result(self, doc_id, doc, final_score, scores, why, mode):
        return {
            "mode": mode,
            "doc_id": doc_id,
            "title": doc.get("title", "Untitled"),
            "url": doc.get("url", ""),
            "description": doc.get("description", ""),
            "language": doc.get("language"),
            "topics": doc.get("topics", []),
            "stars": doc.get("stars", 0),
            "forks": doc.get("forks", 0),
            "score": round(final_score, 4),
            "score_breakdown": {key: round(value, 4) for key, value in scores.items()},
            "why_recommended": why,
        }


# ============================================================
# CLI
# ============================================================

def print_options(title: str, options: List[Dict[str, Any]], allow_skip: bool = True) -> None:
    print(f"\n{title}")
    if allow_skip:
        print("0. No preference / Skip")
    for i, option in enumerate(options, start=1):
        count = option.get("count")
        if count is not None:
            print(f"{i}. {option['label']} ({count} repos)")
        else:
            print(f"{i}. {option['label']}")


def choose_one(title: str, options: List[Dict[str, Any]], allow_skip: bool = True) -> Optional[str]:
    print_options(title, options, allow_skip)
    while True:
        raw = input("\nChoose one number: ").strip()
        if allow_skip and raw == "0":
            return None
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(options):
                return options[idx - 1]["value"]
        print("Invalid choice. Try again.")


def print_results(title: str, results: List[Dict[str, Any]]) -> None:
    print("\n====================================================")
    print(title)
    print("====================================================\n")
    if not results:
        print("No results found.\n")
        return
    for i, repo in enumerate(results, start=1):
        print(f"{i}. {repo['title']} | score={repo['score']}")
        print(f"   URL: {repo['url']}")
        print(f"   Language: {repo['language']} | Stars: {repo['stars']} | Forks: {repo['forks']}")
        print(f"   Topics: {', '.join(repo['topics'][:8])}")
        print("   Score breakdown:")
        for key, value in repo["score_breakdown"].items():
            print(f"   - {key}: {value}")
        print("   Why:")
        for reason in repo["why_recommended"]:
            print(f"   - {reason}")
        print()


def main() -> None:
    data_path = "processed.json"
    options_builder = DatasetOptionsBuilder(data_path)
    website_options = options_builder.save_website_options("smart_profile_options.json")

    print("\nSaved website options to: smart_profile_options.json")
    print("Now answer the profile questions.\n")

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
        top_k=5
    )

    recommender = SmartProfileRecommender(data_path)

    print("\n====================================================")
    print("Your selected profile")
    print("====================================================")
    print(f"project_type: {profile.project_type}")
    print(f"language: {profile.language}")
    print(f"goal: {profile.goal}")
    print(f"level: {profile.level}")
    print(f"repo_kind: {profile.repo_kind}")
    print(f"complexity: {profile.complexity}")

    profile_results = recommender.recommend_for_profile(profile)
    print_results("Recommended for you based on your profile", profile_results)

    query = input("\nNow type your search query, or press Enter to skip: ").strip()
    if query:
        search_results = recommender.search_with_profile(query, profile)
        print_results(f"Personalized search results for query: {query}", search_results)
    else:
        print("\nSearch skipped.\n")


if __name__ == "__main__":
    main()
