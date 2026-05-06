"""Document extraction, summarization, and chunking services."""

from __future__ import annotations

import asyncio
import io
from dataclasses import dataclass
from typing import List, Optional

from pypdf import PdfReader

from app.core.logging_config import get_logger
from app.repositories.knowledge_repository import KnowledgeChunk
from app.services.ai_service import AIProvider, AIService, ReasoningMode

logger = get_logger(__name__)

MAX_TEXT_SIZE = 10 * 1024 * 1024
MAX_EXTRACT_PAGES = 200
MAX_SUMMARY_PAGES = 15


@dataclass(frozen=True)
class DocumentProcessingResult:
    """Processed document text and summary."""

    summary: str
    extracted_text: str
    is_processed: bool


class DocumentProcessingService:
    """Service for document extraction, chunking, and summarization."""

    def __init__(self, ai_service: Optional[AIService] = None) -> None:
        self.ai_service = ai_service or AIService()

    def split_text_to_chunks(
        self,
        text: str,
        chunk_size: int = 800,
        overlap: int = 100,
    ) -> List[str]:
        """Split text into bounded overlapping chunks.

        Args:
            text: Text to chunk.
            chunk_size: Maximum characters per chunk.
            overlap: Character overlap between adjacent chunks.

        Returns:
            List of non-empty chunks.
        """
        if not text:
            return []

        if len(text) > MAX_TEXT_SIZE:
            logger.warning(
                "document_text_truncated",
                extra={"original_length": len(text), "max_length": MAX_TEXT_SIZE},
            )
            text = text[:MAX_TEXT_SIZE]

        if len(text) <= chunk_size:
            return [text]

        chunks: List[str] = []
        start = 0
        overlap = min(overlap, chunk_size - 1)
        step = chunk_size - overlap

        while start < len(text):
            chunk = text[start : start + chunk_size].strip()
            if chunk:
                chunks.append(chunk)
            start += step

        return chunks

    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes.

        Args:
            pdf_bytes: Raw PDF file bytes.

        Returns:
            Extracted text, or an empty string when the file is unreadable.
        """
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            page_texts: List[str] = []
            for page in reader.pages[:MAX_EXTRACT_PAGES]:
                try:
                    text = page.extract_text() or ""
                except Exception:
                    continue
                if text.strip():
                    page_texts.append(text)

            extracted = "\n\n".join(page_texts)
            if len(extracted) > MAX_TEXT_SIZE:
                return extracted[:MAX_TEXT_SIZE] + "\n\n[Text truncated due to size limits.]"
            return extracted
        except Exception:
            return ""

    async def summarize_pdf(self, pdf_bytes: bytes, simple: bool = False) -> str:
        """Summarize a PDF with the tiered AI service.

        Args:
            pdf_bytes: Raw PDF bytes.
            simple: Whether to append a beginner-friendly explanation.

        Returns:
            Generated summary text.
        """
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
        except Exception as exc:
            logger.warning("pdf_open_failed", extra={"error": str(exc)})
            return "Could not extract text from this PDF. It may be scanned or unreadable."

        page_summaries: List[str] = []
        for index, page in enumerate(reader.pages[:MAX_SUMMARY_PAGES]):
            try:
                page_text = (page.extract_text() or "").strip()
            except Exception:
                continue
            if not page_text:
                continue

            prompt = (
                f"Summarize page {index + 1} in 2-3 concise bullets. "
                "Keep each bullet under 18 words.\n\n"
                f"{page_text[:2500]}"
            )
            completion = await self.ai_service.complete(
                prompt,
                mode=ReasoningMode.CHAT,
                provider=AIProvider.AUTO,
            )
            page_summaries.append(f"Page {index + 1}: {completion.content}")

        if not page_summaries:
            return "Could not extract meaningful text from this PDF."

        synthesis_prompt = (
            "Using the page notes below, produce:\n"
            "1. A five-sentence executive summary\n"
            "2. Four key ideas\n"
            "3. Two applied examples\n"
            "4. Four exam-style questions\n\n"
            f"{chr(10).join(page_summaries)[:7000]}"
        )
        final_summary = (
            await self.ai_service.complete(
                synthesis_prompt,
                mode=ReasoningMode.THINK,
                provider=AIProvider.AUTO,
            )
        ).content

        if not simple:
            return final_summary

        simple_prompt = "Rewrite this summary in beginner-friendly terms:\n\n" + final_summary
        simple_summary = (
            await self.ai_service.complete(
                simple_prompt,
                mode=ReasoningMode.CHAT,
                provider=AIProvider.AUTO,
            )
        ).content
        return f"{final_summary}\n\nSimple explanation:\n{simple_summary}"

    async def process_pdf(self, pdf_bytes: bytes, simple: bool = False) -> DocumentProcessingResult:
        """Extract text and produce a summary for a PDF."""
        extracted_text = self.extract_text_from_pdf_bytes(pdf_bytes)
        summary = await self.summarize_pdf(pdf_bytes, simple=simple)
        return DocumentProcessingResult(
            summary=summary,
            extracted_text=extracted_text,
            is_processed=bool(extracted_text or summary),
        )

    def process_pdf_sync(self, pdf_bytes: bytes, simple: bool = False) -> DocumentProcessingResult:
        """Synchronous bridge for Celery workers."""
        return asyncio.run(self.process_pdf(pdf_bytes, simple=simple))

    def build_pdf_chunks(
        self,
        pdf_bytes: bytes,
        source_name: str,
        user_id: int,
        workspace_id: Optional[int] = None,
        file_id: Optional[int] = None,
    ) -> List[KnowledgeChunk]:
        """Extract and chunk a PDF for vector indexing."""
        reader = PdfReader(io.BytesIO(pdf_bytes))
        chunks: List[KnowledgeChunk] = []

        for page_index, page in enumerate(reader.pages[:MAX_EXTRACT_PAGES]):
            try:
                text = (page.extract_text() or "").strip()
            except Exception:
                continue
            if not text:
                continue

            page_chunks = self.split_text_to_chunks(text[:12000], chunk_size=900, overlap=140)
            for chunk_index, chunk_text in enumerate(page_chunks):
                chunks.append(
                    KnowledgeChunk(
                        text=chunk_text,
                        source=f"{source_name} | page {page_index + 1}, chunk {chunk_index + 1}",
                        user_id=user_id,
                        workspace_id=workspace_id,
                        file_id=file_id,
                        page_number=page_index + 1,
                        chunk_index=len(chunks),
                    )
                )

        return chunks

