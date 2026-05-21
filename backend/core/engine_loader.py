"""
Search & similar-repo endpoints use semantic_hybrid_recommender (BM25 + embeddings).
Profile quiz recommendations use smart_profile_recommender_v2 via profile_loader.
"""

from backend.core.semantic_loader import load_semantic_hybrid

# Backward-compatible alias for repos/search/recommend routes
def load_engine():
    return load_semantic_hybrid()
