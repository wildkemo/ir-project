import os
from ir_engine import HybridSearchEngine


engine = None


def load_engine():
    global engine

    if engine is not None:
        return engine

    engine = HybridSearchEngine(
        processed_file="processed.json",
        index_dir="search_index",
        embedding_model_name="sentence-transformers/all-MiniLM-L6-v2",
    )

    embeddings_path = os.path.join("search_index", "embeddings.npy")

    if os.path.exists(embeddings_path):
        engine.load_index()
    else:
        engine.build_index(save=True)

    return engine