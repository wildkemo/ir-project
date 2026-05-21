import json
import re
import math
from datetime import datetime, timezone

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# =========================
# NLTK SETUP
# =========================
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

stop_words = set(stopwords.words("english"))

extra_stop_words = {
    "github", "readme", "license", "contributing",
    "contributors", "contributor"
}

stop_words.update(extra_stop_words)

programming_languages = {
    "python", "javascript", "typescript", "go", "rust", "java",
    "c", "c++", "c#", "php", "ruby", "swift", "kotlin",
    "sql", "bash", "shell", "html", "css", "dart", "scala",
    "r", "perl", "lua", "haskell", "elixir", "clojure"
}

lemmatizer = WordNetLemmatizer()


# =========================
# TEXT CLEANING
# =========================
def clean_text(text):
    if not text:
        return []

    text = str(text).lower()

    # Keep useful programming symbols: c++, c#, .net, node.js
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s+#.]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = text.split()
    processed = []

    for token in tokens:
        token = token.strip()

        if not token:
            continue

        # Keep programming languages exactly
        if token in programming_languages:
            processed.append(token)
            continue

        if len(token) <= 2:
            continue

        if token in stop_words:
            continue

        lemma = lemmatizer.lemmatize(token)

        if lemma not in stop_words:
            processed.append(lemma)

    return processed


# =========================
# SAFE INTEGER
# =========================
def safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


# =========================
# DATE PARSING
# =========================
def parse_github_date(date_str):
    if not date_str:
        return None

    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        return None


# =========================
# NUMERIC NORMALIZATION
# =========================
def log_normalize(value):
    value = safe_int(value)
    return math.log1p(value)


# =========================
# POPULARITY SCORE
# =========================
def compute_popularity_score(item):
    stars = safe_int(item.get("stars", 0))
    forks = safe_int(item.get("forks", 0))
    watchers = safe_int(item.get("watchers", 0))

    return (
        0.60 * log_normalize(stars) +
        0.30 * log_normalize(forks) +
        0.10 * log_normalize(watchers)
    )


# =========================
# ACTIVITY SCORE
# =========================
def compute_activity_score(item):
    pushed_at = item.get("pushed_at") or item.get("updated_at")
    pushed_date = parse_github_date(pushed_at)

    if not pushed_date:
        return 0.0

    now = datetime.now(timezone.utc)
    days_since_push = (now - pushed_date).days

    if days_since_push <= 30:
        return 1.0
    elif days_since_push <= 90:
        return 0.8
    elif days_since_push <= 180:
        return 0.6
    elif days_since_push <= 365:
        return 0.4
    elif days_since_push <= 730:
        return 0.2
    else:
        return 0.1


# =========================
# QUALITY SCORE
# =========================
def compute_quality_score(item):
    score = 0.0

    if item.get("description"):
        score += 0.2

    if item.get("readme") or item.get("has_readme"):
        score += 0.3

    if item.get("license"):
        score += 0.2

    if item.get("topics"):
        score += 0.2

    if item.get("language") or item.get("languages"):
        score += 0.1

    return score


# =========================
# METADATA TOKENS
# =========================
def process_metadata(item):
    meta_tokens = []

    # Topics are very strong IR signals
    for topic in item.get("topics", []) or []:
        meta_tokens += clean_text(topic.replace("-", " "))

    # Main language
    if item.get("language"):
        meta_tokens.append(str(item["language"]).lower())

    # All detected languages
    languages = item.get("languages", {}) or {}

    if isinstance(languages, dict):
        for lang in languages.keys():
            meta_tokens.append(str(lang).lower())

    # License
    if item.get("license"):
        meta_tokens += clean_text(str(item.get("license")))

    # Owner/repo name
    if item.get("owner"):
        meta_tokens += clean_text(item.get("owner"))

    if item.get("repo"):
        meta_tokens += clean_text(item.get("repo"))

    if item.get("full_name"):
        meta_tokens += clean_text(item.get("full_name").replace("/", " "))

    return meta_tokens


# =========================
# POPULARITY TOKENS
# =========================
def popularity_tokens(item):
    tokens = []

    stars = safe_int(item.get("stars", 0))
    forks = safe_int(item.get("forks", 0))

    if stars > 50000:
        tokens += ["extremely_popular"] * 5
    elif stars > 10000:
        tokens += ["very_popular"] * 4
    elif stars > 1000:
        tokens += ["popular"] * 3
    elif stars > 100:
        tokens += ["trending"] * 2

    if forks > 10000:
        tokens += ["massively_forked"] * 4
    elif forks > 5000:
        tokens += ["highly_forked"] * 3
    elif forks > 500:
        tokens += ["forked"] * 2

    return tokens


# =========================
# NORMALIZE ITEM
# =========================
def normalize_item(item):
    item["stars"] = safe_int(item.get("stars", 0))
    item["forks"] = safe_int(item.get("forks", 0))
    item["watchers"] = safe_int(item.get("watchers", 0))

    # Support both old scraper and new API scraper
    item["issues"] = safe_int(
        item.get("issues", item.get("open_issues", 0))
    )

    item["open_issues"] = item["issues"]

    return item


# =========================
# MAIN PIPELINE
# =========================
def process_data(
    input_file="new_data.json",
    output_file="processed.json"
):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    processed = []

    for item in data:
        item = normalize_item(item)

        # Works with old and new schema
        title = (
            item.get("title")
            or item.get("name")
            or item.get("repo")
            or item.get("full_name")
            or ""
        )

        description = item.get("description", "")
        readme = item.get("readme", "")

        # =========================
        # FIELD TOKENS
        # =========================
        title_tokens = clean_text(title)
        desc_tokens = clean_text(description)
        readme_tokens = clean_text(readme)
        meta_tokens = process_metadata(item)
        pop_tokens = popularity_tokens(item)

        # =========================
        # WEIGHTED IR DOCUMENT
        # =========================
        all_tokens = (
            title_tokens * 5 +
            desc_tokens * 3 +
            meta_tokens * 3 +
            readme_tokens +
            pop_tokens
        )

        # =========================
        # NUMERIC FEATURES
        # =========================
        popularity_score = compute_popularity_score(item)
        activity_score = compute_activity_score(item)
        quality_score = compute_quality_score(item)

        processed.append({
            "id": item.get("id"),
            "url": item.get("url"),
            "owner": item.get("owner"),
            "repo": item.get("repo"),
            "name": item.get("name") or title,
            "title": title,
            "full_name": item.get("full_name"),

            "description": description,
            "language": item.get("language"),
            "languages": item.get("languages", {}),
            "topics": item.get("topics", []),
            "license": item.get("license"),

            "stars": item["stars"],
            "forks": item["forks"],
            "watchers": item["watchers"],
            "issues": item["issues"],
            "open_issues": item["open_issues"],

            "created_at": item.get("created_at"),
            "updated_at": item.get("updated_at"),
            "pushed_at": item.get("pushed_at"),

            "has_readme": bool(readme),
            "readme_length": len(readme),

            # IR fields
            "tokens": all_tokens,
            "title_tokens": title_tokens,
            "desc_tokens": desc_tokens,
            "readme_tokens": readme_tokens,
            "meta_tokens": meta_tokens,
            "pop_tokens": pop_tokens,
            "doc_length": len(all_tokens),

            # Ranking features
            "popularity_score": popularity_score,
            "activity_score": activity_score,
            "quality_score": quality_score,

            # Ready-to-index text
            "processed_text": " ".join(all_tokens)
        })

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=4, ensure_ascii=False)

    print(f"Processed {len(processed)} repositories successfully.")
    print(f"Saved to {output_file}")


if __name__ == "__main__":
    process_data()