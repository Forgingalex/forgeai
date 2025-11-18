"""Knowledge Base - TF-IDF based RAG system."""
import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple
from pathlib import Path

# KB directory relative to backend root
BACKEND_ROOT = Path(__file__).parent.parent.parent
KB_DIR = BACKEND_ROOT / "kb_data"
KB_TEXTS = KB_DIR / "texts.json"
KB_VECTORS = KB_DIR / "vectors.npy"
KB_META = KB_DIR / "meta.json"

# Ensure directory exists
KB_DIR.mkdir(parents=True, exist_ok=True)


def _load_texts():
    """Load stored texts from JSON."""
    if KB_TEXTS.exists():
        with open(KB_TEXTS, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save_texts(texts):
    """Save texts to JSON."""
    with open(KB_TEXTS, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=2)


def _load_meta():
    """Load metadata from JSON."""
    if KB_META.exists():
        with open(KB_META, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_meta(meta):
    """Save metadata to JSON."""
    with open(KB_META, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)


def _load_vectors():
    """Load TF-IDF vectors."""
    if KB_VECTORS.exists():
        return np.load(KB_VECTORS, allow_pickle=True)
    return None


def _save_vectors(vectors):
    """Save TF-IDF vectors."""
    np.save(KB_VECTORS, vectors, allow_pickle=True)


def build_index_from_texts(text_chunks: List[str]) -> None:
    """
    Rebuild the TF-IDF index from the provided list of text chunks.
    This overwrites previous index.
    """
    # save raw texts
    _save_texts(text_chunks)
    if len(text_chunks) == 0:
        _save_vectors(np.zeros((0, 0)))
        _save_meta({})
        return

    # build vectorizer
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    vectors = vectorizer.fit_transform(text_chunks).toarray()
    _save_vectors(vectors)
    # save vectorizer vocab + params via meta for potential debugging
    meta = {"n_texts": len(text_chunks)}
    _save_meta(meta)


def add_texts_to_index(new_text_chunks: List[dict]) -> None:
    """
    Add new chunks to the existing KB. Each new chunk should be dict:
    {"text": "...", "source": "filename page X"}.
    """
    existing = _load_texts()
    existing.extend(new_text_chunks)
    # store only the text for vectorizer
    texts_only = [t["text"] for t in existing]
    build_index_from_texts(texts_only)


def query_kb(query: str, top_k: int = 3) -> List[Tuple[float, dict]]:
    """
    Return top_k (score, metadata) results. Metadata is the stored dict for chunk.
    """
    texts = _load_texts()
    if not texts:
        return []

    # Build a TF-IDF on the stored texts (we re-fit each time for simplicity)
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    vectors = vectorizer.fit_transform([t["text"] for t in texts]).toarray()
    q_vec = vectorizer.transform([query]).toarray()

    sims = cosine_similarity(q_vec, vectors)[0]
    idxs = np.argsort(sims)[::-1][:top_k]
    results = []
    for i in idxs:
        results.append((float(sims[i]), texts[i]))
    return results


def clear_kb():
    """Remove KB files (for dev)."""
    for p in [KB_TEXTS, KB_VECTORS, KB_META]:
        if p.exists():
            p.unlink()

