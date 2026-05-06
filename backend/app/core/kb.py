"""Knowledge base compatibility facade.

The production implementation lives in ``app.services.rag_service`` and
``app.repositories.knowledge_repository``. This module preserves legacy imports
while routing all operations through ChromaDB-backed hybrid retrieval.
"""

from __future__ import annotations

from typing import List

from app.services.rag_service import add_texts_to_index, clear_kb, query_kb

__all__ = ["add_texts_to_index", "clear_kb", "query_kb"]


def build_index_from_texts(text_chunks: List[str]) -> None:
    """Build an index from raw text chunks.

    Args:
        text_chunks: Raw text chunks to index under the default compatibility
            user scope.
    """
    clear_kb()
    add_texts_to_index(
        [{"text": chunk, "source": f"manual | chunk {index + 1}"} for index, chunk in enumerate(text_chunks)]
    )
