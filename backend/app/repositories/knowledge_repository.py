"""Vector and keyword persistence for the ForgeAI knowledge base."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class KnowledgeChunk:
    """A text chunk ready to be indexed."""

    text: str
    source: str
    user_id: int = 0
    workspace_id: Optional[int] = None
    file_id: Optional[int] = None
    page_number: Optional[int] = None
    chunk_index: int = 0


@dataclass(frozen=True)
class KnowledgeSearchResult:
    """A ranked knowledge-base match."""

    text: str
    source: str
    score: float
    semantic_score: float
    keyword_score: float
    metadata: Dict[str, Any]


class ChromaKnowledgeRepository:
    """Repository for hybrid retrieval backed by ChromaDB.

    ChromaDB stores durable semantic vectors. A lightweight TF-IDF pass is
    computed over candidate workspace documents at query time to blend lexical
    precision with semantic recall.
    """

    def __init__(
        self,
        collection_name: str = settings.CHROMA_COLLECTION,
        semantic_weight: float = settings.HYBRID_SEMANTIC_WEIGHT,
    ) -> None:
        self.collection_name = collection_name
        self.semantic_weight = semantic_weight
        self._client: Any = None
        self._collection: Any = None
        self._embedding_model: Any = None

    @property
    def collection(self) -> Any:
        """Return the configured Chroma collection, creating it lazily."""
        if self._collection is None:
            self._collection = self._get_client().get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def add_chunks(self, chunks: Sequence[KnowledgeChunk]) -> int:
        """Upsert chunks into the vector store.

        Args:
            chunks: Text chunks with source and ownership metadata.

        Returns:
            Number of chunks written.
        """
        valid_chunks = [chunk for chunk in chunks if chunk.text.strip()]
        if not valid_chunks:
            return 0

        documents = [chunk.text for chunk in valid_chunks]
        embeddings = self._embed(documents)
        ids = [self._chunk_id(chunk) for chunk in valid_chunks]
        metadatas = [self._metadata_for(chunk) for chunk in valid_chunks]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )
        logger.info("indexed_knowledge_chunks", extra={"chunk_count": len(valid_chunks)})
        return len(valid_chunks)

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        user_id: int = 0,
        workspace_id: Optional[int] = None,
    ) -> List[KnowledgeSearchResult]:
        """Search with semantic and keyword scoring.

        Args:
            query: User question or search text.
            top_k: Maximum number of ranked chunks to return.
            user_id: Owner scope for retrieval.
            workspace_id: Optional workspace scope.

        Returns:
            Ranked knowledge search results.
        """
        if not query.strip():
            return []

        semantic_results = self._semantic_search(query, max(top_k * 4, 12), user_id, workspace_id)
        keyword_results = self._keyword_search(query, max(top_k * 4, 12), user_id, workspace_id)
        combined = self._merge_results(semantic_results, keyword_results)
        return sorted(combined.values(), key=lambda item: item.score, reverse=True)[:top_k]

    def clear(self) -> None:
        """Delete and recreate the backing collection."""
        client = self._get_client()
        try:
            client.delete_collection(self.collection_name)
        except Exception:
            logger.debug("knowledge_collection_missing_on_clear")
        self._collection = client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def _get_client(self) -> Any:
        if self._client is not None:
            return self._client

        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError(
                "ChromaDB is not installed. Install backend requirements before indexing."
            ) from exc

        if settings.CHROMA_MODE == "http":
            self._client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        else:
            self._client = chromadb.PersistentClient(path=str(settings.CHROMA_PERSIST_DIR))
        return self._client

    def _get_embedding_model(self) -> Any:
        if self._embedding_model is not None:
            return self._embedding_model

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is not installed. Install backend requirements before indexing."
            ) from exc

        self._embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        return self._embedding_model

    def _embed(self, texts: Sequence[str]) -> List[List[float]]:
        model = self._get_embedding_model()
        vectors = model.encode(
            list(texts),
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.astype(float).tolist()

    def _semantic_search(
        self,
        query: str,
        limit: int,
        user_id: int,
        workspace_id: Optional[int],
    ) -> List[KnowledgeSearchResult]:
        try:
            response = self.collection.query(
                query_embeddings=self._embed([query]),
                n_results=limit,
                where=self._where(user_id, workspace_id),
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            logger.warning("semantic_search_failed", extra={"error": str(exc)})
            return []

        ids = response.get("ids", [[]])[0]
        documents = response.get("documents", [[]])[0]
        metadatas = response.get("metadatas", [[]])[0]
        distances = response.get("distances", [[]])[0]
        results: List[KnowledgeSearchResult] = []

        for index, document in enumerate(documents):
            metadata = metadatas[index] or {}
            distance = float(distances[index]) if index < len(distances) else 1.0
            semantic_score = max(0.0, 1.0 - distance)
            metadata["_id"] = ids[index] if index < len(ids) else self._stable_id(document)
            results.append(
                KnowledgeSearchResult(
                    text=document,
                    source=str(metadata.get("source", "Unknown source")),
                    score=semantic_score,
                    semantic_score=semantic_score,
                    keyword_score=0.0,
                    metadata=metadata,
                )
            )
        return results

    def _keyword_search(
        self,
        query: str,
        limit: int,
        user_id: int,
        workspace_id: Optional[int],
    ) -> List[KnowledgeSearchResult]:
        try:
            response = self.collection.get(
                where=self._where(user_id, workspace_id),
                include=["documents", "metadatas"],
            )
        except Exception as exc:
            logger.warning("keyword_search_failed", extra={"error": str(exc)})
            return []

        documents = response.get("documents") or []
        metadatas = response.get("metadatas") or []
        ids = response.get("ids") or []
        if not documents:
            return []

        vectorizer = TfidfVectorizer(max_features=8000, ngram_range=(1, 2), stop_words="english")
        matrix = vectorizer.fit_transform(documents)
        query_vector = vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, matrix)[0]
        ranked_indexes = np.argsort(similarities)[::-1][:limit]

        results: List[KnowledgeSearchResult] = []
        for index in ranked_indexes:
            keyword_score = float(similarities[index])
            if keyword_score <= 0:
                continue
            metadata = dict(metadatas[index] or {})
            metadata["_id"] = ids[index] if index < len(ids) else self._stable_id(documents[index])
            results.append(
                KnowledgeSearchResult(
                    text=documents[index],
                    source=str(metadata.get("source", "Unknown source")),
                    score=keyword_score,
                    semantic_score=0.0,
                    keyword_score=keyword_score,
                    metadata=metadata,
                )
            )
        return results

    def _merge_results(
        self,
        semantic_results: Iterable[KnowledgeSearchResult],
        keyword_results: Iterable[KnowledgeSearchResult],
    ) -> Dict[str, KnowledgeSearchResult]:
        merged: Dict[str, KnowledgeSearchResult] = {}
        keyword_weight = 1.0 - self.semantic_weight

        for result in semantic_results:
            key = str(result.metadata.get("_id", self._stable_id(result.text)))
            merged[key] = KnowledgeSearchResult(
                text=result.text,
                source=result.source,
                score=(result.semantic_score * self.semantic_weight),
                semantic_score=result.semantic_score,
                keyword_score=0.0,
                metadata=result.metadata,
            )

        for result in keyword_results:
            key = str(result.metadata.get("_id", self._stable_id(result.text)))
            existing = merged.get(key)
            if existing:
                merged[key] = KnowledgeSearchResult(
                    text=existing.text,
                    source=existing.source,
                    score=existing.score + (result.keyword_score * keyword_weight),
                    semantic_score=existing.semantic_score,
                    keyword_score=result.keyword_score,
                    metadata=existing.metadata,
                )
            else:
                merged[key] = KnowledgeSearchResult(
                    text=result.text,
                    source=result.source,
                    score=result.keyword_score * keyword_weight,
                    semantic_score=0.0,
                    keyword_score=result.keyword_score,
                    metadata=result.metadata,
                )

        return merged

    def _metadata_for(self, chunk: KnowledgeChunk) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {
            "source": chunk.source,
            "user_id": chunk.user_id,
            "workspace_id": chunk.workspace_id or 0,
            "chunk_index": chunk.chunk_index,
        }
        if chunk.file_id is not None:
            metadata["file_id"] = chunk.file_id
        if chunk.page_number is not None:
            metadata["page_number"] = chunk.page_number
        return metadata

    def _where(self, user_id: int, workspace_id: Optional[int]) -> Dict[str, Any]:
        if workspace_id is None:
            return {"user_id": user_id}
        return {"$and": [{"user_id": user_id}, {"workspace_id": workspace_id}]}

    def _chunk_id(self, chunk: KnowledgeChunk) -> str:
        raw = "|".join(
            [
                str(chunk.user_id),
                str(chunk.workspace_id or 0),
                str(chunk.file_id or 0),
                chunk.source,
                str(chunk.chunk_index),
                chunk.text[:256],
            ]
        )
        return self._stable_id(raw)

    def _stable_id(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

