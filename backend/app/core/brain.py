"""Legacy AI brain facade.

New code should use ``app.services.ai_service``, ``app.services.document_service``,
and ``app.services.rag_service`` directly. These wrappers keep older imports and
tests stable while the application follows a service/repository architecture.
"""

from __future__ import annotations

import asyncio
from typing import Any, List, Optional

from app.services.ai_service import AIProvider, AIService
from app.services.document_service import DocumentProcessingService
from app.services.rag_service import RAGService, add_texts_to_index, clear_kb, query_kb


def _run_sync(coro: Any) -> Any:
    """Run an async coroutine from a synchronous legacy boundary."""
    return asyncio.run(coro)


def ask_brain(prompt: str) -> str:
    """Return an AI answer using the hybrid provider stack."""
    completion = _run_sync(AIService().complete(prompt=prompt, provider=AIProvider.AUTO))
    return completion.content


def split_text_to_chunks(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks."""
    return DocumentProcessingService().split_text_to_chunks(
        text,
        chunk_size=chunk_size,
        overlap=overlap,
    )


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract text from PDF bytes."""
    return DocumentProcessingService().extract_text_from_pdf_bytes(pdf_bytes)


def summarize_pdf(pdf_bytes: bytes, simple: bool = False) -> str:
    """Summarize a PDF using the document service."""
    return DocumentProcessingService().process_pdf_sync(pdf_bytes, simple=simple).summary


def index_pdf_bytes_to_kb(
    pdf_bytes: bytes,
    source_name: str = "uploaded",
    user_id: int = 0,
    workspace_id: Optional[int] = None,
    file_id: Optional[int] = None,
) -> int:
    """Index a PDF into ChromaDB-backed knowledge storage."""
    return RAGService().index_pdf_bytes(
        pdf_bytes=pdf_bytes,
        source_name=source_name,
        user_id=user_id,
        workspace_id=workspace_id,
        file_id=file_id,
    )


def ask_with_context(question: str, top_k: int = 3) -> str:
    """Answer a question using retrieved context."""
    answer = _run_sync(RAGService().answer_question(question=question, top_k=top_k))
    if not answer.sources:
        return f"{answer.answer}\n\n(Sources: none)"
    return f"{answer.answer}\n\nSources used: {', '.join(answer.sources)}"
