import json
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from collections import Counter

# =========================
# NLTK SETUP
# =========================
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

stop_words = set(stopwords.words("english"))

extra_stop_words = {
    "software", "open", "source", "project", "repository", "github",
    "readme", "license", "contributing", "contributors", "contributor",
    "stars", "fork", "forks", "watchers", "activity", "build",
    "framework", "library", "system", "application", "tool"
}

stop_words.update(extra_stop_words)

languages = {
    "python", "javascript", "typescript", "go", "rust", "java",
    "c", "c++", "c#", "php", "ruby", "swift", "kotlin",
    "sql", "bash", "shell", "html", "css", "dart", "scala"
}

stemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()


# =========================
# CLEAN TEXT
# =========================
def clean_text(text):
    if not text:
        return []

    text = text.lower()
    text = re.sub(r"[^\w\s+#]", " ", text)

    tokens = text.split()
    processed = []

    for token in tokens:

        if token in languages:
            processed.append(token)
            continue

        if len(token) <= 2:
            continue

        lemma = lemmatizer.lemmatize(token)
        stem = stemmer.stem(lemma)

        if lemma not in stop_words and stem not in stop_words:
            processed.append(stem)

    return processed


# =========================
# METADATA PROCESSING
# =========================
def process_metadata(item):
    meta_tokens = []

    # topics (VERY strong IR signal)
    meta_tokens += [t.lower() for t in item.get("topics", [])]

    # language (important signal)
    if item.get("language"):
        meta_tokens.append(item["language"].lower())

    # license
    if item.get("license"):
        meta_tokens.append(item["license"].lower())

    # contributors
    for c in item.get("contributors", []):
        meta_tokens += clean_text(c)

    # releases
    for r in item.get("releases", []):
        meta_tokens += clean_text(r)

    return meta_tokens


# =========================
# POPULARITY FEATURES → TOKENS
# =========================
def popularity_tokens(item):
    tokens = []

    stars = int(item.get("stars", 0))
    forks = int(item.get("forks", 0))

    # convert popularity into IR signals
    if stars > 10000:
        tokens += ["very_popular"] * 5
    elif stars > 1000:
        tokens += ["popular"] * 3
    elif stars > 100:
        tokens += ["trending"] * 2

    if forks > 5000:
        tokens += ["highly_forked"] * 3
    elif forks > 500:
        tokens += ["forked"] * 2

    return tokens


# =========================
# NORMALIZE NUMERIC FIELDS
# =========================
def normalize_item(item):
    item["stars"] = int(item.get("stars", 0))
    item["forks"] = int(item.get("forks", 0))
    item["watchers"] = int(item.get("watchers", 0))
    item["issues"] = int(item.get("issues", 0))
    return item


# =========================
# MAIN PIPELINE
# =========================
def process_data():

    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    processed = []

    for item in data:

        item = normalize_item(item)

        # =========================
        # TEXT PROCESSING
        # =========================
        title_tokens = clean_text(item.get("title", ""))
        desc_tokens = clean_text(item.get("description", ""))
        readme_tokens = clean_text(item.get("readme", ""))

        # =========================
        # METADATA + SIGNALS
        # =========================
        meta_tokens = process_metadata(item)

        # =========================
        # POPULARITY SIGNALS
        # =========================
        pop_tokens = popularity_tokens(item)

        # =========================
        # FINAL IR DOCUMENT
        # =========================
        all_tokens = (
            title_tokens * 4 +        # VERY IMPORTANT
            desc_tokens * 2 +         # medium importance
            readme_tokens +           # full content
            meta_tokens * 2 +         # structured signals
            pop_tokens                # ranking boost signals
        )

        processed.append({
            "url": item.get("url"),
            "title": item.get("title"),

            "stars": item["stars"],
            "forks": item["forks"],
            "watchers": item["watchers"],
            "issues": item["issues"],

            "language": item.get("language"),
            "topics": item.get("topics", []),

            # IR fields
            "tokens": all_tokens,
            "title_tokens": title_tokens,
            "meta_tokens": meta_tokens,
            "readme_tokens": readme_tokens,
            "desc_tokens": desc_tokens,
            "pop_tokens": pop_tokens,

            # useful for BM25 normalization later
            "doc_length": len(all_tokens)
        })

    with open("processed.json", "w", encoding="utf-8") as f:
        json.dump(processed, f, indent=4)

    print(f"Processed {len(processed)} repositories successfully.")


if __name__ == "__main__":
    process_data()