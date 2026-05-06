"""Retrieval-augmented generation service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from app.core.logging_config import get_logger
from app.repositories.knowledge_repository import (
    ChromaKnowledgeRepository,
    KnowledgeChunk,
    KnowledgeSearchResult,
)
from app.services.ai_service import AIProvider, AIService, ReasoningMode
from app.services.document_service import DocumentProcessingService

logger = get_logger(__name__)


@dataclass(frozen=True)
class RAGAnswer:
    """RAG response returned to routes and chat handlers."""

    answer: str
    sources: List[str]
    results: List[KnowledgeSearchResult]


class RAGService:
    """Coordinates document indexing, hybrid retrieval, and grounded answers."""

    def __init__(
        self,
        knowledge_repository: Optional[ChromaKnowledgeRepository] = None,
        document_service: Optional[DocumentProcessingService] = None,
        ai_service: Optional[AIService] = None,
    ) -> None:
        self.knowledge_repository = knowledge_repository or ChromaKnowledgeRepository()
        self.document_service = document_service or DocumentProcessingService()
        self.ai_service = ai_service or AIService()

    def index_chunks(self, chunks: Sequence[KnowledgeChunk]) -> int:
        """Index prepared chunks in ChromaDB."""
        return self.knowledge_repository.add_chunks(chunks)

    def index_pdf_bytes(
        self,
        pdf_bytes: bytes,
        source_name: str,
        user_id: int,
        workspace_id: Optional[int] = None,
        file_id: Optional[int] = None,
    ) -> int:
        """Extract and index PDF chunks.

        Args:
            pdf_bytes: Raw PDF bytes.
            source_name: Human-readable source name.
            user_id: Owner id.
            workspace_id: Optional workspace scope.
            file_id: Optional database file id.

        Returns:
            Number of chunks indexed.
        """
        chunks = self.document_service.build_pdf_chunks(
            pdf_bytes=pdf_bytes,
            source_name=source_name,
            user_id=user_id,
            workspace_id=workspace_id,
            file_id=file_id,
        )
        return self.index_chunks(chunks)

    def search(
        self,
        question: str,
        top_k: int = 5,
        user_id: int = 0,
        workspace_id: Optional[int] = None,
    ) -> List[KnowledgeSearchResult]:
        """Run hybrid search against the scoped knowledge base."""
        return self.knowledge_repository.hybrid_search(
            query=question,
            top_k=top_k,
            user_id=user_id,
            workspace_id=workspace_id,
        )

    async def answer_question(
        self,
        question: str,
        top_k: int = 5,
        user_id: int = 0,
        workspace_id: Optional[int] = None,
    ) -> RAGAnswer:
        """Answer a question using only retrieved local context."""
        results = self.search(
            question=question,
            top_k=top_k,
            user_id=user_id,
            workspace_id=workspace_id,
        )

        if not results:
            return RAGAnswer(
                answer="Not found in the selected knowledge workspace.",
                sources=[],
                results=[],
            )

        context = "\n\n".join(
            f"[{index + 1}] {result.source}\n{result.text[:1200]}"
            for index, result in enumerate(results)
        )
        prompt = (
            "Answer using only the retrieved ForgeAI notes. If the answer is not present, "
            "say exactly: Not found in notes.\n\n"
            f"Retrieved notes:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Return a direct answer and cite note numbers inline."
        )
        completion = await self.ai_service.complete(
            prompt,
            mode=ReasoningMode.SEARCH,
            provider=AIProvider.OLLAMA,
        )
        sources = list(dict.fromkeys(result.source for result in results))
        logger.info(
            "rag_answer_completed",
            extra={"source_count": len(sources), "workspace_id": workspace_id},
        )
        return RAGAnswer(answer=completion.content, sources=sources, results=results)


_default_rag_service = RAGService()


def query_kb(question: str, top_k: int = 3) -> List[tuple[float, dict]]:
    """Compatibility wrapper returning old ``(score, metadata)`` tuples."""
    results = _default_rag_service.search(question=question, top_k=top_k)
    return [
        (
            result.score,
            {
                "text": result.text,
                "source": result.source,
                **result.metadata,
            },
        )
        for result in results
    ]


def add_texts_to_index(new_text_chunks: List[dict]) -> None:
    """Compatibility wrapper for direct text indexing."""
    chunks = [
        KnowledgeChunk(
            text=str(item.get("text", "")),
            source=str(item.get("source", "manual")),
            user_id=int(item.get("user_id", 0)),
            workspace_id=item.get("workspace_id"),
            file_id=item.get("file_id"),
            chunk_index=index,
        )
        for index, item in enumerate(new_text_chunks)
    ]
    _default_rag_service.index_chunks(chunks)


def clear_kb() -> None:
    """Compatibility wrapper that clears the Chroma collection."""
    _default_rag_service.knowledge_repository.clear()

