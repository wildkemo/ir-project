"""
Replace the entire Qdrant database content with processed.json only.

- Deletes every existing collection on the Qdrant server
- Creates a single collection (QDRANT_COLLECTION from .env)
- Upserts one point per repository; payload = full record from processed.json

Run from project root:
    python quadrant_updater.py
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://127.0.0.1:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "github_repos")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
VECTOR_SIZE = int(os.getenv("VECTOR_SIZE", "384"))
PROCESSED_FILE = os.getenv("PROCESSED_FILE", "processed.json")
BATCH_SIZE = int(os.getenv("QDRANT_BATCH_SIZE", "64"))


def build_document_text(repo: Dict[str, Any]) -> str:
    """Text used for the vector embedding (searchable summary of the repo)."""
    title = repo.get("title") or repo.get("name") or repo.get("repo") or ""
    full_name = repo.get("full_name") or ""
    description = repo.get("description") or ""
    language = repo.get("language") or ""
    license_name = repo.get("license") or ""
    topics = repo.get("topics") or []
    topics_text = ", ".join(str(t) for t in topics) if isinstance(topics, list) else str(topics)
    processed_text = repo.get("processed_text") or ""

    return " ".join([
        f"Repository: {full_name} {title}.",
        f"Description: {description}.",
        f"Programming language: {language}.",
        f"Topics: {topics_text}.",
        f"License: {license_name}.",
        f"Content: {processed_text}",
    ]).strip()


def sanitize_payload(repo: Dict[str, Any]) -> Dict[str, Any]:
    """Store the full processed.json record; ensure JSON-friendly values."""
    payload = dict(repo)
    payload["_source"] = "processed.json"
    return payload


def delete_all_collections(client: QdrantClient) -> List[str]:
    """Remove every collection so the DB only contains what we upload next."""
    removed: List[str] = []
    response = client.get_collections()
    for collection in response.collections:
        name = collection.name
        print(f"Deleting collection: {name}")
        client.delete_collection(name)
        removed.append(name)
    return removed


def load_processed_repos(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found. Run process.py after scraper.py first.")

    with open(path, "r", encoding="utf-8") as f:
        repos = json.load(f)

    if not isinstance(repos, list):
        raise ValueError(f"{path} must contain a JSON array of repositories.")

    return repos


def sync_processed_json_to_qdrant(
    processed_file: str = PROCESSED_FILE,
    collection_name: str = QDRANT_COLLECTION,
    qdrant_url: str = QDRANT_URL,
) -> int:
    print(f"Connecting to Qdrant at {qdrant_url}...")
    client = QdrantClient(url=qdrant_url)

    repos = load_processed_repos(processed_file)
    print(f"Loaded {len(repos)} repositories from {processed_file}.")

    removed = delete_all_collections(client)
    if removed:
        print(f"Removed {len(removed)} collection(s): {', '.join(removed)}")
    else:
        print("No existing collections found.")

    print(f"Creating collection '{collection_name}' (vector size {VECTOR_SIZE})...")
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.COSINE,
        ),
    )

    print(f"Loading embedding model: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    total_batches = (len(repos) + BATCH_SIZE - 1) // BATCH_SIZE
    for batch_index in range(0, len(repos), BATCH_SIZE):
        batch = repos[batch_index : batch_index + BATCH_SIZE]
        batch_num = batch_index // BATCH_SIZE + 1
        print(f"Embedding & uploading batch {batch_num}/{total_batches} ({len(batch)} repos)...")

        texts = [build_document_text(repo) for repo in batch]
        embeddings = model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

        points = []
        for offset, (repo, vector) in enumerate(zip(batch, embeddings)):
            point_id = batch_index + offset
            points.append(
                models.PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=sanitize_payload(repo),
                )
            )

        client.upsert(collection_name=collection_name, points=points)

    info = client.get_collection(collection_name)
    points_count = info.points_count if hasattr(info, "points_count") else len(repos)
    print(
        f"Done. Collection '{collection_name}' now has {points_count} points "
        f"(source: {processed_file} only)."
    )
    return len(repos)


def main() -> None:
    sync_processed_json_to_qdrant()


if __name__ == "__main__":
    main()
